from django.shortcuts import render
# from django.http import HttpResponseRedirect
# from .forms import FeedbackForm
# from .models import Feedback
from datascraper.models import (
    WeatherParameter, Location, ForecastTemplate, Forecast, ForecastSource,
    ArchiveTemplate, Archive)
# from datascraper.forecasts import DATETIME_STEP
from backports import zoneinfo
from django.utils import timezone
from datetime import timedelta


WEATHER_PARAMETERS = [par.name for par in WeatherParameter.objects.all()]
LOCATIONS = [f'{loc.name}, {loc.region}, {loc.country}'
             for loc in Location.objects.all()]
FORECAST_SOURCES_URLS = [source.url for source in ForecastSource.objects.all()]
FORECAST_SOURCES_NAMES = [
    source.name for source in ForecastSource.objects.all()]


def forecast(request):

    if request.method == 'GET':
        # Default location Saint-Petersburg
        location = LOCATIONS[0]
        # Default show Temperature
        weather_parameter = WEATHER_PARAMETERS[0]
        # Default one week
        forecast_length = 7

    elif request.method == 'POST':
        location = request.POST.get('location')
        weather_parameter = request.POST.get('weather_parameter')
        forecast_length = request.POST.get('forecast_length')

    forecast_length = 7 if forecast_length == '' else int(forecast_length)
    if forecast_length > 14:
        forecast_length = 14
    elif forecast_length < 1:
        forecast_length = 1
    forecast_length_steps = forecast_length*4

    weather_parameter_index = WEATHER_PARAMETERS.index(weather_parameter)

    location_object = location_object_from_input(location)

    forecast_templates = ForecastTemplate.objects.filter(
        location=location_object)


    # Getting local datetime at forecast location
    timezone_info = zoneinfo.ZoneInfo(location_object.timezone)
    local_datetime = timezone.localtime(timezone=timezone_info)

    # Calculating start forecast datetime
    start_forecast_datetime = ForecastTemplate.start_forecast_datetime(
        local_datetime)

    # Generating datetime row
    datetime_row, datetime_ = [], start_forecast_datetime
    for step in range(forecast_length_steps):
        datetime_row.append(datetime_)
        datetime_ += DATETIME_STEP

    # Tooltip titles
    tooltip_titles = [dt.strftime("%d.%m %H:%M") for dt in datetime_row]
    tooltip_titles = insert_empty_steps(tooltip_titles, '')

    # Making datasets for Chartjs
    datasets = []
    for template in forecast_templates:
        forecast = Forecast.objects.filter(
            forecast_template=template).latest('scraped_datetime')
        if forecast.is_actual():
            start_forecast_datetime_from_db = forecast.start_forecast_datetime
            forecast_data = forecast.data_json[weather_parameter_index]

            # Data correction
            while datetime_row[0] != start_forecast_datetime_from_db:
                if datetime_row[0] > start_forecast_datetime_from_db:
                    start_forecast_datetime_from_db += DATETIME_STEP
                    del forecast_data[0]
                elif datetime_row[0] < start_forecast_datetime_from_db:
                    start_forecast_datetime_from_db -= DATETIME_STEP
                    forecast_data.insert(0, None)

            forecast_data = insert_empty_steps(forecast_data[
                    :forecast_length_steps], 'none')

            datasets.append({
                'label': template.forecast_source.name,
                'data': forecast_data,
                'borderColor': template.forecast_source.chart_color,
                'backgroundColor': template.forecast_source.chart_color,
            })

    # For X axe in Chartjs
    labels = [dt.strftime("%a")
              if dt.hour == 9
              else ''
              for dt in datetime_row]
    labels = insert_empty_steps(labels, '')
    for index in range(len(labels)):
        if tooltip_titles[index][-5:] == '21:00':
            labels[index+1] = " "
        elif tooltip_titles[index][-5:] == '09:00':
            labels[index+1] = labels[index]
            labels[index] = ""

    chartjs_data = {
        'labels': labels,
        'datasets': datasets,
    }

    last_database_refresh = Forecast.objects.latest(
        'scraped_datetime').scraped_datetime.strftime(
            "Database updated:  %d.%m.%Y %H:%M UTC")

    scales_list = ((-5, 5), (755, 765), (0, 10))
    chartjs_options = {'suggestedMin': scales_list[weather_parameter_index][0],
                       'suggestedMax': scales_list[weather_parameter_index][1],
                       'tooltip_titles': tooltip_titles,
                       'last_database_refresh': last_database_refresh,
                       }

    context = {
        'locations': LOCATIONS,
        'location': location,
        'weather_parameters': WEATHER_PARAMETERS,
        'weather_parameter': weather_parameter,
        'forecast_length': forecast_length,
        'chartjs_options': chartjs_options,
        'chartjs_data': chartjs_data,
        'forecast_sources': zip(FORECAST_SOURCES_NAMES, FORECAST_SOURCES_URLS),
        }
    # from pprint import pprint
    # pprint(chartjs_data)

    return render(
        request=request,
        template_name='website/forecast.html',
        context=context)

