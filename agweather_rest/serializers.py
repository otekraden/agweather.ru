from rest_framework import serializers
from datascraper.models import Location


class LocationSerializer(serializers.ModelSerializer):
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Location
        fields = '__all__'
        # fields = ('name', 'region', 'country', 'timezone')
