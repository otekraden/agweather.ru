from django.core.management.base import BaseCommand
from datascraper.models import Archive
import csv
import os.path


class Command(BaseCommand):
    help = 'Dump archive to *csv.'

    def handle(self, *args, **kwargs):

        filename = "dump_archive.csv"

        try:
            os.remove(filename)
        except FileNotFoundError:
            pass

        # Write CSV file
        with open(filename, 'a') as fp:

            writer = csv.writer(fp, delimiter=",")

            for obj in Archive.objects.all():

                record = (  # obj.scraped_datetime,
                          obj.record_datetime,
                          obj.data_json,
                          obj.archive_template)

                writer.writerow(record)

        self.stdout.write("All archive records has been dumped.")
