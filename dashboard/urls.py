from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('applications/', views.applications_view, name='applications'),
    path('applications/<int:application_id>/', views.application_detail_view, name='application_detail'),
    path('manage-staff/', views.manage_staff_view, name='manage_staff'),
    path('logs/', views.logs_view, name='logs'),
]