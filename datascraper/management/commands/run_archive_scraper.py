from django.core.management.base import BaseCommand
from datascraper.models import ArchiveTemplate
from datascraper.logging import init_logger


class Command(BaseCommand):
    help = 'Run archive scraper.'

    def handle(self, *args, **kwargs):
        logger = init_logger('Archive scraper')

        logger.info("> START")

        ArchiveTemplate.scrap_archive(logger)

        logger.info("> END")
