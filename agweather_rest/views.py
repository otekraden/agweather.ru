from rest_framework import generics
from datascraper.models import Location
from .serializers import LocationSerializer


class LocationsAPIView(generics.ListAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
