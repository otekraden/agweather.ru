from django.core.management.base import BaseCommand
from datascraper.models import ArchiveTemplate
from datetime import datetime


class Command(BaseCommand):
    help = 'Run archive scraper.'

    def handle(self, *args, **kwargs):

        print(f"{datetime.now().isoformat()} > Archive scraper START")

        ArchiveTemplate.scrap_archive()

        print(f"{datetime.now().isoformat()} > Archive scraper STOP")

        return "Archive scraper finished its work."
