from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import WhitelistApplication
from whitelist.forms import WhitelistApplicationForm
from discord_bot.bot import send_application_notification

@login_required
def apply_view(request):
    # Check if user already has a pending application
    existing_application = WhitelistApplication.objects.filter(
        user=request.user, 
        status='pending'
    ).first()
    
    if existing_application:
        messages.warning(request, "You already have a pending application. Please wait for it to be reviewed.")
        return redirect('profile')
    
    # Check if user is already whitelisted
    if request.user.is_whitelisted:
        messages.info(request, "You are already whitelisted on the server!")
        return redirect('profile')
    
    if request.method == 'POST':
        form = WhitelistApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user
            application.save()
            
            # Send Discord notification
            try:
                send_application_notification(application)
                messages.success(request, "Your application has been submitted successfully! You will be notified when it's reviewed.")
            except Exception as e:
                print(f"Error sending Discord notification: {e}")
                messages.success(request, "Your application has been submitted successfully! You will be notified when it's reviewed.")
            
            return redirect('whitelist_success')
    else:
        form = WhitelistApplicationForm()
    
    return render(request, 'whitelist/apply.html', {'form': form})

@login_required
def success_view(request):
    return render(request, 'whitelist/success.html')