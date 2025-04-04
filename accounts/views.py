from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from social_django.models import UserSocialAuth
from whitelist.models import WhitelistApplication

def login_view(request):
    return render(request, 'accounts/login.html')

@login_required
def profile_view(request):
    try:
        discord_account = request.user.social_auth.get(provider='discord')
        extra_data = discord_account.extra_data
        
        # Update user's Discord info if needed
        if request.user.discord_id != extra_data.get('id'):
            request.user.discord_id = extra_data.get('id')
            request.user.discord_username = extra_data.get('username')
            request.user.discord_discriminator = extra_data.get('discriminator')
            request.user.discord_avatar = extra_data.get('avatar')
            request.user.save()
    except UserSocialAuth.DoesNotExist:
        pass
    
    # Get user's whitelist application if exists
    try:
        application = WhitelistApplication.objects.filter(user=request.user).latest('created_at')
    except WhitelistApplication.DoesNotExist:
        application = None
    
    context = {
        'application': application
    }
    
    return render(request, 'accounts/profile.html', context)

def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('home')