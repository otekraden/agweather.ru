from datascraper.models import ForecastSource
from user_profile.models import Profile, User


def add_variable_to_context(request):

    context_add = {
            'forecast_sources': ForecastSource.dropdown_list(), }

    username = request.user.username
    if username:
        user = User.objects.get(username=username)
        profile = Profile.objects.get(user=user)
        context_add['user_profile_avatar'] = profile.avatar.url

    return context_add
