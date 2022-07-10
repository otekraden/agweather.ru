from django.core.management.base import BaseCommand
from datascraper.models import ForecastTemplate
from datetime import datetime


class Command(BaseCommand):
    help = 'Check relevance of data in database. All forecast and archive \
        records must be not older than 1 hour.'

    def handle(self, *args, **kwargs):

        outdated_last_records = ForecastTemplate.get_outdated_last_records()

        if outdated_last_records:

            outdated_sources = [record.forecast_source
                                for record in outdated_last_records]

            msg = [[(source.name+':').ljust(15),
                    outdated_sources.count(source),
                    ForecastTemplate.objects.filter(
                        forecast_source=source).count()]
                   for source in set(outdated_sources)]

            msg = '\n'.join([f"{i[0]} {i[1]}/{i[2]} locs" for i in msg])
            msg = "{0} > Detected forecast sources with OUTDATED data:\n{1}".\
                format(datetime.now().isoformat(' '), msg)

            self.stdout.write(msg)
