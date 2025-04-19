from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from social_django.models import UserSocialAuth
from social_django.utils import load_strategy
from social_core.backends.discord import DiscordOAuth2
from whitelist.models import WhitelistApplication
from jobs.models import JobApplication
from .utils import refresh_discord_token  # <-- import token refresh utility

def login_view(request):
    return render(request, 'accounts/login.html')

@login_required
def profile_view(request):
    try:
        discord_account = request.user.social_auth.get(provider='discord')

        # Refresh the token if needed
        access_token = refresh_discord_token(discord_account)

        # Get user info from Discord
        strategy = load_strategy(request)
        backend = DiscordOAuth2(strategy=strategy)
        user_info = backend.user_data(access_token)

        print("User Info from Discord API:")
        print(user_info)

        # Debug: Log the extra_data content
        print(f"extra_data: {discord_account.extra_data}")

        # Update user's Discord info
        request.user.discord_id = user_info.get('id')
        request.user.discord_username = user_info.get('username')
        request.user.discord_discriminator = user_info.get('discriminator')
        request.user.discord_avatar = user_info.get('avatar')
        request.user.save()

        print(f"Updated User: {request.user.discord_username}#{request.user.discord_discriminator}")

    except UserSocialAuth.DoesNotExist:
        messages.error(request, "Discord account not linked.")
    except Exception as e:
        messages.error(request, f"Error fetching Discord data: {e}")
        return render(request, "accounts/verify_discord.html")  # Optional fallback page

    # Whitelist application
    whitelist_application = WhitelistApplication.objects.filter(user=request.user).order_by('-created_at').first()

    # Job applications
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
