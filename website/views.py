from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from datascraper.models import (
    WeatherParameter, Location, ForecastTemplate, Forecast, ForecastSource,
    ArchiveTemplate, Archive)
from backports import zoneinfo
from django.utils import timezone
from datetime import timedelta, datetime


WEATHER_PARAMETERS = [
    f'{par.name}, {par.meas_unit}' for par in WeatherParameter.objects.all()]
LOCATIONS = [f'{loc.name}, {loc.region}, {loc.country}'
             for loc in Location.objects.all()]
FORECAST_SOURCES_URLS = [source.url for source in ForecastSource.objects.all()]
FORECAST_SOURCES_NAMES = [
    source.name for source in ForecastSource.objects.all()]


def forecast(request):

    if request.method == 'GET':
        # Default location Saint-Petersburg
        location = LOCATIONS[4]
        # Default show Temperature
        weather_parameter = WEATHER_PARAMETERS[0]
        # Default one week
        forecast_length = 7

    elif request.method == 'POST':
        location = request.POST.get('location')
        weather_parameter = request.POST.get('weather_parameter')
        forecast_length = request.POST.get('forecast_length')

    forecast_length = check_int_input(forecast_length, 1, 14, 7)
    forecast_length_steps = forecast_length*24

    weather_parameter_index = WEATHER_PARAMETERS.index(weather_parameter)

    location_object = location_object_from_input(location)

    forecast_templates = ForecastTemplate.objects.filter(
        location=location_object)

    # Calculating start forecast datetime
    start_forecast_datetime = forecast_templates[0].start_forecast_datetime()

    # Generating datetime row
    datetime_row, datetime_ = [], start_forecast_datetime
    for step in range(forecast_length_steps):
        datetime_row.append(datetime_)
        datetime_ += timedelta(hours=1)

    # Tooltip titles for Chartjs
    tooltip_titles = [dt.strftime("%d.%m %H:%M") for dt in datetime_row]

    # Making datasets for Chartjs
    datasets = []
    for template in forecast_templates:

        forecasts = Forecast.objects.filter(
            scraped_datetime=template.last_scraped,
            forecast_template=template)

        if not forecasts or not forecasts[0].is_actual():
            continue

        forecast_data = []
        for datetime_ in datetime_row:
            try:
                forecast_record = forecasts.get(
                    forecast_datetime=datetime_).forecast_data[
                        weather_parameter_index]
            except (ObjectDoesNotExist, MultipleObjectsReturned):
                forecast_record = 'none'

            if not forecast_record and forecast_record != 0:
                forecast_record = 'none'

            forecast_data.append(forecast_record)

        datasets.append({
            'label': template.forecast_source.name,
            'data': forecast_data,
            'borderColor': template.forecast_source.chart_color,
            'backgroundColor': template.forecast_source.chart_color,
        })

    # For X axe in Chartjs
    labels = [i.strftime("%a") if i.hour == 12 else ' '
              if i.hour == 0 else ''
              for i in datetime_row]

    chartjs_data = {
        'labels': labels,
        'datasets': datasets,
    }

    last_database_refresh = ForecastTemplate.objects.latest(
        'last_scraped').last_scraped.strftime(
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
        'timezone': start_forecast_datetime.tzinfo,
        }

    return render(
        request=request,
        template_name='website/forecast.html',
        context=context)


