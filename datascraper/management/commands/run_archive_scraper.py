from django.core.management.base import BaseCommand
from datascraper.models import ArchiveTemplate


class Command(BaseCommand):
    help = 'Run archive scraper.'

    def handle(self, *args, **kwargs):

        ArchiveTemplate.scrap_archives()
