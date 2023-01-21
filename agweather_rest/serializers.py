from rest_framework import serializers
from datascraper.models import Location


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ('name', 'region', 'country', 'timezone')