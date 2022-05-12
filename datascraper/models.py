from django.db import models
from datetime import datetime, timedelta
from django.utils import timezone
from datascraper import forecasts
from backports import zoneinfo

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


class WeatherPrameter(models.Model):
    param_key = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=30)
    tooltip = models.CharField(max_length=30)
    meas_unit = models.CharField(max_length=30)

    def __str__(self):
        return self.param_key


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
    def scrap_all_forecasts(cls):

        for template in cls.objects.all():

            # Getting local datetime at forecast location
            timezone_info = zoneinfo.ZoneInfo(template.location.timezone)
            local_datetime = timezone.localtime(timezone=timezone_info)

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

            # Full pass to forecast source
            forecast_url = template.forecast_source.url + \
                template.location_relative_url

            # Getting json_data from calling source scraper function
            scraper_func = getattr(forecasts, template.forecast_source.id)
            try:
                forecast_data_json = scraper_func(
                    start_forecast_datetime, forecast_url)
            except Exception as _ex:
                print(f"Failed to scrap data for {template}:")
                print(_ex)
                continue

            print(template)
            for i in forecast_data_json:
                print(i)

            Forecast.objects.get_or_create(
                forecast_template=template,
                start_forecast_datetime=start_forecast_datetime,
                data_json=forecast_data_json,
                defaults={'scraped_datetime': timezone.now()})


class Forecast(models.Model):
    forecast_template = models.ForeignKey(
        ForecastTemplate, on_delete=models.PROTECT)
    scraped_datetime = models.DateTimeField()
    start_forecast_datetime = models.DateTimeField()
    data_json = models.JSONField()

    def __str__(self):
        return f"{self.forecast_template.forecast_source.name} >> \
                {self.forecast_template.location.name} >> \
                Scraped: {self.scraped_datetime.isoformat()} >> \
                Start: {self.start_forecast_datetime.isoformat()}"


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


class Archive(models.Model):
    archive_template = models.ForeignKey(
        ArchiveTemplate, on_delete=models.PROTECT)
    scraped_datetime = models.DateTimeField(default=datetime.now())
    data_json = models.JSONField()

    def __str__(self):
        return f"{self.archive_source.name} >> {self.location.name} >> \
                Scraped: {self.scraped_datetime.isoformat()}"
