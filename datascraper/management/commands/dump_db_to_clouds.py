from django.core.management.base import BaseCommand
from datetime import datetime
import yadisk
import os
import subprocess
from datascraper.logging import init_logger
from datascraper.models import elapsed_time_decorator

LOGGER = init_logger('Dump database & media to Yandex Disk')


class Command(BaseCommand):
    help = 'Dump data from database & media folder to Yandex Disk.'

    @elapsed_time_decorator(LOGGER)
    def handle(self, *args, **kwargs):

        # making dump names
        dt = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
        dump_name = f"{dt}_dump"
        db_file_name = f"{dt}_db"

        # creating database dump file
        process = subprocess.run(
            ['pg_dump',
                '--dbname=postgresql://anton:Nahsi7ahboid#004@localhost:5432/agweather_db',
                '-Fc',
                # '-v',
                '-f',
                db_file_name])

        if process.returncode:
            LOGGER.debug('Command failed. Return code : {}'.format(
                process.returncode))
            exit(1)

        LOGGER.debug("Dump database file created")

        # zipping database vs media
        subprocess.run(['zip', '-r', '-q',
                        f'{dump_name}.zip',
                        f'{db_file_name}',
                        'media',
                        ])

        LOGGER.debug("Database dump file & media folder zipped")

        # sending dump to Yandex Disk
        try:
            yandex = yadisk.YaDisk(token=os.environ.get("YANDEX_TOKEN"))
            yandex.upload(f'{dump_name}.zip',
                          f'agweather_dump_db/{dump_name}.zip',
                          timeout=(100, 100))
        except Exception as e:
            LOGGER.error(e)
        LOGGER.debug("Sent to Yandex Disk")

        # removing temp files
        os.remove(db_file_name)
        os.remove(f'{dump_name}.zip')
