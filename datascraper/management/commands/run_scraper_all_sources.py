from django.core.management.base import BaseCommand
from datascraper.models import ForecastTemplate  # , Archive


class Command(BaseCommand):
    help = 'Run datascraper for all sources'

    def handle(self, *args, **kwargs):
        ForecastTemplate.scrap_forecasts()
        return "Scraper finished its work for all sources."
