from django.contrib import admin
from .models import Profile


######################
# WEATHER PARAMETERS #
######################


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):

    list_display = ('user', 'bio', 'location', 'avatar')
    fields = ('user', 'bio', 'location', 'avatar')
    # readonly_fields = ('test',)

    # def test(self, obj):

    #     return obj.first_name
