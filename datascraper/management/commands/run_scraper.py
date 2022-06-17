from django.core.management.base import BaseCommand
from datascraper.models import ForecastTemplate  # , Archive


class Command(BaseCommand):
    help = 'Run datascraper'

    def handle(self, *args, **kwargs):
        ForecastTemplate.scrap_all_forecasts()
        return "Scraper finished its work."
    
