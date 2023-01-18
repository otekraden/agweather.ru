from website.forms import (
    ForecastTemplate2,
    ArchiveTemplate2,
)
from datascraper.models import ForecastSource, ArchiveSource
from website.tests.test_views import WebsiteTestBase


class ForecastTemplateFormTest(WebsiteTestBase):

    def setUp(self):
        self.forecast_source = \
            ForecastSource.objects.get(scraper_class='yandex')

    def test_input_incorrect_url(self):
        form = ForecastTemplate2(
            forecast_source=self.forecast_source,
            data={'url': 'https://yandexxxxx.ru/'})
        self.assertFalse(form.is_valid())


class ArchiveTemplateFormTest(WebsiteTestBase):

    def setUp(self):
        self.archive_source = ArchiveSource.objects.get(scraper_class='rp5')

    def test_input_incorrect_url(self):
        form = ArchiveTemplate2(
            archive_source=self.archive_source,
            data={'url': 'https://rp55.ru/'})
        self.assertFalse(form.is_valid())
