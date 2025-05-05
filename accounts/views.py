from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from social_django.models import UserSocialAuth
from social_django.utils import load_strategy
from social_core.backends.discord import DiscordOAuth2
from whitelist.models import WhitelistApplication
from jobs.models import JobApplication
from .utils import refresh_discord_token
from discord_bot.bot import bot, bot_ready
from django.conf import settings
import asyncio

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
        # Update user's Discord info
        request.user.discord_id = user_info.get('id')
        request.user.discord_username = user_info.get('username')
        request.user.discord_discriminator = user_info.get('discriminator')
        request.user.discord_avatar = user_info.get('avatar')
        request.user.save()

        # Only check Discord membership if bot is ready
        if not bot_ready.is_set():
            messages.error(request, "Discord bot is not ready. Please try again later.")
            return render(request, 'accounts/profile.html', context={})

        async def check_discord_membership():
            try:
                guild = bot.get_guild(int(settings.DISCORD_GUILD_ID))
                if not guild:
                    return False
                member = await guild.fetch_member(int(request.user.discord_id))
                return member is not None
            except Exception as e:
                print(f"Error checking Discord membership: {e}")
                return False

        try:
            is_in_server = asyncio.run_coroutine_threadsafe(
                check_discord_membership(), bot.loop
            ).result(timeout=5)  # Reduce timeout for faster feedback
        except Exception as e:
            print(f"Error running Discord membership check: {e}")
            messages.error(request, "Error checking Discord membership. Please try again later.")
            return render(request, 'accounts/profile.html', context={})

        if not is_in_server:
            return render(request, 'accounts/join_discord.html')

    except UserSocialAuth.DoesNotExist:
        return render(request, 'accounts/verify_discord.html')
    except Exception as e:
        print(f"Error in profile view: {e}")
        messages.error(request, "There was an error processing your Discord account. Please try again.")
        return render(request, 'accounts/verify_discord.html')

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
