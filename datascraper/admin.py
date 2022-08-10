from django.contrib import admin
from django.utils.html import format_html

from .models import (
    Location,
    WeatherParameter,
    ForecastSource,
    ForecastTemplate,
    ArchiveSource,
    ArchiveTemplate,
    Forecast,
    )

from backports import zoneinfo
from django.utils import timezone
from .forecasts import DATETIME_STEP

#############
# LOCATIONS #
#############


class ForecastTemplateInline(admin.TabularInline):

    model = ForecastTemplate
    extra = 0

    fields = ("forecast_source", 'source_url', "location_relative_url")
    readonly_fields = ('source_url',)

    def source_url(self, obj):

        url = obj.forecast_source.url
        color = obj.forecast_source.chart_color

        return format_html('<a href="{}" target="_blank" \
                           style="color: {};">{}</a>', url, color, url)


class ArchiveTemplateInline(admin.TabularInline):

    model = ArchiveTemplate
    extra = 0

    fields = ("archive_source", 'source_url', "location_relative_url")
    readonly_fields = ('source_url',)

    def source_url(self, obj):

        url = obj.archive_source.url
        color = obj.archive_source.chart_color

        return format_html('<a href="{}" target="_blank" \
                           style="color: {};">{}</a>', url, color, url)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):

    inlines = [
        ForecastTemplateInline,
        ArchiveTemplateInline,
        ]

    list_display = ['name', 'region', 'country', 'timezone']

    list_filter = ["country"]

    search_fields = ["name"]


####################
# FORECAST SOURCES #
####################

@admin.register(ForecastSource)
class ForecastSourceAdmin(admin.ModelAdmin):

    list_display = ['name', 'id', 'url', 'chart_color']


###################
# ARCHIVE SOURCES #
###################

@admin.register(ArchiveSource)
class ArchiveSourceAdmin(admin.ModelAdmin):

    list_display = ['name', 'id', 'url', 'chart_color']


######################
# WEATHER PARAMETERS #
######################

@admin.register(WeatherParameter)
class WeatherParameterAdmin(admin.ModelAdmin):

    list_display = ['name', 'id', 'var_name', 'tooltip', 'meas_unit']

    def has_delete_permission(self, request, obj=None):
        return False


######################
# FORECAST TEMPLATES #
######################

class ForecastInline(admin.TabularInline):

    model = Forecast
    extra = 0

    fields = ("forecast_data",)
    readonly_fields = ("forecast_data",)

    ordering = ("-start_forecast_datetime",)

    @admin.display(description=format_html(""))
    def forecast_data(self, obj):

        data_json = obj.data_json

        datetime_col = []
        datetime_ = timezone.localtime(
            value=obj.start_forecast_datetime,
            timezone=zoneinfo.ZoneInfo(obj.forecast_template.location.timezone)
            )

        for i in data_json[0]:
            datetime_col.append(datetime_)
            datetime_ += DATETIME_STEP

        data_json.insert(0, datetime_col)

        # <caption>Таблица размеров обуви</caption>
        scraped_datetime = timezone.localtime(
            value=obj.scraped_datetime,
            timezone=zoneinfo.ZoneInfo(obj.forecast_template.location.timezone)
            ).strftime("%Y-%m-%d %H:%M:%S %Z")

        caption = f'<caption style="background:#265d2b">\
            <b>SCRAPED: {scraped_datetime}</b>\
            </caption>'

        thead = [f'{i.name}, {i.meas_unit}'
                 for i in WeatherParameter.objects.all()]
        thead.insert(0, 'Datetime UTC')
        thead = ''.join([f'<th style="padding:3px">{str(j)}</th>'
                         for j in thead])
        thead = f'<thead><tr>{thead}</tr></thead>'

        table = list(zip(*data_json))

        tbody = [''.join([f'<td style="padding:3px">{str(j)}</td>'
                          for j in i]) for i in table]
        tbody = ''.join([f'<tr>{i}</tr>' for i in tbody])
        tbody = f'<tbody>{tbody}</tbody>'

        table = caption + thead + tbody

        table = f'<table>{table}</table>'

        return format_html(table)


@admin.register(ForecastTemplate)
class ForecastTemplateAdmin(admin.ModelAdmin):

    list_display = ('forecast_source', 'location')
    readonly_fields = ('forecast_source', 'location')
    fields = ('forecast_source', 'location')

    list_filter = ('forecast_source', 'location')

    inlines = [ForecastInline, ]

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False
