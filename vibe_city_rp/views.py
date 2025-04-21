from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from jobs.models import JobApplication

def home(request):
    """Render the home page."""
    return render(request, 'home.html')

def rules(request):
    """Render the rules page."""
    return render(request, 'rules.html')

def terms_of_service(request):
    """Render the Terms of Service page."""
    return render(request, 'legal/terms_of_service.html')

def privacy_policy(request):
    """Render the Privacy Policy page."""
    return render(request, 'legal/privacy_policy.html')

def server_info(request):
    """Render the server information page."""
    return render(request, 'server_info.html') 