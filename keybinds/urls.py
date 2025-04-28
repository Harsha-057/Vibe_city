from django.urls import path
from . import views

app_name = 'keybinds'

urlpatterns = [
    path('', views.keybinds_view, name='list'),
] 