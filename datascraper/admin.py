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
    Archive,
    )

from backports import zoneinfo
from django.utils import timezone
# from .forecasts import DATETIME_STEP
from django_admin_inline_paginator.admin import TabularInlinePaginated

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

    list_display = ['name', 'id', 'url', 'chart_color_']

    def chart_color_(self, obj):

        color = obj.chart_color

        return format_html('<b style="color: {};">{}</a>', color, color)


###################
# ARCHIVE SOURCES #
###################

@admin.register(ArchiveSource)
class ArchiveSourceAdmin(admin.ModelAdmin):

    list_display = ['name', 'id', 'url', 'chart_color_']

    def chart_color_(self, obj):

        color = obj.chart_color

        return format_html('<b style="color: {};">{}</a>', color, color)


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

class ForecastInline(TabularInlinePaginated):

    model = Forecast
    extra = 0
    per_page = 5

    verbose_name = 'forecast record'

    fields = ("forecast_data",)
    readonly_fields = ("forecast_data",)

    ordering = ("-scraped_datetime",)

    @admin.display(description=format_html(""))
    def forecast_data(self, obj):

        data_json = obj.data_json

        datetime_col = []
        datetime_ = timezone.localtime(
            value=obj.forecast_datetime,
            timezone=zoneinfo.ZoneInfo(obj.forecast_template.location.timezone)
            )

        for i in data_json[0]:
            datetime_col.append(datetime_)
            # datetime_ += DATETIME_STEP

        data_json.insert(0, datetime_col)

        scraped_datetime = timezone.localtime(
            value=obj.scraped_datetime,
            timezone=zoneinfo.ZoneInfo(obj.forecast_template.location.timezone)
            ).strftime("%Y-%m-%d %H:%M:%S %Z")

        caption = f'<caption style="background:#265d2b">\
            <b>SCRAPED: {scraped_datetime}</b>\
            </caption>'

        thead = [f'{i.name}, {i.meas_unit}'
                 for i in WeatherParameter.objects.all()]
        thead.insert(0, 'Local Datetime')
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

    list_display = ('forecast_source', 'location', 'view_on_source_site')
    readonly_fields = ('forecast_source', 'location', 'view_on_source_site')
    fields = ('forecast_source', 'location', 'view_on_source_site')

    list_filter = ('forecast_source', 'location')

    list_per_page = 15

    def view_on_source_site(self, obj):

        url = obj.forecast_source.url + obj.location_relative_url
        color = obj.forecast_source.chart_color

        return format_html('<a href="{}" target="_blank" \
                           style="color: {};">{}</a>', url, color, url)

    inlines = [ForecastInline, ]

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False


#####################
# ARCHIVE TEMPLATES #
#####################

class ArchiveInline(TabularInlinePaginated):

    model = Archive
    extra = 0

    fields = ("local_datetime", "data_json_")
    readonly_fields = ("local_datetime", "data_json_")

    verbose_name = 'archive record'

    per_page = 20

    ordering = ("-record_datetime",)

    def local_datetime(self, obj):

        local_datetime = timezone.localtime(
            value=obj.record_datetime,
            timezone=zoneinfo.ZoneInfo(obj.archive_template.location.timezone)
            ).strftime("%Y-%m-%d %H:%M:%S %Z")

        return local_datetime

    data_json_name = [
        f'{i.name}, {i.meas_unit}' for i in WeatherParameter.objects.all()]
    data_json_name = ''.join([f'<th>{str(j)}</th>'for j in data_json_name])

    @admin.display(description=format_html(data_json_name))
    def data_json_(self, obj):

        data_json = ''.join([f'<td>{i}</td>' for i in obj.data_json])

        return format_html(data_json)


@admin.register(ArchiveTemplate)
class ArchiveTemplateAdmin(admin.ModelAdmin):

    list_display = ('archive_source', 'location', 'view_on_source_site')
    readonly_fields = ('archive_source', 'location', 'view_on_source_site')
    fields = ('archive_source', 'location', 'view_on_source_site')

    list_filter = ('archive_source', 'location')

    name = 'archive record'

    def view_on_source_site(self, obj):

        url = obj.archive_source.url + obj.location_relative_url
        color = obj.archive_source.chart_color

        return format_html('<a href="{}" target="_blank" \
                           style="color: {};">{}</a>', url, color, url)

    inlines = [ArchiveInline, ]

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False
