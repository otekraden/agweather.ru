from rest_framework import serializers
from datascraper.models import Location, ForecastTemplate, ArchiveTemplate


class BaseDatascraperSerializer(serializers.ModelSerializer):
    """Base serializer for datascraper models."""
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())


class LocationSerializer(BaseDatascraperSerializer):
    class Meta:
        model = Location
        fields = ('name', 'region', 'country', 'timezone', 'author')


class ForecastTemplateSerializer(BaseDatascraperSerializer):
    class Meta:
        model = ForecastTemplate
        fields = '__all__'


class ArchiveTemplateSerializer(BaseDatascraperSerializer):
    class Meta:
        model = ArchiveTemplate
        fields = '__all__'
