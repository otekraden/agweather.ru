from django.core.management.base import BaseCommand
import yadisk
from dotenv import load_dotenv
import os
import zipfile
from datascraper.logging import init_logger


class Command(BaseCommand):
    help = 'Recover data of datascraper app from Yandex Disk'

    def handle(self, *args, **kwargs):

        logger = init_logger('Recover database')

        logger.info("> START")

        load_dotenv()
        yandex = yadisk.YaDisk(token=os.environ["YANDEX_TOKEN"])
        last_dump_file = next(yandex.get_last_uploaded())
        last_dump_file_name = last_dump_file.name
        logger.debug(f'Last dump file detected: {last_dump_file_name}')
        last_dump_file.download(last_dump_file_name)

        with zipfile.ZipFile(last_dump_file_name, 'r') as myzip:
            myzip.extractall('')

        os.remove(last_dump_file_name)
        last_dump_file_name = last_dump_file_name.rstrip('.zip')
        logger.debug(last_dump_file_name)
        # os.remove(f'{filename}.zip')

        logger.info("> END")
