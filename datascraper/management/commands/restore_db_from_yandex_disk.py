from django.core.management.base import BaseCommand
import yadisk
from dotenv import load_dotenv
import os
from datascraper.logging import init_logger
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
        last_dump_file.download(last_dump_file_name)

        # unzipping dump file
        os.system(f"unzip {last_dump_file_name}")
        os.remove(last_dump_file_name)
        last_dump_file_name = last_dump_file_name.replace(".zip", "")

        # restoring data from dump file
        postgres_db = os.environ["POSTGRES_DB"]
        postgres_user = os.environ["POSTGRES_USER"]
        os.system(f"pg_restore -d {postgres_db} -U {postgres_user} \
                  --no-owner --clean {last_dump_file_name}")

        os.remove(last_dump_file_name)

        LOGGER.debug("Database successfully recovered from Yandex Disk.")
