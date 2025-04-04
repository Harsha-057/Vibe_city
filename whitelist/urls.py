from django.urls import path
from . import views

urlpatterns = [
    path('apply/', views.apply_view, name='whitelist_apply'),
    path('success/', views.success_view, name='whitelist_success'),
]