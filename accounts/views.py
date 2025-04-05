from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from social_django.models import UserSocialAuth
from social_django.utils import load_strategy
from social_core.backends.discord import DiscordOAuth2
from whitelist.models import WhitelistApplication
from jobs.models import JobApplication

def login_view(request):
    return render(request, 'accounts/login.html')

@login_required
def profile_view(request):
    try:
        discord_account = request.user.social_auth.get(provider='discord')
        extra_data = discord_account.extra_data
        strategy = load_strategy(request)
        backend = DiscordOAuth2(strategy=strategy)
        user_info = backend.user_data(discord_account.extra_data['access_token'])

        print("User Info from Discord API:")
        print(user_info)
        
        # Debugging: Log the extra_data content
        print(f"extra_data: {extra_data}")
        
        # Debugging: Log the data before saving
        print(f"Before Save: ID={request.user.discord_id}, Username={request.user.discord_username}, Discriminator={request.user.discord_discriminator}, Avatar={request.user.discord_avatar}")
        
        # Update user's Discord info if needed
        request.user.discord_id = user_info.get('id')
        request.user.discord_username = user_info.get('username')
        request.user.discord_discriminator = user_info.get('discriminator')
        request.user.discord_avatar = user_info.get('avatar')
        request.user.save()
            
            # Debugging: Log the data after saving
        print(f"After Save: ID={request.user.discord_id}, Username={request.user.discord_username}, Discriminator={request.user.discord_discriminator}, Avatar={request.user.discord_avatar}")
    except UserSocialAuth.DoesNotExist:
        pass
    
    # Get user's latest whitelist application if exists
    whitelist_application = None
    try:
        whitelist_application = WhitelistApplication.objects.filter(user=request.user).latest('created_at')
    except WhitelistApplication.DoesNotExist:
        pass
    
    # Get user's job applications (order by submission date)
    user_job_applications = JobApplication.objects.filter(applicant=request.user).order_by('-submitted_at')
    
    context = {
        'whitelist_application': whitelist_application,
        'job_applications': user_job_applications,
    }
    
    return render(request, 'accounts/profile.html', context)

def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('home')