from django.test import TestCase
from website.views import (
    WEATHER_PARAMETERS,
    check_int_input
)
from django.urls import reverse
from datascraper.models import (
    ForecastTemplate,
    ArchiveTemplate,
    Location,
    Forecast)
from datetime import datetime, timedelta


class WebsiteTestBase(TestCase):
    fixtures = ["test_db"]


class ForecastViewTest(WebsiteTestBase):

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/forecast/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        self.client.login(username='anton', password='#ASDF2023')
        response = self.client.get(reverse('website:forecast'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['location'], 'Moscow, Moscow, Russia')

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
        print(response.context['chartjs_data']['datasets'][0]['label'])
        self.assertEqual(
            response.context['chartjs_data']['datasets'][0]['label'],
            'RP5')
        
    def test_view_location_without_template(self):
        location = Location.objects.create(
            name='Gothem',
            region='New York',
            country='USA')
        response = self.client.post(reverse('website:forecast'), {
            'location': 'Gothem, New York, USA',
            'weather_parameter': WEATHER_PARAMETERS[0],
            'selection_period': 7})
        # print(response.content)
        self.assertEqual(
            response.content,
            bytes(f"No forecast templates fo location {location}.", 'utf-8'))


class ArchiveViewTest(WebsiteTestBase):

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/archive/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('website:archive'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('website:archive'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'website/archive.html')

    def test_view_post(self):
        response = self.client.post(reverse('website:archive'), {
            'location': 'Moscow, Moscow, Russia',
            'weather_parameter': WEATHER_PARAMETERS[0],
            'selection_period': 7,
            'prediction_range': 1,
            'period_end_date': datetime.now().strftime('%d/%m/%Y')})
        self.assertEqual(response.status_code, 200)

    def test_view_datasets(self):
        ForecastTemplate.run_scraper(scraper_class='rp5')
        for forecast in Forecast.objects.all():
            forecast.forecast_datetime -= timedelta(days=1)
            forecast.save()
        ArchiveTemplate.run_scraper()
        response = self.client.get(reverse('website:archive'))
        self.assertEqual(
            response.context['chartjs_data']['datasets'][0]['label'],
            'Archive_RP5')
        self.assertEqual(
            response.context['chartjs_data']['datasets'][1]['label'], 'RP5')


class FeedbackViewTest(WebsiteTestBase):

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/feedback/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/forum/topic/2/')

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('website:feedback'))
        self.assertEqual(response.status_code, 302)


class MiscTest(WebsiteTestBase):

    def test_check_int_input(self):

        self.assertEqual(check_int_input('10', 3, 7, 9), 7)
        self.assertEqual(check_int_input('', 3, 7, 6), 6)
        self.assertEqual(check_int_input('1', 3, 7, 9), 3)
        self.assertEqual(check_int_input('5', 3, 7, 9), 5)
