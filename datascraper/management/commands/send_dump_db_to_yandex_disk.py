from django.core.management.base import BaseCommand
from datetime import datetime
import yadisk
from dotenv import load_dotenv
import os


class Command(BaseCommand):
    help = 'Dump data of datascraper app'

    def handle(self, *args, **kwargs):

        load_dotenv()
        y = yadisk.YaDisk(token=os.environ["YANDEX_TOKEN"])

        date = datetime.now().strftime("%d-%m-%Y_%H:%M:%S")
        path = '/home/anton/agweather_venv/agweather.online/datascraper/'
        y.upload(f"{path}dump_db.json.zip",
                 f"agweather_dump_db/dump_db_{date}.json.zip")

        print("{0} > Database dump of the Datascraper App created and saved".
              format(datetime.now().isoformat(' ')))
