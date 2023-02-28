from django.core.management.base import BaseCommand
from datetime import datetime
import yadisk
from dotenv import load_dotenv
import os
import tg_logger
import zipfile
from datascraper.logging import init_logger
from datascraper.models import elapsed_time_decorator

LOGGER = init_logger('Dump database to Clouds')


class Command(BaseCommand):
    help = 'Dump data from database to Cloud services.'

    @elapsed_time_decorator(LOGGER)
    def handle(self, *args, **kwargs):

        # making dump file
        dt = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
        dump_file_name = f"{dt}_dump_db"

        # for reading environmental vars
        load_dotenv()
        postgres_db = os.environ["POSTGRES_DB"]
        postgres_user = os.environ["POSTGRES_USER"]

        # creating dump file
        os.system(f"pg_dump -U {postgres_user} -Ft \
                  --exclude-table 'public.django_content_type' \
                  --exclude-table 'public.auth_permission' \
                  {postgres_db} > {dump_file_name}")

        LOGGER.debug("Dump file created")

        # zipping dump file
        with zipfile.ZipFile(f'{dump_file_name}.zip', 'w',
                             compression=zipfile.ZIP_DEFLATED) as myzip:
            myzip.write(dump_file_name)
        LOGGER.debug("Dump file archived")

        # sending dump to Yandex Disk
        try:
            yandex = yadisk.YaDisk(token=os.environ["YANDEX_TOKEN"])
            yandex.upload(f'{dump_file_name}.zip',
                          f'agweather_dump_db/{dump_file_name}.zip',
                          timeout=(100, 100))
        except Exception as e:
            LOGGER.error(e)
        LOGGER.debug("Sent to Yandex Disk")

        # sending dump to Telegram (file size limit 50M)
        try:
            token = os.environ["TELEGRAM_TOKEN"]
            users = os.environ["TELEGRAM_USERS"].split('\n')
            tg_files_logger = tg_logger.TgFileLogger(
                token=token,
                users=users,
                timeout=10
            )
            tg_files_logger.send(f'{dump_file_name}.zip')
        except Exception as e:
            LOGGER.error(e)

        # removing temp files
        os.remove(dump_file_name)
        os.remove(f'{dump_file_name}.zip')

        LOGGER.debug("Sent to Telegram")
