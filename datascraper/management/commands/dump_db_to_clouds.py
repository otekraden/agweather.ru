from django.core.management.base import BaseCommand
from datetime import datetime
import yadisk
from dotenv import load_dotenv
import os
import tg_logger
import zipfile
from datascraper.logging import init_logger

from django.core import management


class Command(BaseCommand):
    help = 'Dump data of datascraper app to cloud services'

    def handle(self, *args, **kwargs):

        logger = init_logger('Dump database')

        logger.info("> START")

        dt = datetime.now().strftime("%d-%m-%Y_%H:%M:%S")
        filename = f"{dt}_dump_db.json"

        with open(filename, "w") as f:
            management.call_command("dumpdata", stdout=f)

        with zipfile.ZipFile(f'{filename}.zip', 'w',
                             compression=zipfile.ZIP_DEFLATED) as myzip:
            myzip.write(filename)

        load_dotenv()

        try:
            yandex = yadisk.YaDisk(token=os.environ["YANDEX_TOKEN"])
            yandex.upload(f'{filename}.zip',
                          f'agweather_dump_db/{filename}.zip')
        except Exception as e:
            logger.error(e)

        try:
            token = os.environ["TELEGRAM_TOKEN"]
            users = os.environ["TELEGRAM_USERS"].split('\n')
            tg_files_logger = tg_logger.TgFileLogger(
                token=token,
                users=users,
                timeout=10
            )
            tg_files_logger.send(f'{filename}.zip')
        except Exception as e:
            logger.error(e)

        os.remove(filename)
        os.remove(f'{filename}.zip')

        logger.info("> END")
