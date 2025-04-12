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

    async def on_message(self, message):
        # Prevent the bot from replying to itself
        if message.author == self.user:
            return
        
        # Check for keywords in the message
        keywords = ['form', 'apply', 'whitelist']
        if any(keyword in message.content.lower() for keyword in keywords):
            response = (
                "To apply, please visit: [Vibe City RP Website](http://104.234.180.225/)\n\n"
                "⌛Processing Times:\n"
                "Regular applications: ``Cleared within 1 day``\n\n"
                "If your application is taking longer, we're working hard through the workload and will get it out ASAP. Thanks for your patience!"
            )
            await message.reply(response)

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
            embed.add_field(name="\u200b", value="\u200b", inline=False) # Add a blank field to start a new line
            embed.add_field(name="Reviewed By", value=f"<@{application.reviewed_by.discord_id}>" if application.reviewed_by.discord_id else application.reviewed_by.username, inline=True)
            embed.add_field(name="Reviewed At", value=application.reviewed_at.strftime("%Y-%m-%d %H:%M UTC"), inline=True)
            
            
            embed.set_thumbnail(url=application.user.avatar_url)
            
            # Set image based on status
            if application.status == 'approved':
                # TODO: Replace with your approval image URL
                embed.set_image(url="https://res.cloudinary.com/dsodx3ntj/image/upload/v1744445339/1_m1klpk.jpg")
                pass # Placeholder if no image URL yet
            else:
                # TODO: Replace with your rejection image URL
                embed.set_image(url="https://res.cloudinary.com/dsodx3ntj/image/upload/v1744445339/2_xq0z7y.jpg")
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
                    dm_embed.set_image(url="https://res.cloudinary.com/dsodx3ntj/image/upload/v1744445339/1_m1klpk.jpg")
                    pass # Placeholder if no image URL yet
                else:
                    # TODO: Replace with your rejection image URL
                    dm_embed.set_image(url="https://res.cloudinary.com/dsodx3ntj/image/upload/v1744445339/2_xq0z7y.jpg")
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
            applicant_obj = await sync_to_async(lambda: application.applicant)()
            form_reviewer_obj = await sync_to_async(lambda: application.form_reviewer)()
            interview_reviewer_obj = await sync_to_async(lambda: application.interview_reviewer)()
            
            if not applicant_obj:
                print(f"[JobAppNotify-{application.id}] Application has no applicant.")
                return
            print(f"[JobAppNotify-{application.id}] Applicant found: {applicant_obj.username} ({applicant_obj.id})") 
            
            applicant_discord_tag = await sync_to_async(lambda: applicant_obj.discord_tag)()
            applicant_username = await sync_to_async(lambda: applicant_obj.username)()
            applicant_discord_id = await sync_to_async(lambda: applicant_obj.discord_id)()

            # Determine which reviewer is relevant based on current status
            final_reviewer_obj = interview_reviewer_obj if application.status in ['HIRED', 'REJECTED_INTERVIEW'] else form_reviewer_obj
            final_reviewer_tag = None
            final_reviewer_username = None
            if final_reviewer_obj:
                 final_reviewer_tag = await sync_to_async(lambda: final_reviewer_obj.discord_tag)()
                 final_reviewer_username = await sync_to_async(lambda: final_reviewer_obj.username)()

            # Determine status color and text for embeds
            status_color = discord.Color.default()
            if application.status == 'HIRED': status_color = discord.Color.green()
            elif application.status == 'INTERVIEW_PENDING': status_color = discord.Color.blue()
            elif application.status == 'PENDING': status_color = discord.Color.gold() # Should not normally notify here
            elif 'REJECTED' in application.status: status_color = discord.Color.red()

            status_text = application.get_status_display() # Use display name from model
            final_feedback = application.interview_feedback if application.status in ['HIRED', 'REJECTED_INTERVIEW'] else application.form_feedback

            # --- Send to Notifications Channel --- #
            try:
                channel_id = int(settings.DISCORD_NOTIFICATIONS_CHANNEL_ID)
                channel = bot.get_channel(channel_id)
                if not channel:
                    print(f"[JobAppNotify-{application.id}] Channel not found: {channel_id}")
                else:
                    channel_embed = discord.Embed(
                        title=f"Job Application Update: {application.get_job_type_display()}",
                        description=f"{applicant_username}'s application status updated to **{status_text}**.",
                        color=status_color
                    )
                    channel_embed.add_field(name="Applicant", value=applicant_discord_tag or applicant_username, inline=True)
                    channel_embed.add_field(name="Job", value=application.get_job_type_display(), inline=True)
                    if final_reviewer_obj:
                        channel_embed.add_field(name="Processed By", value=final_reviewer_tag or final_reviewer_username, inline=True)
                    
                    # Add reviewed date based on stage
                    reviewed_at = application.interview_reviewed_at if application.status in ['HIRED', 'REJECTED_INTERVIEW'] else application.form_reviewed_at
                    if reviewed_at:
                         channel_embed.add_field(name="Processed At", value=reviewed_at.strftime("%Y-%m-%d %H:%M"), inline=True)
                    
                    if final_feedback:
                         channel_embed.add_field(name="Feedback", value=final_feedback[:1020] + "..." if len(final_feedback)>1024 else final_feedback, inline=False)

                    # Add job-specific image for approved/rejected applications
                    if application.status == 'HIRED':
                        if application.job_type == 'SASP':
                            channel_embed.set_image(url="https://res.cloudinary.com/dsodx3ntj/image/upload/v1744445310/2_menxjj.jpg")
                        elif application.job_type == 'EMS':
                            channel_embed.set_image(url="https://res.cloudinary.com/dsodx3ntj/image/upload/v1744445258/1_vakqr9.jpg")
                        elif application.job_type == 'MECHANIC':
                            channel_embed.set_image(url="https://res.cloudinary.com/dsodx3ntj/image/upload/v1744445290/2_snyeko.jpg")
                    elif 'REJECTED' in application.status:
                        if application.job_type == 'SASP':
                            channel_embed.set_image(url="https://res.cloudinary.com/dsodx3ntj/image/upload/v1744445310/1_hwtnj7.jpg")
                        elif application.job_type == 'EMS':
                            channel_embed.set_image(url="https://res.cloudinary.com/dsodx3ntj/image/upload/v1744445258/2_n3ynli.jpg")
                        elif application.job_type == 'MECHANIC':
                            channel_embed.set_image(url="https://res.cloudinary.com/dsodx3ntj/image/upload/v1744445290/1_klkkrk.jpg")

                    # Mention user in content
                    await channel.send(content=f"Job application update for <@{applicant_discord_id}>:", embed=channel_embed)
                    print(f"[JobAppNotify-{application.id}] Sent channel message for status {status_text}")
            except Exception as e:
                print(f"[JobAppNotify-{application.id}] Error sending to channel {settings.DISCORD_NOTIFICATIONS_CHANNEL_ID}: {e}")

            # --- NEW: Send to Public Responses Channel --- #
            try:
                public_channel_id_setting = getattr(settings, 'DISCORD_JOB_RESPONSES_CHANNEL_ID', None)
                if public_channel_id_setting:
                    public_channel_id = int(public_channel_id_setting)
                    public_channel = bot.get_guild(public_channel_id)
                    if not public_channel:
                        print(f"[JobAppNotify-{application.id}] Public responses channel not found: {public_channel_id}")
                    else:
                        # Create a simplified embed for public view
                        public_embed = discord.Embed(
                            # title=f"{application.get_job_type_display()} Application Update", # Alternative title
                            color=status_color
                        )
                        
                        mention = f"<@{applicant_discord_id}>"
                        job_display = application.get_job_type_display()
                        
                        # Tailor message based on status
                        if application.status == 'HIRED':
                            public_embed.description = f"🎉 Congratulations to {mention} on being **HIRED** for the **{job_display}** team! Welcome aboard!"
                        elif application.status == 'INTERVIEW_PENDING':
                             public_embed.description = f"📄 {mention}'s application for **{job_display}** has passed the initial review and is moving to the interview stage!"
                        elif application.status == 'REJECTED' or application.status == 'REJECTED_INTERVIEW':
                             # Decide if you want to announce rejections publicly
                             # If not, you can comment out this block or add a condition
                             stage = "Form Stage" if application.status == 'REJECTED' else "Interview Stage"
                             public_embed.description = f"❗️ Regarding {mention}'s application for **{job_display}**: The application was not successful at this time ({stage})."
                        else:
                            public_embed = None # Don't announce other statuses publicly?
                        
                        if public_embed:
                            # Send mention in content for ping
                            await public_channel.send(content=f"Application update for <@{applicant_discord_id}>:", embed=public_embed)
                            print(f"[JobAppNotify-{application.id}] Sent PUBLIC response to channel {public_channel.name}.")
                else:
                     print(f"[JobAppNotify-{application.id}] DISCORD_JOB_RESPONSES_CHANNEL_ID not set. Skipping public notification.")
            except ValueError:
                 print(f"[JobAppNotify-{application.id}] Invalid DISCORD_JOB_RESPONSES_CHANNEL_ID: {public_channel_id_setting}")
            except Exception as e:
                print(f"[JobAppNotify-{application.id}] Error sending to PUBLIC responses channel: {e}")

            # --- DM the user --- #
            if not applicant_discord_id:
                print(f"[JobAppNotify-{application.id}] Applicant {applicant_username} has no Discord ID.")
                return
            
            print(f"[JobAppNotify-{application.id}] Applicant Discord ID found: {applicant_discord_id}") 
            try:
                guild_id = int(settings.DISCORD_GUILD_ID)
                guild = bot.get_guild(guild_id)
                if not guild:
                    print(f"[JobAppNotify-{application.id}] Guild not found: {guild_id}")
                    return 
                else:
                    print(f"[JobAppNotify-{application.id}] Found guild: {guild.name}") 

                print(f"[JobAppNotify-{application.id}] Attempting to fetch member: {applicant_discord_id}") 
                member = await guild.fetch_member(int(applicant_discord_id))
                if not member:
                    print(f"[JobAppNotify-{application.id}] Member not found in guild {guild.name}: {applicant_discord_id}")
                    return
                print(f"[JobAppNotify-{application.id}] Found member: {member.name}") 
                
                dm_embed = discord.Embed(
                    title=f"Update on your {application.get_job_type_display()} Application",
                    color=status_color
                )

                if application.status == 'HIRED':
                    dm_embed.description = f"**Congratulations! You have been HIRED for the {application.get_job_type_display()} position at Vibe City RP!**"
                    dm_embed.add_field(name="Next Steps", value="Please contact the relevant department lead or HR in Discord for onboarding instructions.", inline=False)
                    if final_feedback:
                        dm_embed.add_field(name="Additional Comments from Hiring Manager", value=final_feedback, inline=False)
                    
                    # Add job-specific image for approved applications
                    if application.job_type == 'SASP':
                        dm_embed.set_image(url="https://res.cloudinary.com/dsodx3ntj/image/upload/v1744445310/2_menxjj.jpg")
                    elif application.job_type == 'EMS':
                        dm_embed.set_image(url="https://res.cloudinary.com/dsodx3ntj/image/upload/v1744445258/1_vakqr9.jpg")
                    elif application.job_type == 'MECHANIC':
                        dm_embed.set_image(url="https://res.cloudinary.com/dsodx3ntj/image/upload/v1744445290/2_snyeko.jpg")
                elif application.status == 'INTERVIEW_PENDING':
                     dm_embed.description = f"Good news! Your initial application for **{application.get_job_type_display()}** has passed review."
                     dm_embed.add_field(name="Next Step: Interview", value="You will be contacted shortly by a department representative to schedule an interview. Please be prepared.", inline=False)
                     if final_feedback:
                        dm_embed.add_field(name="Reviewer Comments", value=final_feedback, inline=False)
                elif 'REJECTED' in application.status:
                    stage = "Form Stage" if application.status == 'REJECTED' else "Interview Stage"
                    dm_embed.description = f"We regret to inform you that your application for the **{application.get_job_type_display()}** position was not successful at the **{stage}**."
                    dm_embed.add_field(name="Reason/Feedback", value=final_feedback or "No specific feedback provided.", inline=False)
                    dm_embed.add_field(name="What Next?", value="You may be able to reapply after a cooldown period. Check department guidelines or contact HR.", inline=False)
                    
                    # Add job-specific image for rejected applications
                    if application.job_type == 'SASP':
                        dm_embed.set_image(url="https://res.cloudinary.com/dsodx3ntj/image/upload/v1744445310/1_hwtnj7.jpg")
                    elif application.job_type == 'EMS':
                        dm_embed.set_image(url="https://res.cloudinary.com/dsodx3ntj/image/upload/v1744445258/2_n3ynli.jpg")
                    elif application.job_type == 'MECHANIC':
                        dm_embed.set_image(url="https://res.cloudinary.com/dsodx3ntj/image/upload/v1744445290/1_klkkrk.jpg")
                # No DM needed for PENDING status usually
                else:
                     print(f"[JobAppNotify-{application.id}] No DM configured for status {application.status}")
                     return # Don't send DM for unhandled statuses

                await member.send(embed=dm_embed)
                print(f"[JobAppNotify-{application.id}] Sent DM for status {status_text}")

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

