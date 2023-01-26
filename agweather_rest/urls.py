from django.urls import path, include
from agweather_rest.views import (
    LocationViewSet, ForecastTemplateViewSet, ArchiveTemplateViewSet)
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'location', LocationViewSet)
router.register(r'forecast_template', ForecastTemplateViewSet)
router.register(r'archive_template', ArchiveTemplateViewSet)

urlpatterns = [
    path('v1/', include(router.urls)),
]
