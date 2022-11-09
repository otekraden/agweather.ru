from django.contrib import admin
from .models import Profile


################
# USER PROFILE #
################


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):

    list_display = ('user', 'favorite_location', 'avatar')
    fields = ('user', 'about_me', 'favorite_location', 'avatar')
    # readonly_fields = ('test',)

    # def test(self, obj):

    #     return obj.first_name
