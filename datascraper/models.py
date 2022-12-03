from django.db import models
from datetime import datetime, timedelta
from django.utils import timezone
from datascraper import forecasts, archive
from backports import zoneinfo
import collections
from datascraper.logging import init_logger
from datascraper.forecasts import get_soup
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

##############
# VALIDATORS #
##############


alpha = RegexValidator(r'^[a-zA-Z]*$', 'Only roman characters are allowed.')


def validate_first_upper(value):
    if value[0].islower():
        raise ValidationError(
            "First letter must be uppercase.",
            params={"value": value},
        )

########
# MISC #
########


class TimeZone(models.Model):
    name = models.CharField(max_length=50)

    @classmethod
    def scrap_zones(cls):
        logger = init_logger('TimeZone scraper')

        try:
            tzones = get_soup(
                'https://en.wikipedia.org/wiki/List_of_tz_database_time_zones')
            tzones = tzones.tbody.find_all('tr')[2:]
            tzones = (tz.td.find_next_sibling().get_text().strip() for tz in
                      tzones)

        except Exception as e:
            logger.critical(f'FAILED to scrap TimeZones: {e}')
            exit()

        cls.objects.all().delete()
        for tz in tzones:
            cls.objects.create(name=tz)

        logger.debug('Timezones successfully scraped from Wikipedia.')

    @classmethod
    def zones_list(cls):
        return [(tz.name, tz.name) for tz in cls.objects.all()]


class Location(models.Model):
    name = models.CharField(
        max_length=30, validators=[alpha, validate_first_upper])
    region = models.CharField(
        max_length=30, validators=[alpha, validate_first_upper])
    country = models.CharField(
        max_length=30, validators=[alpha, validate_first_upper])
    timezone = models.CharField(
        max_length=40, default='Europe/Moscow', choices=TimeZone.zones_list())
    is_active = models.BooleanField(default=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        unique_together = ('name', 'region', 'country')

    # Getting local datetime at location
    def local_datetime(self):
        return timezone.localtime(timezone=zoneinfo.ZoneInfo(self.timezone))
    
    # Calculating start forecast datetime
    def start_forecast_datetime(self):
        # Calculating start forecast datetime
        # Forecasts step is 1 hour
        return self.local_datetime().replace(
            minute=0, second=0, microsecond=0) + timedelta(hours=1)

    @classmethod
    def locations_list(cls):
        return tuple(map(str, cls.objects.filter(is_active=True)))

    def __str__(self):
        return f'{self.name}, {self.region}, {self.country}'


class WeatherParameter(models.Model):
    id = models.IntegerField(primary_key=True)
    var_name = models.CharField(max_length=10)
    name = models.CharField(max_length=30)
    tooltip = models.CharField(max_length=30)
    meas_unit = models.CharField(max_length=30)

    def __str__(self):
        return self.var_name

###################
# FORECAST MODELS #
###################


class ForecastSource(models.Model):
    id = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=30)
    url = models.CharField(max_length=200)
    chart_color = models.CharField(max_length=10)

    def __str__(self):
        return self.name

    @classmethod
    def dropdown_list(cls):
        return ((source.name, source.url) for source in cls.objects.all())


class ForecastTemplate(models.Model):
    forecast_source = models.ForeignKey(
        ForecastSource, on_delete=models.PROTECT)
    location = models.ForeignKey(Location, on_delete=models.PROTECT)
    url = models.CharField(
        max_length=500,
        unique=True)
    last_scraped = models.DateTimeField(default=datetime.fromtimestamp(0))
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['location', 'forecast_source']
        unique_together = ('forecast_source', 'location')

    def __str__(self):
        return f"{self.forecast_source} --> {self.location}"

    @classmethod
    def scrap_forecasts(cls, forecast_source_id=False):

        logger = init_logger('Forecast scraper')
        logger.info("START")

        if not forecast_source_id:
            templates = cls.objects.all()
        else:
            try:
                ForecastSource.objects.get(id=forecast_source_id)
                templates = cls.objects.filter(
                    forecast_source_id=forecast_source_id)
            except ForecastSource.DoesNotExist as e:
                logger.error(e)
                exit()

        for template in templates:

            logger.debug(template)

            local_datetime = template.location.local_datetime()
            logger.debug(f'LDT: {local_datetime}')

            start_forecast_datetime = template.location.start_forecast_datetime()
            logger.debug(f'SFDT: {start_forecast_datetime}')

            # Getting json_data from calling source scraper function
            scraper_func = getattr(forecasts, template.forecast_source.id)
            try:
                scraped_forecasts = scraper_func(
                    start_forecast_datetime, template.url)
                template.last_scraped = local_datetime
                template.save()

            except Exception as e:

                logger.error(f"{template}: {e}")
                continue

            logger.debug("Scraped forecasts: \n"+'\n'.join([
                f'{f[0].isoformat()}, {f[1]}' for f in scraped_forecasts]))

            for forecast in scraped_forecasts:

                prediction_range_hours = int(
                    (forecast[0] - local_datetime.replace(
                        minute=0, second=0, microsecond=0))/timedelta(hours=1))

                Forecast.objects.update_or_create(
                    forecast_template=template,
                    forecast_datetime=forecast[0],
                    forecast_data=forecast[1],
                    prediction_range_hours=prediction_range_hours,
                    # defaults={'scraped_datetime': timezone.now()})
                    defaults={'scraped_datetime': local_datetime})

        # Closing Selenium driver
        if forecasts.driver:
            forecasts.driver.close()
            forecasts.driver.quit()

        # Checking for expired forecasts
        # whose data is more than an hour out of date
        exp_report = []
        for template in cls.objects.all():

            def exp_report_append(): exp_report.append(
                        template.forecast_source)

            try:

                last_forecast = Forecast.objects.filter(
                    forecast_template=template).latest('scraped_datetime')

                if not last_forecast.is_actual():
                    exp_report_append()

            except Forecast.DoesNotExist:
                exp_report_append()

        if exp_report:
            exp_report = [
                ((i[0].name+':').ljust(15),
                 i[1],
                 ForecastTemplate.objects.filter(forecast_source=i[0]).count())
                for i in collections.Counter(exp_report).items()]
            exp_report = '\n'.join(
                [f"{i[0]} {i[1]}/{i[2]} locs" for i in exp_report])
            exp_report = f"OUTDATED data detected:\n{exp_report}"

            logger.critical(exp_report)

        logger.info("END")


