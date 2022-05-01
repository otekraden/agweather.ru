from django.contrib import admin

from .models import Location, WeatherPrameter, ForecastSource, \
    ForecastTemplate, ArchiveSource, ArchiveTemplate

admin.site.register(Location)
admin.site.register(WeatherPrameter)
admin.site.register(ForecastSource)
admin.site.register(ForecastTemplate)
admin.site.register(ArchiveSource)
admin.site.register(ArchiveTemplate)
