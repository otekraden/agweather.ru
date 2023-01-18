from django.core.management.base import BaseCommand
from datascraper.models import Archive, elapsed_time_decorator
from datascraper.logging import init_logger

LOGGER = init_logger('Clear archive')


class Command(BaseCommand):
    help = 'Clear all archive records from database.'

    @elapsed_time_decorator(LOGGER)
    def handle(self, *args, **kwargs):
        try:
            Archive.objects.all().delete()
            LOGGER.debug("All archive records has been deleted from database.")
        except Exception:
            return
        return True
