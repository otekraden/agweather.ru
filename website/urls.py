from django.urls import path

from . import views

app_name = "website"
urlpatterns = [
    path('', views.forecast, name='forecast'),
    # path('', views.IndexView.as_view(), name="index"),
]