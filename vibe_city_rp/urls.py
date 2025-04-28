from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('rules/', views.rules, name='rules'),
    path('accounts/', include('accounts.urls')),
    path('whitelist/', include('whitelist.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('social-auth/', include('social_django.urls', namespace='social')),
    path('jobs/', include('jobs.urls')),
    path('guidebook/', include('guidebook.urls')),
    path('keybinds/', include('keybinds.urls')),
    path('terms-of-service/', views.terms_of_service, name='terms_of_service'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('server-info/', views.server_info, name='server_info'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)