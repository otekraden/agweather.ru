from django.core.management.base import BaseCommand
from datascraper.models import Archive


class Command(BaseCommand):
    help = 'Clear all archive records.'

    def handle(self, *args, **kwargs):

        Archive.objects.all().delete()

        self.stdout.write("All archive records has been deleted")
