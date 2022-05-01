from django.shortcuts import render
from django.http import HttpResponse
from .main import main
from .models import Location, WeatherPrameter, ForecastSource, \
    ForecastTemplate, ArchiveSource, ArchiveTemplate


def test(request):
    # return HttpResponse("Hello from VPS!!!!")
    return HttpResponse(main())


def init_database(request):

    loc1 = Location.objects.get_or_create(
        name="Saint-Petersburg", region="Saint-Petersburg", country="Russia",
        timezone="Europe/Moscow")[0]
    loc2 = Location.objects.get_or_create(
        name="Moscow", region="Moscow", country="Russia",
        timezone="Europe/Moscow")[0]

    WeatherPrameter.objects.get_or_create(
        param_key="temp", name="Temperature", tooltip="Air temperature",
        meas_unit="℃")
    WeatherPrameter.objects.get_or_create(
        param_key="press", name="Pressure", tooltip="Atmospheric pressure",
        meas_unit="mmHg")
    WeatherPrameter.objects.get_or_create(
        param_key="wind_speed", name="Wind speed", tooltip="Wind speed",
        meas_unit="m/s")

    as1 = ArchiveSource.objects.get_or_create(
        id="rp5", name="RP5", url="https://rp5.ru/", chart_color="white")[0]

    fs1 = ForecastSource.objects.get_or_create(
        id="rp5", name="RP5", url="https://rp5.ru/", chart_color="#1E90FF")[0]
    fs2 = ForecastSource.objects.get_or_create(
        id="yandex", name="Yandex Pogoda", url="https://yandex.ru/pogoda/",
        chart_color="#FF0000")[0]
    fs3 = ForecastSource.objects.get_or_create(
        id="meteoinfo", name="Meteoinfo.ru",
        url="https://meteoinfo.ru/forecasts/", chart_color="#00FF00")[0]
    fs4 = ForecastSource.objects.get_or_create(
        id="foreca", name="Foreca.ru", url="https://www.foreca.ru/",
        chart_color="#FBFF00")[0]

    ForecastTemplate.objects.get_or_create(
        forecast_source=fs1, location=loc1,
        location_relative_url="Погода_в_Санкт-Петербурге")
    ForecastTemplate.objects.get_or_create(
        forecast_source=fs2, location=loc1,
        location_relative_url="saint-petersburg")
    ForecastTemplate.objects.get_or_create(
        forecast_source=fs3, location=loc1,
        location_relative_url="russia/leningrad-region/sankt-peterburg")
    ForecastTemplate.objects.get_or_create(
        forecast_source=fs4, location=loc1,
        location_relative_url="Saint_Petersburg?details=")

    ForecastTemplate.objects.get_or_create(
        forecast_source=fs1, location=loc2,
        location_relative_url="Погода_в_Москве_(ВДНХ)")
    ForecastTemplate.objects.get_or_create(
        forecast_source=fs2, location=loc2,
        location_relative_url="213")
    ForecastTemplate.objects.get_or_create(
        forecast_source=fs3, location=loc2,
        location_relative_url="russia/moscow-area/moscow")
    ForecastTemplate.objects.get_or_create(
        forecast_source=fs4, location=loc2,
        location_relative_url="Moscow?details=")
    
    ArchiveTemplate.objects.get_or_create(
        archive_source=as1, location=loc1,
        location_relative_url="Архив_погоды_в_Санкт-Петербурге")
    ArchiveTemplate.objects.get_or_create(
        archive_source=as1, location=loc2,
        location_relative_url="Архив_погоды_в_Москве_(ВДНХ)")

    return HttpResponse("Database filled by initial data.")