# --- New Job Application Submitted Notification --- #

def send_new_job_application_notification(application):
    """Sends notifications when a NEW job application is submitted."""
    print(f"[JobAppNewNotify-{application.id}] Received request.") # DEBUG
    if not bot_ready.is_set():
        print(f"[JobAppNewNotify-{application.id}] Bot not ready, waiting...")
        bot_ready.wait(timeout=15) 
        if not bot_ready.is_set():
            print(f"[JobAppNewNotify-{application.id}] Bot did not become ready.")
            return
        print(f"[JobAppNewNotify-{application.id}] Bot ready.")

    if not bot or not bot.loop.is_running():
        print(f"[JobAppNewNotify-{application.id}] Bot not initialized or loop not running.")
        return

    async def send():
        print(f"[JobAppNewNotify-{application.id}] Entering async send().")
        try:
            applicant_obj = await sync_to_async(lambda: application.applicant)()
            if not applicant_obj:
                print(f"[JobAppNewNotify-{application.id}] No applicant found.")
                return
            
            applicant_discord_tag = await sync_to_async(lambda: applicant_obj.discord_tag)()
            applicant_username = await sync_to_async(lambda: applicant_obj.username)()
            applicant_discord_id = await sync_to_async(lambda: applicant_obj.discord_id)()
            applicant_avatar_url = await sync_to_async(lambda: applicant_obj.avatar_url)()

            job_type_display = application.get_job_type_display()
            submitted_at_str = application.submitted_at.strftime("%Y-%m-%d %H:%M UTC")

            # --- Notify Staff Channel --- #
            try:
                # Use a specific channel for NEW applications if configured, else use general notifications
                channel_id_setting = getattr(settings, 'DISCORD_JOB_APPLICATIONS_CHANNEL_ID', settings.DISCORD_NOTIFICATIONS_CHANNEL_ID)
                channel_id = int(channel_id_setting)
                channel = bot.get_channel(channel_id)
                if not channel:
                    print(f"[JobAppNewNotify-{application.id}] Staff channel not found: {channel_id}")
                else:
                    staff_embed = discord.Embed(
                        title=f"New Job Application Submitted: {job_type_display}",
                        description=f"Submitted by **{applicant_discord_tag or applicant_username}**.",
                        color=discord.Color.blue()
                    )
                    if applicant_avatar_url: staff_embed.set_thumbnail(url=applicant_avatar_url)
                    staff_embed.add_field(name="Applicant", value=applicant_username, inline=True)
                    staff_embed.add_field(name="Job Type", value=job_type_display, inline=True)
                    staff_embed.add_field(name="Submitted", value=submitted_at_str, inline=True)
                    staff_embed.set_footer(text=f"Application ID: {application.id}. Review via staff dashboard.")
                    
                    # TODO: Add link to review page?
                    # Requires generating the URL: reverse('job_application_detail', args=[application.id])
                    # Need to make reverse() async-safe or generate URL before calling this function.

                    # Mention user in content
                    await channel.send(content=f"New job application from <@{applicant_discord_id}>:", embed=staff_embed)
                    print(f"[JobAppNewNotify-{application.id}] Sent staff notification to channel {channel.name}.")
            except ValueError:
                 print(f"[JobAppNewNotify-{application.id}] Invalid Discord Channel ID setting.")
            except Exception as e:
                print(f"[JobAppNewNotify-{application.id}] Error sending to staff channel: {e}")

            # --- DM Applicant --- #
            if applicant_discord_id:
                try:
                    guild_id = int(settings.DISCORD_GUILD_ID)
                    guild = bot.get_guild(guild_id)
                    if guild:
                         member = await guild.fetch_member(int(applicant_discord_id))
                         if member:
                            dm_embed = discord.Embed(
                                title=f"Your {job_type_display} Application Received",
                                description=f"Thank you, {applicant_username}, for applying to join the {job_type_display} team at Vibe City RP!",
                                color=discord.Color.gold()
                            )
                            dm_embed.add_field(name="Status", value="Your application is now Pending Form Review. You will receive further updates via DM.", inline=False)
                            dm_embed.add_field(name="Submitted", value=submitted_at_str, inline=True)
                            dm_embed.set_footer(text="We appreciate your interest!")
                            
                            await member.send(embed=dm_embed)
                            print(f"[JobAppNewNotify-{application.id}] Sent confirmation DM to {member.name}.")
                         else:
                             print(f"[JobAppNewNotify-{application.id}] Applicant member not found in guild {guild_id} for DM.")
                    else:
                        print(f"[JobAppNewNotify-{application.id}] Guild {guild_id} not found for DM.")
                except Exception as e:
                    print(f"[JobAppNewNotify-{application.id}] Error sending confirmation DM: {e}")
            else:
                print(f"[JobAppNewNotify-{application.id}] No Discord ID for applicant, cannot send DM.")

        except Exception as e:
            print(f"[JobAppNewNotify-{application.id}] General error: {e}")
            import traceback
            traceback.print_exc()

    asyncio.run_coroutine_threadsafe(send(), bot.loop)
    print(f"[JobAppNewNotify-{application.id}] Coroutine scheduled.") 

