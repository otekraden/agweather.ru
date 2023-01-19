from datascraper.models import ForecastSource
from user_profile.models import Profile, User


def add_variable_to_context(request):
    """Permanent context data for all views."""

    # forecast sources dropdown list
    context_add = {
            'forecast_sources': ForecastSource.dropdown_list(), }

    # user avatar image url
    username = request.user.username
    if username:
        user = User.objects.get(username=username)
        profile = Profile.objects.get(user=user)
        context_add['user_profile_avatar'] = profile.avatar.url

    return context_add
