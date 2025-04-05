import discord
from discord.ext import commands
import asyncio
import os
from django.conf import settings
import threading
from asgiref.sync import sync_to_async

# Global bot instance
bot = None
bot_ready = threading.Event()

class VibeCity(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        
        super().__init__(command_prefix='!', intents=intents)
    
    async def on_ready(self):
        print(f'Logged in as {self.user.name} ({self.user.id})')
        bot_ready.set()

def run_bot():
    global bot
    bot = VibeCity()
    
    @bot.command(name='ping')
    async def ping(ctx):
        await ctx.send('Pong!')
    
    bot.run(settings.DISCORD_BOT_TOKEN)

# Start the bot in a separate thread
def start_bot():
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()

# Initialize the bot when Django starts
start_bot()

# Helper functions to send notifications
def send_application_notification(application):
    if not bot_ready.is_set():
        print("Bot not ready yet, waiting...")
        bot_ready.wait(timeout=10)
    
    if not bot:
        print("Bot not initialized")
        return
    
    async def send():
        try:
            channel = bot.get_channel(int(settings.DISCORD_APPLICATIONS_CHANNEL_ID))
            if not channel:
                print(f"Channel not found: {settings.DISCORD_APPLICATIONS_CHANNEL_ID}")
                return
            
            embed = discord.Embed(
                title="New Whitelist Application Submitted",
                description=f"A new application has been submitted by {application.user.discord_tag}",
                color=discord.Color.blue()
            )
            
            embed.add_field(name="Applicant", value=f"<@{application.user.discord_id}> ({application.user.discord_tag})", inline=True)
            embed.add_field(name="Age", value=str(application.age), inline=True)
            embed.add_field(name="Submitted At", value=application.created_at.strftime("%Y-%m-%d %H:%M UTC"), inline=True)
            embed.add_field(name="Status", value="Pending Review", inline=True)
            embed.add_field(name="Application ID", value=application.id, inline=True)
            
            embed.set_thumbnail(url=application.user.avatar_url)
            # TODO: Replace with your desired image URL for new applications
            # embed.set_image(url="YOUR_SERVER_BANNER_OR_LOGO_URL") 
            embed.set_footer(text="Review this application in the staff dashboard")
            
            await channel.send(embed=embed)
        except Exception as e:
            print(f"Error sending application notification: {e}")
    
    asyncio.run_coroutine_threadsafe(send(), bot.loop)

def send_application_result(application):
    if not bot_ready.is_set():
        print("Bot not ready yet, waiting...")
        bot_ready.wait(timeout=10)
    
    if not bot:
        print("Bot not initialized")
        return
    
    async def send():
        try:
            # Send to notifications channel
            channel = bot.get_channel(int(settings.DISCORD_NOTIFICATIONS_CHANNEL_ID))
            if not channel:
                print(f"Channel not found: {settings.DISCORD_NOTIFICATIONS_CHANNEL_ID}")
                return
            
            status_color = discord.Color.green() if application.status == 'approved' else discord.Color.red()
            status_text = "APPROVED" if application.status == 'approved' else "REJECTED"
            
            embed = discord.Embed(
                title=f"Whitelist Application {status_text}",
                description=f"{application.user.username}'s whitelist application has been {application.status}.",
                color=status_color
            )
            
            embed.add_field(name="Applicant", value=f"<@{application.user.discord_id}>", inline=True)
            embed.add_field(name="Reviewed By", value=f"<@{application.reviewed_by.discord_id}> ({application.reviewed_by.discord_tag})" if application.reviewed_by.discord_id else application.reviewed_by.username, inline=True)
            embed.add_field(name="Reviewed At", value=application.reviewed_at.strftime("%Y-%m-%d %H:%M UTC"), inline=True)
            
            embed.set_thumbnail(url=application.user.avatar_url)
            
            # Set image based on status
            if application.status == 'approved':
                # TODO: Replace with your approval image URL
                embed.set_image(url="https://media.discordapp.net/attachments/1274763426866008234/1358112763691663529/20250327_174238.png?ex=67f2a893&is=67f15713&hm=6e8175f3b658e284d8a24d09a036bb462220c031d4090ba3776156087539236d&=&format=webp&quality=lossless&width=778&height=778")
                pass # Placeholder if no image URL yet
            else:
                # TODO: Replace with your rejection image URL
                # embed.set_image(url="YOUR_REJECTION_IMAGE_URL")
                pass # Placeholder if no image URL yet

            # Mention the user in the channel message content
            await channel.send(content=f"Status update for <@{application.user.discord_id}>:", embed=embed)
            
            # Assign whitelist role if approved
            if application.status == 'approved':
                try:
                    guild = bot.get_guild(int(settings.DISCORD_GUILD_ID))
                    if not guild:
                        print(f"Guild not found: {settings.DISCORD_GUILD_ID}")
                        return
                    
                    member = await guild.fetch_member(int(application.user.discord_id))
                    if not member:
                        print(f"Member not found: {application.user.discord_id}")
                        return
                    
                    whitelist_role = guild.get_role(int(settings.DISCORD_WHITELIST_ROLE_ID))
                    if not whitelist_role:
                        print(f"Whitelist role not found: {settings.DISCORD_WHITELIST_ROLE_ID}")
                        return
                    await member.add_roles(whitelist_role)
                    print(f"Assigned whitelist role to {member.display_name}")
                except Exception as e:
                    print(f"Error assigning whitelist role: {e}")
            
            # DM the user
            try:
                guild = bot.get_guild(int(settings.DISCORD_GUILD_ID))
                if not guild:
                    print(f"Guild not found: {settings.DISCORD_GUILD_ID}")
                    return
                
                member = await guild.fetch_member(int(application.user.discord_id))
                if not member:
                    print(f"Member not found: {application.user.discord_id}")
                    return
                
                dm_embed = discord.Embed(
                    title=f"Your Whitelist Application Has Been {status_text}",
                    color=status_color
                )
                
                if application.status == 'approved':
                    dm_embed.description = f"Congratulations! Your application for Vibe City RP has been approved."
                    dm_embed.add_field(name="Next Steps", value="You have been granted the Whitelisted role in Discord. Please familiarize yourself with server rules and connect to the server!", inline=False)
                else:
                    dm_embed.description = f"We regret to inform you that your whitelist application for Vibe City RP has been rejected."
                    dm_embed.add_field(name="Reason/Feedback", value=application.feedback or "No specific feedback provided.", inline=False)
                    dm_embed.add_field(name="What Next?", value="You may be able to reapply after a cooldown period. Please review the rejection feedback carefully.", inline=False)
                
                if application.status == 'approved' and application.feedback:
                     dm_embed.add_field(name="Additional Comments", value=application.feedback, inline=False)

                dm_embed.set_footer(text=f"Application ID: {application.id}")
                
                # Set image based on status for DM
                if application.status == 'approved':
                    # TODO: Replace with your approval image URL
                    # dm_embed.set_image(url="YOUR_APPROVAL_IMAGE_URL")
                    pass # Placeholder if no image URL yet
                else:
                    # TODO: Replace with your rejection image URL
                    # dm_embed.set_image(url="YOUR_REJECTION_IMAGE_URL")
                    pass # Placeholder if no image URL yet

                await member.send(embed=dm_embed)
            except Exception as e:
                print(f"Error sending DM to user: {e}")
        
        except Exception as e:
            print(f"Error sending application result notification: {e}")
    
    asyncio.run_coroutine_threadsafe(send(), bot.loop)

def send_job_application_result(application):
    """Sends notification about job application results to channel and DM."""
    print(f"[JobAppNotify-{application.id}] Received request to notify.") # DEBUG
    if not bot_ready.is_set():
        print(f"[JobAppNotify-{application.id}] Bot not ready, waiting...")
        bot_ready.wait(timeout=15) # Increased timeout
        if not bot_ready.is_set():
            print(f"[JobAppNotify-{application.id}] Bot did not become ready after wait.")
            return
        print(f"[JobAppNotify-{application.id}] Bot became ready after wait.") # DEBUG

    if not bot:
        print(f"[JobAppNotify-{application.id}] Bot object is None.")
        return
    
    if not bot.loop.is_running():
         print(f"[JobAppNotify-{application.id}] Bot event loop is not running. Cannot schedule notification.")
         return

    async def send():
        print(f"[JobAppNotify-{application.id}] Entering async send() coroutine.") 
        try:
            # Wrap ORM access in sync_to_async
            applicant_obj = await sync_to_async(lambda: application.applicant)()
            reviewer_obj = await sync_to_async(lambda: application.reviewer)()
            
            if not applicant_obj:
                print(f"[JobAppNotify-{application.id}] Application has no applicant.")
                return
            print(f"[JobAppNotify-{application.id}] Applicant found: {applicant_obj.username} ({applicant_obj.id})") 
            
            applicant_discord_tag = await sync_to_async(lambda: applicant_obj.discord_tag)()
            applicant_username = await sync_to_async(lambda: applicant_obj.username)()
            applicant_discord_id = await sync_to_async(lambda: applicant_obj.discord_id)()

            reviewer_discord_tag = None
            reviewer_username = None
            if reviewer_obj:
                 reviewer_discord_tag = await sync_to_async(lambda: reviewer_obj.discord_tag)()
                 reviewer_username = await sync_to_async(lambda: reviewer_obj.username)()

            # --- Send to Notifications Channel --- #
            try:
                channel_id = int(settings.DISCORD_NOTIFICATIONS_CHANNEL_ID)
                # bot.get_channel is async safe
                channel = bot.get_channel(channel_id)
                if not channel:
                    print(f"[JobAppNotify-{application.id}] Channel not found: {channel_id}")
                else:
                    status_color = discord.Color.green() if application.status == 'APPROVED' else discord.Color.red()
                    status_text = "APPROVED" if application.status == 'APPROVED' else "REJECTED"
                    
                    # Access simple fields directly, related fields use fetched values
                    channel_embed = discord.Embed(
                        title=f"Job Application {status_text}: {application.get_job_type_display()}",
                        color=status_color
                    )
                    channel_embed.add_field(name="Applicant", value=f"<@{applicant_discord_id}> ({applicant_discord_tag or applicant_username})", inline=True)
                    channel_embed.add_field(name="Job", value=application.get_job_type_display(), inline=True)
                    if reviewer_obj:
                        reviewer_mention = f"<@{reviewer_obj.discord_id}> ({reviewer_discord_tag or reviewer_username})" if reviewer_obj.discord_id else (reviewer_discord_tag or reviewer_username)
                        channel_embed.add_field(name="Reviewed By", value=reviewer_mention, inline=True)
                    if application.reviewed_at:
                        channel_embed.add_field(name="Reviewed At", value=application.reviewed_at.strftime("%Y-%m-%d %H:%M UTC"), inline=True)

                    channel_embed.set_footer(text=f"Application ID: {application.id}")

                    # Set image based on status
                    if application.status == 'APPROVED':
                        # TODO: Replace with your approval image URL
                        # channel_embed.set_image(url="YOUR_APPROVAL_IMAGE_URL")
                        pass # Placeholder if no image URL yet
                    else: # Rejected
                        # TODO: Replace with your rejection image URL
                        # channel_embed.set_image(url="YOUR_REJECTION_IMAGE_URL")
                        pass # Placeholder if no image URL yet

                    # channel.send is async
                    # Mention the user in the content part of the message
                    await channel.send(content=f"Job application update for <@{applicant_discord_id}>:", embed=channel_embed)
                    print(f"[JobAppNotify-{application.id}] Sent message to channel {channel.name}") 
            except ValueError:
                 print(f"[JobAppNotify-{application.id}] Invalid DISCORD_NOTIFICATIONS_CHANNEL_ID: {settings.DISCORD_NOTIFICATIONS_CHANNEL_ID}")
            except Exception as e:
                print(f"[JobAppNotify-{application.id}] Error sending to channel {settings.DISCORD_NOTIFICATIONS_CHANNEL_ID}: {e}")

            # --- DM the user --- #
            if not applicant_discord_id:
                print(f"[JobAppNotify-{application.id}] Applicant {applicant_username} has no Discord ID.")
                return
            
            print(f"[JobAppNotify-{application.id}] Applicant Discord ID found: {applicant_discord_id}") 
            try:
                guild_id = int(settings.DISCORD_GUILD_ID)
                # bot.get_guild is async safe
                guild = bot.get_guild(guild_id)
                if not guild:
                    print(f"[JobAppNotify-{application.id}] Guild not found: {guild_id}")
                    return 
                else:
                    print(f"[JobAppNotify-{application.id}] Found guild: {guild.name}") 

                print(f"[JobAppNotify-{application.id}] Attempting to fetch member: {applicant_discord_id}") 
                # guild.fetch_member is async
                member = await guild.fetch_member(int(applicant_discord_id))
                if not member:
                    print(f"[JobAppNotify-{application.id}] Member not found in guild {guild.name}: {applicant_discord_id}")
                    return
                print(f"[JobAppNotify-{application.id}] Found member: {member.name}") 
                
                status_color = discord.Color.green() if application.status == 'APPROVED' else discord.Color.red()
                status_text = "APPROVED" if application.status == 'APPROVED' else "REJECTED"

                dm_embed = discord.Embed(
                    title=f"Your {application.get_job_type_display()} Application Status: {status_text}",
                    color=status_color
                )

                if application.status == 'APPROVED':
                    dm_embed.description = f"Congratulations! Your application for the **{application.get_job_type_display()}** position at Vibe City RP has been approved."
                    dm_embed.add_field(name="Next Steps", value="You have been granted the Whitelisted role in Discord. Please familiarize yourself with server rules and connect to the server!", inline=False)
                    if application.feedback:
                        dm_embed.add_field(name="Additional Comments", value=application.feedback, inline=False)
                else: # Rejected
                    dm_embed.description = f"We regret to inform you that your application for the **{application.get_job_type_display()}** position at Vibe City RP has been rejected."
                    dm_embed.add_field(name="Reason/Feedback", value=application.feedback or "No specific feedback provided.", inline=False)
                    dm_embed.add_field(name="What Next?", value="You may be able to reapply after a cooldown period. Check department guidelines or contact HR.", inline=False)

                dm_embed.set_footer(text=f"Application ID: {application.id}")
                
                # Set image based on status for DM
                if application.status == 'APPROVED':
                    # TODO: Replace with your approval image URL
                    # dm_embed.set_image(url="YOUR_APPROVAL_IMAGE_URL")
                    pass # Placeholder if no image URL yet
                else: # Rejected
                    # TODO: Replace with your rejection image URL
                    # dm_embed.set_image(url="YOUR_REJECTION_IMAGE_URL")
                    pass # Placeholder if no image URL yet

                print(f"[JobAppNotify-{application.id}] Attempting to send DM to {member.name}") 
                # member.send is async
                await member.send(embed=dm_embed)
                print(f"[JobAppNotify-{application.id}] Sent DM to {member.name}") 
            except ValueError:
                 print(f"[JobAppNotify-{application.id}] Invalid DISCORD_GUILD_ID ({settings.DISCORD_GUILD_ID}) or applicant discord_id ({applicant_discord_id})")
            except discord.Forbidden:
                 print(f"[JobAppNotify-{application.id}] Cannot send DM to {applicant_username} ({applicant_discord_id}). DMs disabled or bot lacks permissions.")
            except discord.NotFound:
                print(f"[JobAppNotify-{application.id}] Member/User not found when trying to fetch/DM: {applicant_discord_id}")
            except Exception as e:
                print(f"[JobAppNotify-{application.id}] Error fetching member/user or sending DM to {applicant_discord_id}: {e}")
                import traceback
                traceback.print_exc()

        except Exception as e:
            print(f"[JobAppNotify-{application.id}] General error in send_job_application_result: {e}")
            import traceback
            traceback.print_exc()

    # Schedule the async function to run in the bot's event loop
    print(f"[JobAppNotify-{application.id}] Scheduling send() coroutine.") 
    asyncio.run_coroutine_threadsafe(send(), bot.loop)
    print(f"[JobAppNotify-{application.id}] Coroutine scheduled.") 