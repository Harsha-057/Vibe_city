from django.urls import path
from . import views

app_name = 'guidebook'

urlpatterns = [
    path('', views.GuidebookListView.as_view(), name='list'),
    path('<int:pk>/', views.GuidebookDetailView.as_view(), name='detail'),
] 