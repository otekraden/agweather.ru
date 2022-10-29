from django.contrib import admin
from .models import Profile


######################
# WEATHER PARAMETERS #
######################


@admin.register(Profile)
class WeatherParameterAdmin(admin.ModelAdmin):

    list_display = ('user', 'first_name', 'last_name', 'email')
    fields = ('first_name', 'last_name', 'email', 'bio')