def send_ticket_notification(ticket, action_type, message=None):
    """Sends Discord notifications for ticket updates."""
    if not bot_ready.is_set():
        print("Bot not ready yet, waiting...")
        bot_ready.wait(timeout=10)
    
    if not bot:
        print("Bot not initialized")
        return
    
    async def send():
        try:
            # Get the ticket channel
            channel_id = int(settings.DISCORD_SUPPORT_CHANNEL_ID)
            channel = bot.get_channel(channel_id)
            if not channel:
                print(f"Channel not found: {channel_id}")
                return
            
            # Create embed based on action type
            if action_type == 'created':
                embed = discord.Embed(
                    title="New Support Ticket Created",
                    description=f"Ticket #{ticket.id}: {ticket.title}",
                    color=discord.Color.blue()
                )
                embed.add_field(name="User", value=f"<@{ticket.user.discord_id}> ({ticket.user.discord_tag})", inline=True)
                embed.add_field(name="Priority", value=ticket.get_priority_display(), inline=True)
                embed.add_field(name="Description", value=ticket.description[:1024] + "..." if len(ticket.description) > 1024 else ticket.description, inline=False)
                embed.set_footer(text="Please review this ticket in the staff dashboard")
                
            elif action_type == 'status_change':
                embed = discord.Embed(
                    title=f"Ticket #{ticket.id} Status Updated",
                    description=f"Status changed to: {ticket.get_status_display()}",
                    color=discord.Color.gold()
                )
                embed.add_field(name="Ticket", value=ticket.title, inline=True)
                embed.add_field(name="User", value=f"<@{ticket.user.discord_id}>", inline=True)
                if ticket.assigned_to:
                    embed.add_field(name="Assigned To", value=f"<@{ticket.assigned_to.discord_id}>", inline=True)
                
            elif action_type == 'message':
                embed = discord.Embed(
                    title=f"New Message on Ticket #{ticket.id}",
                    description=f"From: {'Staff' if message.is_staff_message else 'User'}",
                    color=discord.Color.green()
                )
                embed.add_field(name="Ticket", value=ticket.title, inline=True)
                embed.add_field(name="User", value=f"<@{message.user.discord_id}>", inline=True)
                embed.add_field(name="Message", value=message.message[:1024] + "..." if len(message.message) > 1024 else message.message, inline=False)
                
            elif action_type == 'reopened':
                embed = discord.Embed(
                    title=f"Ticket #{ticket.id} Reopened",
                    description=f"Ticket has been reopened by {ticket.user.discord_tag}",
                    color=discord.Color.orange()
                )
                embed.add_field(name="Ticket", value=ticket.title, inline=True)
                embed.add_field(name="User", value=f"<@{ticket.user.discord_id}>", inline=True)
            
            # Send to channel
            await channel.send(embed=embed)
            
            # Send DM to user if not staff message
            if action_type in ['status_change', 'message'] and not message.is_staff_message:
                try:
                    guild = bot.get_guild(int(settings.DISCORD_GUILD_ID))
                    if not guild:
                        print(f"Guild not found: {settings.DISCORD_GUILD_ID}")
                        return
                    
                    member = await guild.fetch_member(int(ticket.user.discord_id))
                    if not member:
                        print(f"Member not found: {ticket.user.discord_id}")
                        return
                    
                    dm_embed = discord.Embed(
                        title=f"Update on Ticket #{ticket.id}",
                        color=discord.Color.blue()
                    )
                    
                    if action_type == 'status_change':
                        dm_embed.description = f"Your ticket status has been updated to: {ticket.get_status_display()}"
                        if ticket.assigned_to:
                            dm_embed.add_field(name="Assigned To", value=f"<@{ticket.assigned_to.discord_id}>", inline=True)
                    else:
                        dm_embed.description = f"New message on your ticket from staff"
                        dm_embed.add_field(name="Message", value=message.message[:1024] + "..." if len(message.message) > 1024 else message.message, inline=False)
                    
                    await member.send(embed=dm_embed)
                except Exception as e:
                    print(f"Error sending DM to user: {e}")
        
        except Exception as e:
            print(f"Error sending ticket notification: {e}")
    
    asyncio.run_coroutine_threadsafe(send(), bot.loop)