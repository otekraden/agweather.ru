from django.core.management.base import BaseCommand
import yadisk
from dotenv import load_dotenv
import os
from datascraper.logging import init_logger
from django.core import management
from datascraper.models import elapsed_time_decorator

LOGGER = init_logger('Recover database from Yandex Disk')


class Command(BaseCommand):
    help = 'Recover database from Yandex Disk'

    @elapsed_time_decorator(LOGGER)
    def handle(self, *args, **kwargs):

        # for reading environmental vars
        load_dotenv()

        # loading dump file from Yandex Disk
        yandex = yadisk.YaDisk(token=os.environ["YANDEX_TOKEN"])
        last_dump_file = next(yandex.get_last_uploaded())
        last_dump_file_name = last_dump_file.name
        LOGGER.debug(f'Last dump file detected: {last_dump_file_name}')
        last_dump_file.download(last_dump_file_name)

        # recovering database
        management.call_command(
            "loaddata",
            last_dump_file_name,
            "--exclude",
            "auth.permission",
            "--exclude",
            "contenttypes",
            verbosity=0)

        # removing temp files
        os.remove(last_dump_file_name)

        LOGGER.debug("Database successfully recovered from Yandex Disk.")
