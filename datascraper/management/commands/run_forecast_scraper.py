from django.core.management.base import BaseCommand
from datascraper.models import ForecastTemplate, ForecastSource
from datascraper.logging import init_logger


class Command(BaseCommand):
    help = 'Run forecast scraper for specified source.'

    def add_arguments(self, parser):
        parser.add_argument('forecast_source_id')

    def handle(self, *args, **kwargs):
        logger = init_logger('Forecast scraper')

        logger.info("> START")

        forecast_source_id = kwargs['forecast_source_id']

        try:
            if forecast_source_id == 'all':
                ForecastTemplate.scrap_forecasts(logger)
            else:
                ForecastSource.objects.get(id=forecast_source_id)
                ForecastTemplate.scrap_forecasts(logger, forecast_source_id)

        except Exception as e:
            logger.error(e)

        logger.info("> END")

        outdated_report = ForecastTemplate.get_outdated_report()

        if outdated_report:

            outdated_report = f"> OUTDATED data detected:\n{outdated_report}"

            logger.critical(outdated_report)
