from django.core.management.base import BaseCommand
from datetime import datetime
import yadisk
from dotenv import load_dotenv
import os
# import tg_logger
import zipfile
from datascraper.logging import init_logger
from datascraper.models import elapsed_time_decorator
# from django.core import management

LOGGER = init_logger('Dump database to Clouds')


class Command(BaseCommand):
    help = 'Dump data from database to Cloud services.'

    @elapsed_time_decorator(LOGGER)
    def handle(self, *args, **kwargs):

        # making dump file
        dt = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
        filename = f"{dt}_dump_db"
        # with open(filename, "w") as f:
        #     management.call_command("dumpdata", stdout=f)

        # for reading environmental vars
        load_dotenv()
        postgres_db = os.environ["POSTGRES_DB"]
        postgres_user = os.environ["POSTGRES_USER"]

        # creating dump file
        os.system(f"pg_dump -U {postgres_user} -Fc \
                #   --exclude-table 'public.django_content_type' \
                #   --exclude-table 'public.auth_permission' \
                  {postgres_db} > {filename}")

        LOGGER.debug("Dump file created")

        # zipping dump file
        with zipfile.ZipFile(f'{filename}.zip', 'w',
                             compression=zipfile.ZIP_DEFLATED) as myzip:
            myzip.write(filename)
        LOGGER.debug("Dump file archived. Starting upload to Yandex Disk")

        # for reading environmental vars
        load_dotenv()

        # sending dump to Yandex Disk
        try:
            yandex = yadisk.YaDisk(token=os.environ["YANDEX_TOKEN"])
            yandex.upload(f'{filename}.zip',
                          f'agweather_dump_db/{filename}.zip',
                          timeout=(100, 100))
        except Exception as e:
            LOGGER.error(e)
        # LOGGER.debug("Sent to Yandex Disk. Starting upload Telegram")

        # # sending dump to Telegram (file size limit 50MB)
        # try:
        #     token = os.environ["TELEGRAM_TOKEN"]
        #     users = os.environ["TELEGRAM_USERS"].split('\n')
        #     tg_files_logger = tg_logger.TgFileLogger(
        #         token=token,
        #         users=users,
        #         timeout=10
        #     )
        #     tg_files_logger.send(f'{filename}.zip')
        # except Exception as e:
        #     LOGGER.error(e)

        # removing temp files
        # os.remove(filename)
        # os.remove(f'{filename}.zip')

        LOGGER.debug("Database successfully sent to cloud services.")
