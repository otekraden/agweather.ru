from django.urls import path
from . import views

app_name = "forum"
urlpatterns = [
     path('', views.TopicListView.as_view(), name='forum-index'),
     path('topic/add/', views.TopicCreateView.as_view(), name='topic-add'),
     path('topic/<int:pk>/', views.TopicDetailView.as_view(),
         name='topic-detail'),
     path('topic/<int:pk>/newpost/', views.PostCreateView.as_view(),
         name='post-create'),
     path('post/<int:pk>/update/', views.PostUpdateView.as_view(),
         name='post-update'),
     path('post/<int:pk>/delete/', views.PostDeleteView.as_view(),
         name='post-delete'),
]