def archive(request):
    """View"""
    if request.method == 'GET':

        # Default location Saint-Petersburg
        location = LOCATIONS[0]
        # Default show Temperature
        weather_parameter = WEATHER_PARAMETERS[0]
        # Default two week
        archive_length = 7

        # weather_parameter = weather_parameters[0]
        # archive_length = 14  # длина архива по умолчанию дней
        # forecasts_foresight = 1

    elif request.method == 'POST':
        location = request.POST.get('location')
        weather_parameter = request.POST.get('weather_parameter')
        archive_length = request.POST.get('archive_length')
        # forecasts_foresight = request.POST.get('forecasts-foresight')

    archive_length = 14 if archive_length == '' else int(archive_length)
    if archive_length > 30:
        archive_length = 30
    elif archive_length < 1:
        archive_length = 1
    archive_length_steps = archive_length*24

    # forecasts_foresight = 1 if forecasts_foresight == '' else int(
    #     forecasts_foresight)
    # if forecasts_foresight > 10:
    #     forecasts_foresight = 10
    # elif forecasts_foresight < 1:
    #     forecasts_foresight = 1

    weather_parameter_index = WEATHER_PARAMETERS.index(weather_parameter)

    location_object = location_object_from_input(location)

    # archive = ArchiveRecord.objects.latest('rec_date').rec_data
    archive_templates = ArchiveTemplate.objects.filter(
        location=location_object)
    
    # Getting local datetime at archive location
    timezone_info = zoneinfo.ZoneInfo(location_object.timezone)
    local_datetime = timezone.localtime(timezone=timezone_info)

    # print(local_datetime)
    # print(timezone.localtime(local_datetime, timezone.utc))
    # print("===================")

    # Calculating start archive datetime
    start_archive_datetime = local_datetime.replace(
            minute=0, second=0, microsecond=0)
    
    # print(start_archive_datetime)

    datetime_row, datetime_ = [], start_archive_datetime
    for step in range(archive_length_steps):
        datetime_row.append(datetime_)
        datetime_ -= timedelta(hours=1)
    datetime_row.reverse()

    # for dt in datetime_row:
    #     print(dt.isoformat())

    tooltip_titles = [dt.strftime("%a %H:%M") for dt in datetime_row]
    # tooltip_titles = [weekday_rus[i.weekday()] + i.strftime(" %d.%m %H:%M")
    #                   for i in datetime_row]  # Всплывающие ярлыки


    labels = [i.strftime("%d.%m") if i.hour == 12 else ' ' if i.hour ==
              0 else '' for i in datetime_row]  # Ярлыки оси Х для графика

    # Making datasets for Chartjs
    datasets = []
    for template in archive_templates:
        
        archive_data = []
        for datetime_ in datetime_row:
            try:
                archive_record = Archive.objects.get(
                    archive_template=template,
                    record_datetime=datetime_).data_json[weather_parameter_index]
            except Archive.DoesNotExist:
                archive_record = 'none'
            
            if archive_record is None:
                archive_record = 'none'

            archive_data.append(archive_record)

        datasets.append({
            'label': template.archive_source.name,
            'data': archive_data,
            'borderColor': template.archive_source.chart_color,
            'borderWidth': 1,
            'pointStyle': 'circle',
            'pointRadius': 1,
            'pointHoverRadius': 3,
        })

    chartjs_data = {
        'labels': labels,
        'datasets': datasets,
    }

    last_database_refresh = Archive.objects.latest(
        'scraped_datetime').scraped_datetime.strftime(
            "Database updated:  %d.%m.%Y %H:%M UTC")

    scales_list = ((-5, 5), (755, 765), (0, 10))
    chartjs_options = {'suggestedMin': scales_list[weather_parameter_index][0],
                       'suggestedMax': scales_list[weather_parameter_index][1],
                       'tooltip_titles': tooltip_titles,
                       'last_database_refresh': last_database_refresh,
                       }

    context = {
        'locations': LOCATIONS,
        'location': location,
        'weather_parameters': WEATHER_PARAMETERS,
        'weather_parameter': weather_parameter,
        'archive_length': archive_length,
        # 'forecasts_foresight': forecasts_foresight,
        'chartjs_data': chartjs_data,
        'chartjs_options': chartjs_options,
        'forecast_sources': zip(FORECAST_SOURCES_NAMES, FORECAST_SOURCES_URLS),
    }

    return render(request=request, template_name='website/archive.html', context=context)

########
# MISC #
########


def insert_empty_steps(data_list, symbol):
    """Insert empty steps in data"""
    new_data_list = []
    for item in data_list:
        if item is None:
            new_data_list.append(symbol)
        else:
            new_data_list.append(item)
        new_data_list.append(symbol)

    return new_data_list


def location_object_from_input(location):
    location_string = location.split(', ')
    return Location.objects.get(
        name=location_string[0],
        region=location_string[1],
        country=location_string[2])
