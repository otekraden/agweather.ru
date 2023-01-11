from django.test import TestCase
from .models import (
    TimeZone,
    validate_first_upper,
    Location)
from django.core.exceptions import ValidationError
from django.utils import timezone
from backports import zoneinfo
from datetime import timedelta
# from datetime import datetime


class ValidateFirstUpperTestCase(TestCase):
    def test_first_is_lower(self):
        with self.assertRaises(ValidationError):
            validate_first_upper('aaaa')


class TimeZoneTestCase(TestCase):
    def setUp(self):
        TimeZone.scrap_zones()
        self.timezones_list = TimeZone.zones_list()

    def test_type_of_timezones_list(self):
        """Checking timezones scraper"""
        self.assertEqual(type(self.timezones_list), list)

    def test_len_of_timezones_list(self):
        self.assertEqual(len(self.timezones_list), 597)


class LocationTestCase(TestCase):
    def setUp(self):
        self.location = Location.objects.create(
            name='Moscow',
            region='Moscow',
            country='Russia',
            timezone='Europe/Moscow')

    def test_location_local_datetime(self):
        self.assertTrue(
            self.location.local_datetime() - timezone.localtime(
                timezone=zoneinfo.ZoneInfo(
                    'Europe/Moscow')) < timedelta(seconds=1))

    def test_location_start_forecast_datetime(self):
        self.assertTrue(
            self.location.start_forecast_datetime() - timezone.localtime(
                timezone=zoneinfo.ZoneInfo('Europe/Moscow')).replace(
                minute=0, second=0, microsecond=0) - timedelta(
                    hours=1) < timedelta(seconds=1))

    def test_location_start_archive_datetime(self):
        self.assertTrue(
            self.location.start_archive_datetime() - timezone.localtime(
                timezone=zoneinfo.ZoneInfo('Europe/Moscow')).replace(
                minute=0, second=0, microsecond=0) < timedelta(seconds=1))

    # def test_locations_list(self):
    #     self.assertEqual(Location.locations_list(), ['Moscow, Moscow, Russia'])