class Forecast(models.Model):
    forecast_template = models.ForeignKey(
        ForecastTemplate, on_delete=models.PROTECT)
    scraped_datetime = models.DateTimeField()
    forecast_datetime = models.DateTimeField()
    prediction_range_hours = models.IntegerField()
    forecast_data = models.JSONField()

    class Meta:
        indexes = [
            models.Index(fields=["scraped_datetime", "forecast_template"]),
            models.Index(fields=["forecast_template",
                                 "prediction_range_hours",
                                 "forecast_datetime"]),
        ]

    def is_actual(self):
        exp_datetime = timezone.make_naive(
            # self.scraped_datetime) + timedelta(minutes=10)
            self.scraped_datetime) + timedelta(hours=1)
        return datetime.now() < exp_datetime

    def __str__(self):
        return f"{self.forecast_template.forecast_source} --> \
            {self.forecast_template.location}"


##################
# ARCHIVE MODELS #
##################


class ArchiveSource(models.Model):
    id = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=30)
    url = models.CharField(max_length=200, unique=True)
    chart_color = models.CharField(max_length=10)

    def __str__(self):
        return self.name


class ArchiveTemplate(models.Model):
    archive_source = models.ForeignKey(
        ArchiveSource, on_delete=models.PROTECT)
    location = models.ForeignKey(Location, on_delete=models.PROTECT)
    url = models.CharField(
        max_length=200,
        unique=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['location', 'archive_source']
        unique_together = ('archive_source', 'location')

    def __str__(self):
        return f"{self.archive_source} --> {self.location}"

    @classmethod
    def scrap_archives(cls):

        logger = init_logger('Archive scraper')
        logger.info("START")

        templates = cls.objects.all()

        for template in templates:
            logger.debug(template)

            # Getting local datetime at archive location
            timezone_info = zoneinfo.ZoneInfo(template.location.timezone)
            local_datetime = timezone.localtime(timezone=timezone_info)

            # Calculating start archive datetime
            start_archive_datetime = local_datetime.replace(
                minute=0, second=0, microsecond=0)

            # # Full pass to archive source
            # archive_url = template.archive_source.url + \
            #     template.location_relative_url

            try:
                last_record_datetime = Archive.objects.filter(
                    archive_template__id=template.id).latest(
                    'record_datetime').record_datetime.replace(
                    tzinfo=timezone_info)
            except Archive.DoesNotExist:
                last_record_datetime = None

            try:
                archive_data = archive.arch_rp5(
                    start_archive_datetime, template.url, last_record_datetime)
            except Exception as _ex:

                logger.error(f"{template}: {_ex}")

                continue

            for record in archive_data:

                Archive.objects.get_or_create(
                    archive_template=template,
                    record_datetime=record[0],
                    data_json=record[1],
                    defaults={'scraped_datetime': timezone.now()})
        logger.info("END")


class Archive(models.Model):
    archive_template = models.ForeignKey(
        ArchiveTemplate, on_delete=models.PROTECT)
    scraped_datetime = models.DateTimeField()
    record_datetime = models.DateTimeField(default=None)
    data_json = models.JSONField()

    class Meta:
        ordering = ['archive_template', 'record_datetime']
        # index_together = ['archive_template', 'record_datetime']
        indexes = [
            models.Index(fields=["archive_template", "record_datetime"]),
        ]

    def __str__(self):
        return ""
