from django.db import models
from datetime import datetime, timedelta
from django.utils import timezone
from datascraper import forecasts, archive
from backports import zoneinfo
import collections

########
# MISC #
########


class Location(models.Model):
    name = models.CharField(max_length=30)
    region = models.CharField(max_length=30)
    country = models.CharField(max_length=30)
    timezone = models.CharField(max_length=40, default='UTC')

    class Meta:
        unique_together = ('name', 'region', 'country')

    def __str__(self):
        return self.name


class WeatherParameter(models.Model):
    id = models.IntegerField(primary_key=True)
    var_name = models.CharField(max_length=10)
    name = models.CharField(max_length=30)
    tooltip = models.CharField(max_length=30)
    meas_unit = models.CharField(max_length=30)

    def __str__(self):
        return self.var_name

####################
# FORECASTS MODELS #
####################


class ForecastSource(models.Model):
    id = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=30)
    url = models.CharField(max_length=200)
    chart_color = models.CharField(max_length=10)

    def __str__(self):
        return self.name


class ForecastTemplate(models.Model):
    forecast_source = models.ForeignKey(
        ForecastSource, on_delete=models.PROTECT)
    location = models.ForeignKey(Location, on_delete=models.PROTECT)
    location_relative_url = models.CharField(max_length=100)

    class Meta:
        ordering = ['location', 'forecast_source']

    def __str__(self):
        return f"{self.location} >> {self.forecast_source}"

    @classmethod
    def scrap_forecasts(cls, logger, forecast_source_id=None):

        if forecast_source_id:
            templates = cls.objects.filter(
                forecast_source_id=forecast_source_id)
        else:
            templates = cls.objects.all()

        for template in templates:
            # print(f"Scraping forecast: {template}")
            logger.debug(template)

            # Getting local datetime at forecast location
            timezone_info = zoneinfo.ZoneInfo(template.location.timezone)
            local_datetime = timezone.localtime(timezone=timezone_info)

            # Calculating start forecast datetime
            start_forecast_datetime = ForecastTemplate.start_forecast_datetime(
                timezone_info, local_datetime)

            logger.debug(start_forecast_datetime)

            # Full pass to forecast source
            forecast_url = template.forecast_source.url + \
                template.location_relative_url

            # Getting json_data from calling source scraper function
            scraper_func = getattr(forecasts, template.forecast_source.id)
            try:
                forecast_data_json = scraper_func(
                    start_forecast_datetime, forecast_url)
            except Exception as _ex:

                logger.error(f"{template}: {_ex}")
                continue

            logger.debug("Scraped data >\n"+'\n'.join([
                str(d) for d in forecast_data_json]))

            Forecast.objects.update_or_create(
                forecast_template=template,
                start_forecast_datetime=start_forecast_datetime,
                data_json=forecast_data_json,
                defaults={'scraped_datetime': timezone.now()})
        
        # Closing Selenium driver
        forecasts.driver.close()
        forecasts.driver.quit()

    @classmethod
    def get_outdated_report(cls):
        # Getting a report on forecast sources
        # whose data is more than an hour out of date
        report = []
        for template in cls.objects.all():

            last_record = Forecast.objects.filter(
                forecast_template=template).latest('scraped_datetime')

            if timezone.make_naive(last_record.scraped_datetime) + \
                    timedelta(hours=1) < datetime.now():

                report.append(
                    last_record.forecast_template.forecast_source)

        if report:
            report = [
                ((i[0].name+':').ljust(15),
                 i[1],
                 ForecastTemplate.objects.filter(forecast_source=i[0]).count())
                for i in collections.Counter(report).items()]
            report = '\n'.join([f"{i[0]} {i[1]}/{i[2]} locs" for i in report])

            return report

    @staticmethod
    def start_forecast_datetime(timezone_info: zoneinfo,
                                local_datetime: datetime):
        # Calculating start forecast datetime
        # Local start time can be only 3:00, 9:00, 15:00 or 21:00:
        # night, morning, afternoon, evening.
        # Forecasts step is 6 hours
        start_forecast_datetime = local_datetime.replace(
            minute=0, second=0, microsecond=0)
        start_hour = (((start_forecast_datetime.hour-3)//6+1)*6+3)
        if start_hour == 27:
            start_forecast_datetime = start_forecast_datetime.replace(
                hour=3)
            start_forecast_datetime += timedelta(days=1)
        else:
            start_forecast_datetime = start_forecast_datetime.replace(
                hour=start_hour)
        return start_forecast_datetime


class Forecast(models.Model):
    forecast_template = models.ForeignKey(
        ForecastTemplate, on_delete=models.PROTECT)
    scraped_datetime = models.DateTimeField()
    start_forecast_datetime = models.DateTimeField()
    data_json = models.JSONField()

    def __str__(self):
        return "{0} >> {1}\nScraped: {2}\nStart: {3}".format(
            self.forecast_template.forecast_source.name,
            self.forecast_template.location.name,
            self.scraped_datetime.isoformat(),
            self.start_forecast_datetime.isoformat())


###################
# ARCHIVES MODELS #
###################

class ArchiveSource(models.Model):
    id = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=30)
    url = models.CharField(max_length=200)
    chart_color = models.CharField(max_length=10)

    def __str__(self):
        return self.name


class ArchiveTemplate(models.Model):
    archive_source = models.ForeignKey(
        ArchiveSource, on_delete=models.PROTECT)
    location = models.ForeignKey(Location, on_delete=models.PROTECT)
    location_relative_url = models.CharField(max_length=100)

    class Meta:
        ordering = ['location', 'archive_source']

    def __str__(self):
        return f"{self.location} >> {self.archive_source}"

    @classmethod
    def scrap_archive(cls, logger):
        templates = cls.objects.all()

        for template in templates:
            # print(f"Scraping archive: {template}")
            logger.debug(template)

            # Getting local datetime at archive location
            timezone_info = zoneinfo.ZoneInfo(template.location.timezone)
            local_datetime = timezone.localtime(timezone=timezone_info)

            # Calculating start archive datetime
            start_archive_datetime = ForecastTemplate.start_forecast_datetime(
                timezone_info, local_datetime) - timedelta(hours=6)

            # Full pass to archive source
            archive_url = template.archive_source.url + \
                template.location_relative_url

            try:
                last_record_datetime = Archive.objects.filter(
                    archive_template__id=template.id).latest(
                    'record_datetime').record_datetime.replace(
                    tzinfo=timezone_info)
            except Archive.DoesNotExist:
                last_record_datetime = None

            try:
                archive_data = archive.arch_rp5(
                    start_archive_datetime, archive_url, last_record_datetime)
            except Exception as _ex:

                logger.error(f"{template}: {_ex}")

                continue

            for record in archive_data:

                Archive.objects.get_or_create(
                    archive_template=template,
                    record_datetime=record[0],
                    data_json=record[1],
                    defaults={'scraped_datetime': timezone.now()})


class Archive(models.Model):
    archive_template = models.ForeignKey(
        ArchiveTemplate, on_delete=models.PROTECT)
    scraped_datetime = models.DateTimeField(default=datetime.now())
    record_datetime = models.DateTimeField(default=None)
    data_json = models.JSONField()

    class Meta:
        ordering = ['archive_template', 'record_datetime']
        # unique_together = ['archive_template', 'record_datetime']
        index_together = ['archive_template', 'record_datetime']

    def __str__(self):
        return f"{self.archive_template.archive_source.name} >> \
            {self.archive_template.location.name} >> \
            Scraped: {self.scraped_datetime.isoformat()}"
