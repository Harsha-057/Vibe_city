from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import WhitelistApplication
from whitelist.forms import WhitelistApplicationForm
from discord_bot.bot import send_application_notification, bot, bot_ready
from django.conf import settings
import asyncio





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
    
    # Check if user is in Discord server
    if not request.user.discord_id:
        messages.error(request, "Please link your Discord account before applying for whitelist.")
        return redirect('profile')
    
    # Wait for bot to be ready
    if not bot_ready.is_set():
        bot_ready.wait(timeout=10)
        if not bot_ready.is_set():
            messages.error(request, "Discord bot is not ready. Please try again later.")
            return redirect('profile')
    
    # Check if user is in the Discord server
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
    
    # Run the async check in the bot's event loop
    try:
        is_in_server = asyncio.run_coroutine_threadsafe(check_discord_membership(), bot.loop).result(timeout=10)
    except Exception as e:
        print(f"Error running Discord membership check: {e}")
        messages.error(request, "Error checking Discord membership. Please try again later.")
        return redirect('profile')
    
    if not is_in_server:
        messages.error(request, "You must be a member of our Discord server to apply for whitelist.")
        return redirect('https://discord.gg/7t6wRdnukV')
    
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