from rest_framework import generics
from datascraper.models import Location
from .serializers import LocationSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from django.forms import model_to_dict
from rest_framework import viewsets
# from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAdminUser
from .permissions import IsAdminOrReadOnly, IsOwnerOrReadOnly


class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = (IsAdminOrReadOnly, IsOwnerOrReadOnly)
    # permission_classes = (IsAdminUser, )

# class LocationsAPIView(generics.ListAPIView):
#     queryset = Location.objects.all()
#     serializer_class = LocationSerializer

# class LocationsAPIView(APIView):
#     def get(self, request):
#         lst = Location.objects.all().values()
#         return Response({'locations': list(lst)})

#     def post(self, request):
#         post_new = Location.objects.create(
#             name=request.data['name'],
#             region=request.data['region'],
#             country=request.data['country'],
#         )
#         return Response({'post': model_to_dict(post_new)})