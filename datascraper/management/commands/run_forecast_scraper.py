from django.core.management.base import BaseCommand
from datascraper.models import ForecastTemplate


class Command(BaseCommand):
    help = 'Run forecast scraper for specified source.'

    def add_arguments(self, parser):
        parser.add_argument(
            'forecast_source_id', type=str, nargs='?', default=None)

    def handle(self, *args, **kwargs):

        forecast_source_id = kwargs['forecast_source_id']

        ForecastTemplate.run_scraper(forecast_source_id)
