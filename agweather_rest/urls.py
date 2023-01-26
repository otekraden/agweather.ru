from django.urls import path, include
from agweather_rest.views import LocationViewSet
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'location', LocationViewSet)

urlpatterns = [
    path('v1/', include(router.urls)),
]
