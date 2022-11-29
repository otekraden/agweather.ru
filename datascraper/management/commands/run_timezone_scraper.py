from django.core.management.base import BaseCommand
from datascraper.models import TimeZone


class Command(BaseCommand):
    help = 'Run timezones scraper from Wikipedia.'

    def handle(self, *args, **kwargs):

        TimeZone.scrap_zones()
