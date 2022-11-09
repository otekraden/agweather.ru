from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from datascraper.models import (
    WeatherParameter, Location, ForecastTemplate, Forecast, ForecastSource,
    ArchiveTemplate, Archive)
from backports import zoneinfo
from django.utils import timezone
from datetime import timedelta, datetime
from django.contrib.auth.models import Group
from .forms import SignUpForm, EditProfileForm, EditUserForm
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from .tokens import account_activation_token
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth import get_user_model
from django.db import transaction
from django.contrib.auth.decorators import login_required
from .models import User, Profile


WEATHER_PARAMETERS = [
    f'{par.name}, {par.meas_unit}' for par in WeatherParameter.objects.all()]
LOCATIONS = tuple(map(str, Location.objects.all()))
FORECAST_SOURCES_URLS = [source.url for source in ForecastSource.objects.all()]
FORECAST_SOURCES_NAMES = [
    source.name for source in ForecastSource.objects.all()]


def forecast(request):

    if request.method == 'GET':
        # Default location Saint-Petersburg
        location = request.session.get('location', default_location(request))
        # Default show Temperature
        weather_parameter = request.session.get(
            'weather_parameter', WEATHER_PARAMETERS[0])
        # Default one week
        selection_period = request.session.get('selection_period', 7)

    elif request.method == 'POST':
        location = request.POST.get('location')
        request.session['location'] = location
        weather_parameter = request.POST.get('weather_parameter')
        request.session['weather_parameter'] = weather_parameter
        selection_period = request.POST.get('selection_period')
        request.session['selection_period'] = selection_period

    selection_period = check_int_input(selection_period, 1, 14, 7)
    forecast_length_steps = selection_period*24

    weather_parameter_index = WEATHER_PARAMETERS.index(weather_parameter)

    location_object = location_object_from_input(location)

    forecast_templates = ForecastTemplate.objects.filter(
        location=location_object)

    # Calculating start forecast datetime
    start_forecast_datetime = forecast_templates[0].start_forecast_datetime()

    # Generating datetime row
    datetime_row, datetime_ = [], start_forecast_datetime
    for step in range(forecast_length_steps):
        datetime_row.append(datetime_)
        datetime_ += timedelta(hours=1)

    # Tooltip titles for Chartjs
    tooltip_titles = [dt.strftime("%d.%m %H:%M") for dt in datetime_row]

    # Making datasets for Chartjs
    datasets = []
    for template in forecast_templates:

        forecasts = Forecast.objects.filter(
            scraped_datetime=template.last_scraped,
            forecast_template=template)

        if not forecasts or not forecasts[0].is_actual():
            continue

        forecast_data = []
        for datetime_ in datetime_row:
            try:
                forecast_record = forecasts.get(
                    forecast_datetime=datetime_).forecast_data[
                        weather_parameter_index]
            except (ObjectDoesNotExist, MultipleObjectsReturned):
                forecast_record = 'none'

            if not forecast_record and forecast_record != 0:
                forecast_record = 'none'

            forecast_data.append(forecast_record)

        datasets.append({
            'label': template.forecast_source.name,
            'data': forecast_data,
            'borderColor': template.forecast_source.chart_color,
            'backgroundColor': template.forecast_source.chart_color,
        })

    # For X axe in Chartjs
    labels = [i.strftime("%a") if i.hour == 12 else ' '
              if i.hour == 0 else ''
              for i in datetime_row]

    chartjs_data = {
        'labels': labels,
        'datasets': datasets,
    }

    last_database_refresh = ForecastTemplate.objects.latest(
        'last_scraped').last_scraped.strftime(
            "Database updated:  %d.%m.%Y %H:%M UTC")

    scales_list = ((-5, 5), (755, 765), (0, 10))
    chartjs_options = {'suggestedMin': scales_list[weather_parameter_index][0],
                       'suggestedMax': scales_list[weather_parameter_index][1],
                       'tooltip_titles': tooltip_titles,
                       'last_database_refresh': last_database_refresh,
                       }

    context = {
        'locations': LOCATIONS,
        'location': location,
        'weather_parameters': WEATHER_PARAMETERS,
        'weather_parameter': weather_parameter,
        'selection_period': selection_period,
        'chartjs_options': chartjs_options,
        'chartjs_data': chartjs_data,
        'forecast_sources': zip(FORECAST_SOURCES_NAMES, FORECAST_SOURCES_URLS),
        'timezone': start_forecast_datetime.tzinfo,
        }

    return render(
        request=request,
        template_name='website/forecast.html',
        context=context)


