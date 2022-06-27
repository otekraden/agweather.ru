from django.urls import path

from . import views

urlpatterns = [
    # path('init_database/', views.init_database, name='init_database'),
    # path('scrapdata/', views.scrapdata, name='scrapdata'),
    path('', views.main, name='main'),

]