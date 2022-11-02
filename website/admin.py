from django.contrib import admin
from .models import Profile


######################
# WEATHER PARAMETERS #
######################


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):

    list_display = ('bio', 'location', 'birth_date') #, 'test')
    fields = ('bio', 'location', 'birth_date') #, 'test')
    # readonly_fields = ('test',)

    # def test(self, obj):

    #     return obj.first_name