def archive(request):
    """View"""

    if request.method == 'GET':
        # Default location Saint-Petersburg
        location = request.session.get('location', default_location(request))
        # Default show Temperature
        weather_parameter = request.session.get(
            'weather_parameter', WEATHER_PARAMETERS[0])
        # Default one week
        selection_period = request.session.get('selection_period', 7)
        # Default 24h
        prediction_range = 24
        # Default today
        period_end_date = datetime.now().strftime("%d/%m/%Y")

    elif request.method == 'POST':
        location = request.POST.get('location')
        request.session['location'] = location
        weather_parameter = request.POST.get('weather_parameter')
        request.session['weather_parameter'] = weather_parameter
        selection_period = request.POST.get('selection_period')
        request.session['selection_period'] = selection_period
        period_end_date = request.POST.get('period_end_date')
        prediction_range = request.POST.get('prediction_range')

    selection_period = check_int_input(selection_period, 1, 30, 14)
    archive_length_steps = selection_period*24

    prediction_range = check_int_input(prediction_range, 1, 336, 1)

    weather_parameter_index = WEATHER_PARAMETERS.index(weather_parameter)

    location_object = location_object_from_input(location)
    archive_templates = ArchiveTemplate.objects.filter(
        location=location_object)
    forecast_templates = ForecastTemplate.objects.filter(
        location=location_object)

    # Getting local datetime at archive location
    timezone_info = zoneinfo.ZoneInfo(location_object.timezone)
    # local_date = timezone.localdate(timezone=timezone_info)

    # Calculating end archive datetime
    end_archive_datetime = tuple(map(int, period_end_date.split('/')))
    end_archive_datetime = timezone.datetime(
        end_archive_datetime[2],
        end_archive_datetime[1],
        end_archive_datetime[0],
        tzinfo=timezone_info) + timedelta(1)

    datetime_row, datetime_ = [], end_archive_datetime
    for step in range(archive_length_steps):
        datetime_row.append(datetime_)
        datetime_ -= timedelta(hours=1)
    datetime_row.reverse()

    tooltip_titles = [dt.strftime("%a %H:%M") for dt in datetime_row]

    labels = [i.strftime("%d.%m") if i.hour == 12 else ' ' if i.hour ==
              0 else '' for i in datetime_row]  # Ярлыки оси Х для графика

    # Making datasets for Chartjs
    datasets = []
    for template in archive_templates:

        archive_data = []
        for datetime_ in datetime_row:
            try:
                archive_record = Archive.objects.get(
                    archive_template=template,
                    record_datetime=datetime_).data_json[
                        weather_parameter_index]
            except (ObjectDoesNotExist, MultipleObjectsReturned):
                archive_record = 'none'

            if not archive_record and archive_record != 0:
                archive_record = 'none'

            archive_data.append(archive_record)

        datasets.append({
            'label': f'Archive_{template.archive_source.name}',
            'data': archive_data,
            'borderColor': template.archive_source.chart_color,
            'borderWidth': 1,
            'pointStyle': 'circle',
            'pointRadius': 3,
            'pointHoverRadius': 10,
        })

    for template in forecast_templates:

        forecasts = Forecast.objects.filter(
            forecast_template=template,
            prediction_range_hours=prediction_range,
            forecast_datetime__range=(datetime_row[0], datetime_row[-1]))

        if not forecasts:
            # prediction_range += 1
            continue

        forecast_data = []
        for datetime_ in datetime_row:
            try:
                forecast_record = forecasts.get(
                    forecast_datetime=datetime_).forecast_data[
                        weather_parameter_index]
            except (ObjectDoesNotExist, MultipleObjectsReturned):
                forecast_record = 'none'

            if not forecast_record and forecast_record != 0:
                forecast_record = 'none'

            forecast_data.append(forecast_record)

        datasets.append({
            'label': template.forecast_source.name,
            'data': forecast_data,
            'borderColor': template.forecast_source.chart_color,
            'backgroundColor': template.forecast_source.chart_color,
            'borderWidth': 0,
            'pointStyle': 'triangle',
            'pointRadius': 6,
            'pointHoverRadius': 12,
        })

    chartjs_data = {
        'labels': labels,
        'datasets': datasets,
    }

    last_database_refresh = ForecastTemplate.objects.latest(
        'last_scraped').last_scraped.strftime(
            "Database updated:  %d.%m.%Y %H:%M UTC")

    scales_list = ((-5, 5), (755, 765), (0, 10))
    chartjs_options = {'suggestedMin': scales_list[weather_parameter_index][0],
                       'suggestedMax': scales_list[weather_parameter_index][1],
                       'tooltip_titles': tooltip_titles,
                       'last_database_refresh': last_database_refresh,
                       }

    context = {
        'locations': LOCATIONS,
        'location': location,
        'weather_parameters': WEATHER_PARAMETERS,
        'weather_parameter': weather_parameter,
        'selection_period': selection_period,
        'period_end_date': period_end_date,
        'prediction_range': prediction_range,
        'chartjs_data': chartjs_data,
        'chartjs_options': chartjs_options,
        'forecast_sources': zip(FORECAST_SOURCES_NAMES, FORECAST_SOURCES_URLS),
        'timezone': timezone_info,
    }

    return render(
        request=request, template_name='website/archive.html', context=context)

