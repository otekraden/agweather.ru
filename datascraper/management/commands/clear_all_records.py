from django.core.management.base import BaseCommand
from datascraper.models import Forecast  # , Archive


class Command(BaseCommand):
    help = 'Clear all forecast and archive records'

    def handle(self, *args, **kwargs):

        Forecast.objects.all().delete()

        self.stdout.write("All records deleted")