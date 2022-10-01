from django.core.management.base import BaseCommand
from datascraper.models import ArchiveTemplate, A_LOGGER as logger


class Command(BaseCommand):
    help = 'Run archive scraper.'

    def handle(self, *args, **kwargs):

        logger.info("START")

        ArchiveTemplate.scrap_archive()

        logger.info("END")
