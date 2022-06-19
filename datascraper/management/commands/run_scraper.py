from django.core.management.base import BaseCommand
from datascraper.models import ForecastTemplate, ForecastSource


class Command(BaseCommand):
    help = 'Run datascraper for specified source.'

    def add_arguments(self, parser):
        parser.add_argument('forecast_source_id')

    def handle(self, *args, **kwargs):

        forecast_source_id = kwargs['forecast_source_id']

        try:
            if forecast_source_id == 'all':
                ForecastTemplate.scrap_forecasts()
            else:
                ForecastSource.objects.get(id=forecast_source_id)
                ForecastTemplate.scrap_forecasts(forecast_source_id)

            return f"Scraper finished its work for {forecast_source_id}."
        except Exception as e:
            print(e)
