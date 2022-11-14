from django.urls import path
# from django.contrib import admin
# from website.views import signup

from . import views

app_name = "user_profile"
urlpatterns = [
    path('signup/', views.signup, name="signup"),
    path('activate/(<uidb64>/<token>', views.activate, name='activate'),
    path('profile/<slug:username>', views.profile, name='profile'),
    path('edit_profile/<slug:username>', views.edit_user_profile,
         name='edit_user_profile'),
]