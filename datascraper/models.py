from django.db import models
from datetime import datetime


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


#############
# FORECASTS #
#############

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


class Forecast(models.Model):
    location = models.ForeignKey(Location, on_delete=models.PROTECT)
    forecast_source = models.ForeignKey(
        ForecastSource, on_delete=models.PROTECT)
    scraped_datetime = models.DateTimeField(default=datetime.now())
    start_forecast_datetime = models.DateTimeField()
    data_json = models.JSONField()

    def __str__(self):
        return f"{self.forecast_source.name} >> {self.location.name} >> \
                Scraped: {self.scraped_datetime.isoformat()} >> \
                Start: {self.start_forecast_datetime.isoformat()}"


############
# ARCHIVES #
############

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
    location = models.ForeignKey(Location, on_delete=models.PROTECT)
    archive_source = models.ForeignKey(
        ArchiveSource, on_delete=models.PROTECT)
    scraped_datetime = models.DateTimeField(default=datetime.now())
    data_json = models.JSONField()

    def __str__(self):
        return f"{self.archive_source.name} >> {self.location.name} >> \
                Scraped: {self.scraped_datetime.isoformat()}"