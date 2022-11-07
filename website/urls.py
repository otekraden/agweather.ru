from django.urls import path
# from django.contrib import admin
# from website.views import signup

from . import views

app_name = "website"
urlpatterns = [
    path('', views.forecast, name='forecast'),
    path('forecast/', views.forecast, name="forecast"),
    path('archive/', views.archive, name="archive"),
    path('signup/', views.signup, name="signup"),
    path('activate/(<uidb64>/<token>', views.activate, name='activate'),
    path('profile/<username>/', views.profile, name='profile'),
]