########
# MISC #
########


def location_object_from_input(location):
    location_string = location.split(', ')
    return Location.objects.get(
        name=location_string[0],
        region=location_string[1],
        country=location_string[2])


def check_int_input(value, min, max, default):
    value = default if value == '' else int(value)
    if value > max:
        value = max
    elif value < min:
        value = min
    return value


def default_location(request):
    if request.user.is_authenticated:
        return str(Profile.objects.get(
            user=request.user).favorite_location)
    return LOCATIONS[1]

##################
# AUTHENTICATION #
##################


@transaction.atomic
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            group = Group.objects.get(name='Test Group')
            group.user_set.add(user)

            current_site = get_current_site(request)
            subject = 'AGWeather Account Activation Link'
            message = render_to_string(
                'website/account_activation_email.html',
                {'user': user,
                 'domain': current_site.domain,
                 'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                 'token': account_activation_token.make_token(user),
                 })
            print(message)
            user.email_user(subject, message)

            return render(request, 'website/account_activation_sent.html')
    else:
        return render(request, 'website/signup.html')

    return render(request, 'website/signup.html', {'form': form})


def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        return render(request, 'website/account_activation_complete.html')
    else:
        return render(request, 'website/account_activation_error.html')


@login_required
def profile(request):
    user = get_object_or_404(User, username=request.user.username)
    profile = get_object_or_404(Profile, user=user)
    return render(request, 'website/user_profile.html',
                  {'profile': profile, 'user': user})


@login_required
def edit_user_profile(request):
    user = get_object_or_404(User, username=request.user.username)
    profile = get_object_or_404(Profile, user=user)

    if request.method == 'POST':
        user_form = EditUserForm(request.POST, instance=user)
        profile_form = EditProfileForm(
            request.POST, request.FILES, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('website:profile')

    elif request.method == 'GET':
        user_form = EditUserForm(instance=user)
        profile_form = EditProfileForm(instance=profile)

    return render(request, 'website/edit_user_profile.html',
                  {'user_form': user_form, 'profile_form': profile_form,
                   'locations': LOCATIONS,
                   'avatar': profile.avatar.url, })
