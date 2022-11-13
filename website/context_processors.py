from datascraper.models import ForecastSource
from django.contrib.auth import get_user_model
from user_profile.models import Profile


def add_variable_to_context(request):

    # profile = Profile.objects.get(user=get_user_model().id)

    return {
        'forecast_sources': ForecastSource.dropdown_list(),
        # 'user_profile_avatar': profile.avatar.url,
    }
