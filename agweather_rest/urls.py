from django.urls import path
from agweather_rest.views import LocationsAPIView


urlpatterns = [
    path('v1/locationslist', LocationsAPIView.as_view()),
]
