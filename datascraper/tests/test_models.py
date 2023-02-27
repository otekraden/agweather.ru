from django.test import TestCase
from datascraper.models import (
    TimeZone,
    validate_first_upper,
    Location,
    WeatherParameter,
    ForecastSource,
    ForecastTemplate,
    Forecast,
    ArchiveSource,
    ArchiveTemplate,
    Archive)
from datascraper.forecasts import BaseForecastScraper
from django.core.exceptions import ValidationError
from django.utils import timezone
from zoneinfo import ZoneInfo
from datetime import timedelta


class ValidateFirstUpperTestCase(TestCase):
    def test_first_is_lower(self):
        with self.assertRaises(ValidationError):
            validate_first_upper('aaaa')


class DatascraperTestBase(TestCase):
    fixtures = ["test_db"]


class TimeZoneTestCase(TestCase):

    def test_timezones_list(self):
        TimeZone.scrap_zones()
        tz_list = TimeZone.zones_list()
        self.assertEqual(len(tz_list), 597)
        self.assertEqual(type(tz_list), list)


class LocationTestCase(DatascraperTestBase):

    def setUp(self):
        self.location = Location.objects.filter(name='Moscow')[0]

    def test_location_local_datetime(self):
        self.assertTrue(
            self.location.local_datetime() - timezone.localtime(
                timezone=ZoneInfo(
                    'Europe/Moscow')) < timedelta(seconds=1))

    def test_location_start_forecast_datetime(self):
        self.assertTrue(
            self.location.start_forecast_datetime() - timezone.localtime(
                timezone=ZoneInfo('Europe/Moscow')).replace(
                minute=0, second=0, microsecond=0) - timedelta(
                    hours=1) < timedelta(seconds=1))

    def test_location_start_archive_datetime(self):
        self.assertTrue(
            self.location.start_archive_datetime() - timezone.localtime(
                timezone=ZoneInfo('Europe/Moscow')).replace(
                minute=0, second=0, microsecond=0) < timedelta(seconds=1))

    def test_locations_list(self):
        locations_list = Location.locations_list()
        self.assertEqual(
            locations_list[0], 'Moscow, Moscow, Russia')
        self.assertEqual(len(locations_list), 2)


class WeatherParameterTestCase(DatascraperTestBase):

    def test_weather_parameter_str(self):
        self.assertEqual(str(WeatherParameter.objects.all()[0]), 'temp')


class ForecastSourceTestCase(DatascraperTestBase):

    def test_forecast_source_str(self):
        self.assertEqual(str(ForecastSource.objects.all()[2]), 'RP5')

    def test_forecast_source_dropdown_list(self):
        self.assertEqual(list(
            ForecastSource.dropdown_list())[2], ('RP5', 'https://rp5.ru/'))


class ForecastTemplateTestCase(DatascraperTestBase):

    def test_forecast_template_str(self):
        self.assertEqual(str(ForecastTemplate.objects.all()[7]),
                         'Yandex Pogoda --> Moscow, Moscow, Russia')

    def test_forecast_template_run_scraper(self):
        self.assertIsNone(ForecastTemplate.run_scraper(scraper_class='foo'))
        self.assertTrue(ForecastTemplate.run_scraper(scraper_class='rp5'))
        self.assertTrue(ForecastTemplate.check_expiration())
        self.assertTrue(ForecastTemplate.run_scraper())
        self.assertIsNone(ForecastTemplate.check_expiration())

        forecast = Forecast.objects.filter(
            forecast_template__id=7).latest('scraped_datetime')
        self.assertEqual(
            str(forecast), 'Meteoinfo.ru --> Moscow, Moscow, Russia')
        self.assertTrue(forecast.is_actual())
        forecast.scraped_datetime = \
            forecast.forecast_template.location.local_datetime() - timedelta(
                hours=2)
        forecast.save()
        self.assertFalse(forecast.is_actual())

    def test_forecast_template_check_expiration(self):
        self.assertTrue(ForecastTemplate.check_expiration())


class ForecastScraperTestCase(DatascraperTestBase):

    def test_get_start_date_from_source(self):
        """Testing transition through the New Year"""
        local_datetime = Location.objects.get(id=1).local_datetime()
        forecast_scraper = BaseForecastScraper(
            local_datetime=local_datetime.replace(year=2023, month=12, day=31),
            start_forecast_datetime=None)
        self.assertEqual(forecast_scraper.get_start_date_from_source(
            month=12, day=31).month, 12)
        self.assertEqual(forecast_scraper.get_start_date_from_source(
            month=1, day=1).month, 1)


class ArchiveTemplateTestCase(DatascraperTestBase):

    def test_archive_source_str(self):
        self.assertEqual(str(ArchiveSource.objects.all()[0]), 'RP5')

    def test_archive_template_str(self):
        self.assertEqual(str(ArchiveTemplate.objects.all()[1]),
                         'RP5 --> Moscow, Moscow, Russia')

    def test_archive_template_run_scraper(self):
        self.assertTrue(ArchiveTemplate.run_scraper())
        archive = Archive.objects.all()[17]
        self.assertEqual(str(archive), '')
