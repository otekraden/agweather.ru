from django.core.management.base import BaseCommand
from datascraper.models import TimeZone
from datascraper.logging import init_logger
from datascraper.models import elapsed_time_decorator

LOGGER = init_logger('Timezones scraper')


class Command(BaseCommand):
    help = 'Run timezones scraper from Wikipedia.'

    @elapsed_time_decorator(LOGGER)
    def handle(self, *args, **kwargs):

        TimeZone.scrap_zones()

        LOGGER.debug("Timezones successfully scraped.")