def archive(request):
    """View"""

    if request.method == 'GET':
        # Default location Saint-Petersburg
        location = LOCATIONS[4]
        # Default show Temperature
        weather_parameter = WEATHER_PARAMETERS[0]
        # Default one week
        archive_length = 7
        # Default 24h
        prediction_range = 24
        # Default today
        period_end_date = datetime.now().strftime("%d/%m/%Y")

    elif request.method == 'POST':
        location = request.POST.get('location')
        weather_parameter = request.POST.get('weather_parameter')
        archive_length = request.POST.get('archive_length')
        period_end_date = request.POST.get('period_end_date')
        prediction_range = request.POST.get('prediction_range')

    archive_length = check_int_input(archive_length, 1, 30, 14)
    archive_length_steps = archive_length*24

    prediction_range = check_int_input(prediction_range, 1, 336, 1)

    weather_parameter_index = WEATHER_PARAMETERS.index(weather_parameter)

    location_object = location_object_from_input(location)
    archive_templates = ArchiveTemplate.objects.filter(
        location=location_object)
    forecast_templates = ForecastTemplate.objects.filter(
        location=location_object)

    # Getting local datetime at archive location
    timezone_info = zoneinfo.ZoneInfo(location_object.timezone)
    # local_date = timezone.localdate(timezone=timezone_info)

    # Calculating end archive datetime
    end_archive_datetime = tuple(map(int, period_end_date.split('/')))
    end_archive_datetime = timezone.datetime(
        end_archive_datetime[2],
        end_archive_datetime[1],
        end_archive_datetime[0],
        tzinfo=timezone_info) + timedelta(1)

    datetime_row, datetime_ = [], end_archive_datetime
    for step in range(archive_length_steps):
        datetime_row.append(datetime_)
        datetime_ -= timedelta(hours=1)
    datetime_row.reverse()

    tooltip_titles = [dt.strftime("%a %H:%M") for dt in datetime_row]

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
                    record_datetime=datetime_).data_json[
                        weather_parameter_index]
            except (ObjectDoesNotExist, MultipleObjectsReturned):
                archive_record = 'none'

            if not archive_record and archive_record != 0:
                archive_record = 'none'

            archive_data.append(archive_record)

        datasets.append({
            'label': f'Archive_{template.archive_source.name}',
            'data': archive_data,
            'borderColor': template.archive_source.chart_color,
            'borderWidth': 1,
            'pointStyle': 'circle',
            'pointRadius': 3,
            'pointHoverRadius': 10,
        })

    for template in forecast_templates:

        forecasts = Forecast.objects.filter(
            forecast_template=template,
            prediction_range_hours=prediction_range,
            forecast_datetime__range=(datetime_row[0], datetime_row[-1]))

        if not forecasts:
            # prediction_range += 1
            continue

        forecast_data = []
        for datetime_ in datetime_row:
            try:
                forecast_record = forecasts.get(
                    forecast_datetime=datetime_).forecast_data[
                        weather_parameter_index]
            except (ObjectDoesNotExist, MultipleObjectsReturned):
                forecast_record = 'none'

            if not forecast_record and forecast_record != 0:
                forecast_record = 'none'

            forecast_data.append(forecast_record)

        datasets.append({
            'label': template.forecast_source.name,
            'data': forecast_data,
            'borderColor': template.forecast_source.chart_color,
            'backgroundColor': template.forecast_source.chart_color,
            'borderWidth': 0,
            'pointStyle': 'triangle',
            'pointRadius': 6,
            'pointHoverRadius': 12,
        })

    chartjs_data = {
        'labels': labels,
        'datasets': datasets,
    }

    last_database_refresh = ForecastTemplate.objects.latest(
        'last_scraped').last_scraped.strftime(
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
        'period_end_date': period_end_date,
        'prediction_range': prediction_range,
        'chartjs_data': chartjs_data,
        'chartjs_options': chartjs_options,
        'forecast_sources': zip(FORECAST_SOURCES_NAMES, FORECAST_SOURCES_URLS),
        'timezone': timezone_info,
    }

    return render(
        request=request, template_name='website/archive.html', context=context)

########
# MISC #
########


def location_object_from_input(location):
    location_string = location.split(', ')
    return Location.objects.get(
        name=location_string[0],
        region=location_string[1],
        country=location_string[2])


def check_int_input(value, min, max, default):
    value = default if value == '' else int(value)
    if value > max:
        value = max
    elif value < min:
        value = min
    return value
