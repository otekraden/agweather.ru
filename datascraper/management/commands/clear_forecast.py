from django.core.management.base import BaseCommand
from datascraper.models import Forecast, ForecastTemplate
from datetime import datetime


class Command(BaseCommand):
    help = 'Clear all forecast records.'

    def handle(self, *args, **kwargs):

        Forecast.objects.all().delete()

        for template in ForecastTemplate.objects.all():

            template.last_scraped = datetime(1970, 1, 1, 3)
            template.save()

        self.stdout.write("All forecast records has been deleted.")
