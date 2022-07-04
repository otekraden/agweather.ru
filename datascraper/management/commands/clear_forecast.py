from django.core.management.base import BaseCommand
from datascraper.models import Forecast


class Command(BaseCommand):
    help = 'Clear all forecast records.'

    def handle(self, *args, **kwargs):

        Forecast.objects.all().delete()

        self.stdout.write("All forecast records has been deleted.")
