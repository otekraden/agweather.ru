from django.core.management.base import BaseCommand
from datascraper.models import ForecastTemplate


class Command(BaseCommand):
    help = "Run weather forecast scraper for specified source. " + \
        "If source not specified, scraper will run for all sources."

    def add_arguments(self, parser):
        parser.add_argument(
            'scraper_class', type=str, nargs='?', default=None)

    def handle(self, *args, **kwargs):

        scraper_class = kwargs['scraper_class']

        ForecastTemplate.run_scraper(scraper_class)
