from django.core.management.base import BaseCommand
from datascraper.models import ForecastTemplate, ArchiveTemplate


class Command(BaseCommand):
    help = 'Run all weather forecast and archive scrapers.'

    def handle(self, *args, **kwargs):

        ForecastTemplate.run_scraper()
        ArchiveTemplate.run_scraper()
