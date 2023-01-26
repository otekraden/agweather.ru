from datascraper.models import Location, ForecastTemplate, ArchiveTemplate
from .serializers import (
    LocationSerializer, ForecastTemplateSerializer, ArchiveTemplateSerializer)
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .permissions import IsOwnerOrReadOnly


class BaseDatascraperViewSet(viewsets.ModelViewSet):
    """Base serializer for datascraper models."""
    permission_classes = [IsAuthenticated & IsOwnerOrReadOnly | IsAdminUser]


class LocationViewSet(BaseDatascraperViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer


class ForecastTemplateViewSet(BaseDatascraperViewSet):
    queryset = ForecastTemplate.objects.all()
    serializer_class = ForecastTemplateSerializer


class ArchiveTemplateViewSet(BaseDatascraperViewSet):
    queryset = ArchiveTemplate.objects.all()
    serializer_class = ArchiveTemplateSerializer
