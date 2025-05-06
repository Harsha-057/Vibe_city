from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import WhitelistApplication
from whitelist.forms import WhitelistApplicationForm
from discord_bot.bot import send_application_notification, bot, bot_ready
from django.conf import settings
import asyncio
import discord





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
            if not bot:
                print("Bot is not initialized")
                return False
                
            guild_id = int(settings.DISCORD_GUILD_ID)
            if not guild_id:
                print("DISCORD_GUILD_ID is not set")
                return False
                
            guild = bot.get_guild(guild_id)
            if not guild:
                print(f"Guild not found with ID: {guild_id}")
                return False
            
            user_discord_id = int(request.user.discord_id)
            if not user_discord_id:
                print("User's Discord ID is not set")
                return False
                
            member = await guild.fetch_member(user_discord_id)
            if not member:
                print(f"Member not found in guild with ID: {user_discord_id}")
                return False
                
            return True
        except ValueError as e:
            print(f"Invalid ID format: {e}")
            return False
        except discord.Forbidden as e:
            print(f"Bot lacks permissions to fetch guild members: {e}")
            return False
        except discord.HTTPException as e:
            print(f"Discord API error: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error checking Discord membership: {e}")
            return False
    
    # Run the async check in the bot's event loop
    try:
        is_in_server = asyncio.run_coroutine_threadsafe(check_discord_membership(), bot.loop).result(timeout=10)
    except Exception as e:
        print(f"Error running Discord membership check: {e}")
        is_in_server = False
    
    if not is_in_server:
        discord_invite_link = "https://discord.gg/7t6wRdnukV"
        return render(request, 'whitelist/join_discord.html', {'discord_invite_link': discord_invite_link})
    
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