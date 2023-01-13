from datascraper.tests import DatascraperTestBase
from website.views import WEATHER_PARAMETERS
from django.urls import reverse
from datascraper.models import ForecastTemplate


class ForecastViewTest(DatascraperTestBase):

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/forecast/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('website:forecast'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('website:forecast'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'website/forecast.html')

    def test_view_post(self):
        response = self.client.post(reverse('website:forecast'), {
            'location': 'Moscow, Moscow, Russia',
            'weather_parameter': WEATHER_PARAMETERS[0],
            'selection_period': 7})
        self.assertEqual(response.status_code, 200)

    def test_view_datasets(self):
        ForecastTemplate.run_scraper('rp5')
        response = self.client.get(reverse('website:forecast'))
        # print(response.context['chartjs_data']['datasets'][0]['label'])
        self.assertEqual(
            response.context['chartjs_data']['datasets'][0]['label'],
            'RP5')
