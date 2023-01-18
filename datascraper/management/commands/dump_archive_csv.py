from django.core.management.base import BaseCommand
from datascraper.models import Archive, elapsed_time_decorator
import csv
import os.path
from tqdm import tqdm
from datascraper.logging import init_logger
from website.views import WEATHER_PARAMETERS

LOGGER = init_logger('Dump database to CSV')


class Command(BaseCommand):
    help = 'Dump weather archive to CSV file.'

    @elapsed_time_decorator(LOGGER)
    def handle(self, *args, **kwargs):

        filename = "dump_archive.csv"

        # field names
        field_names = ['archive_source', 'location', 'record_datetime']
        field_names.extend(WEATHER_PARAMETERS)
        field_names[3] = 'Temperature, *C'

        # Remove old dump file
        try:
            os.remove(filename)
        except FileNotFoundError:
            pass

        # writing to csv file
        with open(filename, 'w') as csvfile:

            writer = csv.writer(csvfile, delimiter=';')
            writer.writerow(field_names)

            # writing data rows
            for obj in tqdm(Archive.objects.all()):

                data_json = obj.data_json
                # for Excel replace decimal delimiter to comma
                for i, x in enumerate(data_json):
                    data_json[i] = str(data_json[i]).replace('.', ',')

                record = (obj.archive_template.archive_source,
                          obj.archive_template.location,
                          obj.record_datetime.strftime("%d/%m/%Y %H:%M"),
                          *data_json)

                writer.writerow(record)

        self.stdout.write(
            f"All archive records has been dumped to {filename} file.")
