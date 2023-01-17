from django.test import TestCase
from website.views import (
    WEATHER_PARAMETERS,
    check_int_input
)
from django.urls import reverse
from datascraper.models import (
    ForecastTemplate,
    ArchiveTemplate,
    Archive,
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
        self.assertEqual(
            response.context['location'], 'Moscow, Moscow, Russia')

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
        self.assertEqual(
            response.context['chartjs_data']['datasets'][0]['label'],
            'RP5')

    def test_view_location_without_template(self):
        location = Location.objects.create(
            name='Gotham',
            region='New York',
            country='USA')
        response = self.client.post(reverse('website:forecast'), {
            'location': 'Gotham, New York, USA',
            'weather_parameter': WEATHER_PARAMETERS[0],
            'selection_period': 7})
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


class LocationCreateViewTest(WebsiteTestBase):

    def test_redirect_if_not_logged_in(self):

        response = self.client.get(reverse('website:add_location'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_forbidden_if_logged_in_but_not_correct_permission(self):
        self.client.login(username='Joker', password='#ASDF20241')
        response = self.client.get(reverse('website:add_location'))
        self.assertEqual(response.status_code, 403)

    def test_logged_in_with_correct_permission(self):
        self.client.login(username='Batman', password='#ASDF2024')
        response = self.client.get(reverse('website:add_location'))
        self.assertEqual(response.status_code, 200)

    def test_logged_in_with_correct_permission_another_user(self):
        self.client.login(username='anton', password='#ASDF2023')
        response = self.client.get(reverse('website:add_location'))
        self.assertEqual(response.status_code, 200)

    def test_uses_correct_template(self):
        self.client.login(username='Batman', password='#ASDF2024')
        response = self.client.get(reverse('website:add_location'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'website/location_form.html')

    def test_form_valid(self):
        self.client.login(username='Batman', password='#ASDF2024')
        response = self.client.post(reverse('website:add_location'), {
            'name': 'Gotham',
            'region': 'Gotham',
            'country': 'USA',
            'timezone': 'America/New_York'
            })

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, reverse('website:add_forecast_template'))

    def test_form_invalid_name(self):
        self.client.login(username='Batman', password='#ASDF2024')
        response = self.client.post(reverse('website:add_location'), {
            'name': 'gotham',
            'region': 'Gotham',
            'country': 'USA',
            'timezone': 'America/New_York'
            })

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context['form'],
            'name',
            'First letter must be uppercase.')

    def test_form_location_already_exists(self):
        self.client.login(username='Batman', password='#ASDF2024')
        response = self.client.post(reverse('website:add_location'), {
            'name': 'Moscow',
            'region': 'Moscow',
            'country': 'Russia',
            'timezone': 'Europe/Moscow'
            })

        self.assertEqual(response.status_code, 200)
        self.assertInHTML(
            "Location with this Name, Region and Country already exists.",
            response.content.decode())


class ForecastTemplateWizardTest(WebsiteTestBase):

    def setUp(self):
        ForecastTemplate.objects.get(id=1).delete()

    def test_forecast_template_wizard(self):

        response = self.client.get(reverse('website:add_forecast_template'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

        self.client.login(username='Joker', password='#ASDF20241')
        response = self.client.get(reverse('website:add_forecast_template'))
        self.assertEqual(response.status_code, 403)

        self.client.login(username='Batman', password='#ASDF2024')
        response = self.client.get(reverse('website:add_forecast_template'))
        self.assertEqual(response.status_code, 200)

        self.client.login(username='anton', password='#ASDF2023')
        response = self.client.get(reverse('website:add_forecast_template'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'website/template_wizard/f1.html')

        response = self.client.post(reverse('website:add_forecast_template'), {
            'f1-location': 1,
            'f1-forecast_source': 'yandex',
            'forecast_template_wizard-current_step': 'f1'
            })
        self.assertEqual(response.status_code, 200)

        self.assertInHTML(
            "Forecast template with this Forecast source and " +
            "Location already exists.",
            response.content.decode())

        response = self.client.post(reverse('website:add_forecast_template'), {
            'f1-location': 1,
            'f1-forecast_source': 'rp5',
            'forecast_template_wizard-current_step': 'f1'
            })
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('website:add_forecast_template'), {
            'f2-url': 'https://rp55.ru/foo',
            'forecast_template_wizard-current_step': 'f2'
            })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context['form'],
            'url', "This URL doesn’t belong to the Domain of the Forecast " +
            "Source you previously selected.")

        response = self.client.post(reverse('website:add_forecast_template'), {
            'f2-url': 'https://rp5.ru/Погода_в_Санкт-Петербурге',
            'forecast_template_wizard-current_step': 'f2'
            })
        self.assertEqual(response.status_code, 200)
        self.assertInHTML(
            "The Forecast Template is ready to be created.",
            response.content.decode())

        response = self.client.post(reverse('website:add_forecast_template'), {
            'forecast_template_wizard-current_step': 'f3'
            })
        self.assertEqual(response.status_code, 200)
        self.assertInHTML("Forecast Template successfully created.",
                          response.content.decode())


class ArchiveTemplateWizardTest(WebsiteTestBase):

    def setUp(self):
        Archive.objects.filter(archive_template__id=1).delete()
        ArchiveTemplate.objects.get(id=1).delete()

    def test_archive_template_wizard(self):

        response = self.client.get(reverse('website:add_archive_template'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

        self.client.login(username='Joker', password='#ASDF20241')
        response = self.client.get(reverse('website:add_archive_template'))
        self.assertEqual(response.status_code, 403)

        self.client.login(username='Batman', password='#ASDF2024')
        response = self.client.get(reverse('website:add_archive_template'))
        self.assertEqual(response.status_code, 200)

        self.client.login(username='anton', password='#ASDF2023')
        response = self.client.get(reverse('website:add_archive_template'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'website/template_wizard/a1.html')

        response = self.client.post(reverse('website:add_archive_template'), {
            'a1-location': 1,
            'a1-archive_source': 'rp5',
            'archive_template_wizard-current_step': 'a1'
            })
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('website:add_archive_template'), {
            'a2-url': 'https://rp55.ru/foo',
            'archive_template_wizard-current_step': 'a2'
            })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context['form'],
            'url', "This URL doesn’t belong to the Domain of the Archive " +
            "Source you previously selected.")

        response = self.client.post(reverse('website:add_archive_template'), {
            'a2-url': 'https://rp5.ru/Архив_погоды_в_Санкт-Петербурге',
            'archive_template_wizard-current_step': 'a2'
            })
        self.assertEqual(response.status_code, 200)
        self.assertInHTML(
            "The Archive Template is ready to be created.",
            response.content.decode())

        response = self.client.post(reverse('website:add_archive_template'), {
            'archive_template_wizard-current_step': 'a3'
            })
        self.assertEqual(response.status_code, 200)
        self.assertInHTML("Archive Template successfully created.",
                          response.content.decode())
