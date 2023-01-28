from datascraper.models import (
    Location, ForecastTemplate, ArchiveTemplate, Forecast)
from .serializers import (
    LocationSerializer, ForecastTemplateSerializer, ArchiveTemplateSerializer)
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .permissions import IsOwnerOrReadOnly
from rest_framework.views import APIView
from rest_framework.response import Response
from website.views import check_int_input, WEATHER_PARAMETERS
from datetime import timedelta, datetime
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned


class BaseDatascraperViewSet(viewsets.ModelViewSet):
    """Base view set for datascraper models."""
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


class ForecastAPIView(APIView):
    """Main view. Weather forecasts."""
    def get(self, request):

        # Default location Saint-Petersburg
        location = Location.objects.get(
            id=request.query_params.get("location_id", 1))
        # Default show Temperature
        weather_parameter_index = int(request.query_params.get(
            "weather_parameter_index", 1))
        # Default period is one week
        selection_period = check_int_input(
            request.query_params.get('selection_period', ''), 1, 14, 7)
        forecast_length_steps = selection_period*24

        forecast_templates = ForecastTemplate.objects.filter(
            location=location)

        # Calculating start forecast datetime
        start_forecast_datetime = \
            forecast_templates[0].location.start_forecast_datetime()

        # Generating datetime row
        datetime_row, datetime_ = [], start_forecast_datetime
        for step in range(forecast_length_steps):
            datetime_row.append(datetime_)
            datetime_ += timedelta(hours=1)

        # Making datasets
        datasets = []
        for template in forecast_templates:

            forecasts = Forecast.objects.filter(
                scraped_datetime=template.last_scraped,
                forecast_template=template)

            if not forecasts or not forecasts[0].is_actual():
                continue

            forecast_data = []
            for datetime_ in datetime_row:
                try:
                    forecast_record = forecasts.get(
                        forecast_datetime=datetime_).forecast_data[
                            weather_parameter_index]
                except (ObjectDoesNotExist, MultipleObjectsReturned):
                    forecast_record = None

                if not forecast_record and forecast_record != 0:
                    forecast_record = None

                forecast_data.append(forecast_record)

            datasets.append({
                'forecast_source': template.forecast_source.name,
                'data': forecast_data,
            })

        return Response({'location': str(location),
                         'weather_parameter': WEATHER_PARAMETERS[
                             weather_parameter_index],
                         'selection_period_days': selection_period,
                         'datetime_row': datetime_row,
                         'forecasts': datasets})

        # def get_queryset(self):
        # location_id = self.request.query_params.get("location_id", None)
        # # location_id = self.kwargs["location_id"]
        # print(self.request.query_params)
        # for i in self.request.__dict__:
        #     print(i)
        # if location_id:
        #     qs = Location.objects.filter(id=location_id)
        #     return qs

        # return super().get_queryset()