from django.core.management.base import BaseCommand
from datetime import datetime
import yadisk
from dotenv import load_dotenv
import os
import tg_logger
import zipfile
import logging


from django.core import management


class Command(BaseCommand):
    help = 'Dump data of datascraper app to cloud services'

    def handle(self, *args, **kwargs):

        dt = datetime.now().strftime("%d-%m-%Y_%H:%M:%S")
        filename = "dump_db.json"

        with open(filename, "w") as f:
            management.call_command("dumpdata", stdout=f)

        with zipfile.ZipFile(f'{filename}.zip', 'w',
                             compression=zipfile.ZIP_DEFLATED) as myzip:
            myzip.write(filename)

        load_dotenv()
        yandex = yadisk.YaDisk(token=os.environ["YANDEX_TOKEN"])
        yandex.upload(f'{filename}.zip',
                      f'agweather_dump_db/{dt}_{filename}.zip')
        
        token = os.environ["TELEGRAM_TOKEN"]
        users = os.environ["TELEGRAM_USERS"].split('\n')

        logger = logging.getLogger('foo')
        logger.setLevel(logging.INFO)
        # Logging bridge setup
        tg_logger.setup(logger, token=token, users=users)
        
        tg_files_logger = tg_logger.TgFileLogger(
            token=token,
            users=users,
            timeout=10
        )

        file_name = "test.txt"
        with open(file_name, 'w') as example_file:
            example_file.write("Hello from tg_logger by otter18")

        # Base logger


        tg_files_logger.send(file_name, "Dump database")

        # os.remove(filename)
        # os.remove(f'{filename}.zip')


        # print("{0} > Database dump of the Datascraper App created and saved".
        #       format(datetime.now().isoformat(' ')))
