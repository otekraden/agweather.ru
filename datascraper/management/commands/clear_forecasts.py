from django.core.management.base import BaseCommand
from datascraper.models import (
    Forecast, ForecastTemplate, elapsed_time_decorator)
from datetime import datetime
from datascraper.logging import init_logger
from backports import zoneinfo

LOGGER = init_logger('Clear forecasts')


class Command(BaseCommand):
    help = 'Clear all forecast records from database.'

    @elapsed_time_decorator(LOGGER)
    def handle(self, *args, **kwargs):

        Forecast.objects.all().delete()

        for template in ForecastTemplate.objects.all():

            template.last_scraped = datetime.fromtimestamp(
                0, tz=zoneinfo.ZoneInfo('UTC'))
            template.save()

        LOGGER.debug("All forecast records has been deleted from database.")
