import discord
from discord.ext import commands
import asyncio
import os
from django.conf import settings
import threading
from asgiref.sync import sync_to_async
import pytz
from PIL import Image, ImageDraw, ImageFont, ImageOps
import requests
from io import BytesIO
import aiohttp
import ssl
import certifi
from discord import ui, app_commands


original_init = aiohttp.ClientSession.__init__

def new_init(self, *args, **kwargs):
    if 'connector' not in kwargs:
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        kwargs['connector'] = aiohttp.TCPConnector(ssl=ssl_context)
    original_init(self, *args, **kwargs)

aiohttp.ClientSession.__init__ = new_init
# Global bot instance
bot = None
bot_ready = threading.Event()

async def create_welcome_banner(member):
    """Create a custom welcome banner with user avatar"""
    try:
        # Load the background template
        background = Image.open('discord_bot/assets/welcome_template.png').convert('RGBA')
        
        # Download and process user avatar
        async with aiohttp.ClientSession() as session:
            avatar_url = str(member.avatar.url if member.avatar else member.default_avatar.url)
            async with session.get(avatar_url) as resp:
                avatar_data = await resp.read()
                avatar = Image.open(BytesIO(avatar_data)).convert('RGBA')
        
        # Resize avatar and make it circular
        avatar = avatar.resize((600, 600))  # Much larger avatar
        
        # Create circular mask
        mask = Image.new('L', avatar.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, avatar.size[0], avatar.size[1]), fill=255)
        
        # Apply mask to avatar
        output = Image.new('RGBA', avatar.size, (0, 0, 0, 0))
        output.paste(avatar, (0, 0))
        output.putalpha(mask)
        
        # Calculate positions
        avatar_pos = ((background.width - avatar.width) // 2, 250)  # Moved up to accommodate larger size
        
        # Create a new image for compositing
        composite = Image.new('RGBA', background.size, (0, 0, 0, 0))
        composite.paste(background, (0, 0))
        composite.paste(output, avatar_pos, output)
        
        # Add username text
        draw = ImageDraw.Draw(composite)
        try:
            font = ImageFont.truetype('discord_bot/assets/font.ttf', 500)
        except:
            font = ImageFont.load_default()
        
        username = member.name
        text_width = draw.textlength(username, font=font)
        text_position = ((background.width - text_width) // 2, 900)
        
        # Add text shadow/outline effect
        shadow_offset = 4
        shadow_color = (100, 100, 100, 255)  # Added alpha channel
        
        # Add multiple shadow layers for stronger effect
        for offset in range(1, shadow_offset + 1):
            draw.text((text_position[0] + offset, text_position[1] + offset), 
                     username, font=font, fill=shadow_color)
        
        # Draw main text
        draw.text(text_position, username, font=font, fill=(255, 255, 255, 255))  # Added alpha channel
        
        # Convert to RGB for saving as PNG
        final_image = composite.convert('RGB')
        
        # Save to BytesIO
        output_buffer = BytesIO()
        final_image.save(output_buffer, format='PNG')
        output_buffer.seek(0)
        
        return output_buffer
    except Exception as e:
        print(f"Error creating welcome banner: {e}")
        import traceback
        traceback.print_exc()
        return None

class VibeCity(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        
        super().__init__(command_prefix='!', intents=intents)
    
    async def setup_hook(self):
        try:
            # Clear existing commands
            self.tree.clear_commands(guild=None)
            
            # Add commands
            self.tree.add_command(self.whiteliststeps)
            self.tree.add_command(self.rules)
            
            # Force sync with Discord
            await self.tree.sync(guild=None)
            print("Successfully synced commands with Discord")
        except Exception as e:
            print(f"Error syncing commands: {e}")
            import traceback
            traceback.print_exc()
    
    def get_whitelist_embed_and_view(self):
        class WhitelistApplyView(ui.View):
            def __init__(self):
                super().__init__()
                self.add_item(ui.Button(label="Apply for Whitelist", url="https://vibecityrp.com/whitelist/", style=discord.ButtonStyle.link))
        embed = discord.Embed(
            title="How to Apply for Whitelist",
            description="Follow these steps to apply for the Vibe City RP whitelist:",
            color=discord.Color.green()
        )
        embed.add_field(name="Step 1", value="Go to the application website.", inline=False)
        embed.add_field(name="Step 2", value="Log in with your Discord account.", inline=False)
        embed.add_field(name="Step 3", value="Fill out the whitelist application form with accurate information.", inline=False)
        embed.add_field(name="Step 4", value="Submit your application and wait for staff review.", inline=False)
        embed.add_field(name="Processing Times", value="Most applications are cleared within 1 day. If it takes longer, please be patient!", inline=False)
        embed.set_footer(text="Vibe City RP | Whitelist Application")
        return embed, WhitelistApplyView()

    def get_rules_embed_and_view(self):
        class RulesView(ui.View):
            def __init__(self):
                super().__init__()
                self.add_item(ui.Button(label="View Rules", url="https://vibecityrp.com/rules/", style=discord.ButtonStyle.link))
        embed = discord.Embed(
            title="Vibe City RP Rules",
            description="Please read and follow our server rules to ensure a great experience for everyone.",
            color=discord.Color.blue()
        )
        embed.add_field(name="Rules Link", value="Click the button below to view our complete rules and guidelines.", inline=False)
        embed.set_footer(text="Vibe City RP | Server Rules")
        return embed, RulesView()

    @app_commands.command(
        name="whiteliststeps",
        description="Show steps to apply for whitelist"
    )
    async def whiteliststeps(self, interaction: discord.Interaction):
        """Show steps to apply for whitelist"""
        embed, view = self.get_whitelist_embed_and_view()
        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(
        name="rules",
        description="Show link to server rules"
    )
    async def rules(self, interaction: discord.Interaction):
        """Show link to server rules"""
        embed, view = self.get_rules_embed_and_view()
        await interaction.response.send_message(embed=embed, view=view)

    async def on_ready(self):
        print(f'Logged in as {self.user.name} ({self.user.id})')
        bot_ready.set()

    async def on_message(self, message):
        if message.author == self.user:
            return
        
        # Process commands first
        await self.process_commands(message)
        
        # Then handle other message content
        if 'whitelist' in message.content.lower():
            embed, view = self.get_whitelist_embed_and_view()
            await message.reply(embed=embed, view=view)
        elif any(word in message.content.lower() for word in ['rules', 'rule', 'rtc']):
            embed, view = self.get_rules_embed_and_view()
            await message.reply(embed=embed, view=view)

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
            # Send to applications channel
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
            embed.add_field(name="Submitted At", value=application.created_at.astimezone(pytz.timezone('Asia/Kolkata')).strftime("%Y-%m-%d %H:%M IST"), inline=True)
            embed.add_field(name="Status", value="Pending Review", inline=True)
            embed.add_field(name="Application ID", value=application.id, inline=True)
            
            embed.set_thumbnail(url=application.user.avatar_url)
            embed.set_footer(text="Review this application in the staff dashboard")
            
            await channel.send(embed=embed)

            # Send DM to the user
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
                    title="Whitelist Application Received",
                    description="Thank you for submitting your whitelist application to Vibe City RP!",
                    color=discord.Color.green()
                )
                dm_embed.add_field(
                    name="Status",
                    value="Your application is now pending review by our staff team.",
                    inline=False
                )
                dm_embed.add_field(
                    name="Processing Time",
                    value="Most applications are reviewed within 24 hours. You will receive a DM when your application has been reviewed.",
                    inline=False
                )
                dm_embed.add_field(
                    name="Application ID",
                    value=application.id,
                    inline=True
                )
                dm_embed.add_field(
                    name="Submitted At",
                    value=application.created_at.astimezone(pytz.timezone('Asia/Kolkata')).strftime("%Y-%m-%d %H:%M IST"),
                    inline=True
                )
                dm_embed.set_footer(text="Vibe City RP | Whitelist Application")
                
                await member.send(embed=dm_embed)
                print(f"Sent confirmation DM to {member.name}")
            except Exception as e:
                print(f"Error sending DM to user: {e}")
        
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
            # Get the channel
            channel = bot.get_channel(int(settings.DISCORD_WHITELIST_RESPONSES_CHANNEL_ID))
            if not channel:
                print(f"Channel not found: {settings.DISCORD_WHITELIST_RESPONSES_CHANNEL_ID}")
                return
            
            # Get application data using sync_to_async
            user = await sync_to_async(lambda: application.user)()
            reviewed_by = await sync_to_async(lambda: application.reviewed_by)()
            
            status_color = discord.Color.green() if application.status == 'approved' else discord.Color.red()
            status_text = "APPROVED" if application.status == 'approved' else "REJECTED"
            
            embed = discord.Embed(
                title=f"Whitelist Application {status_text}",
                description=f"<@{user.discord_id}>'s whitelist application has been {application.status}.",
                color=status_color
            )
            
            embed.add_field(name="Applicant", value=f"<@{user.discord_id}>", inline=True)
            embed.add_field(name="\u200b", value="\u200b", inline=False)
            embed.add_field(name="Reviewed By", value=f"<@{reviewed_by.discord_id}>" if reviewed_by.discord_id else reviewed_by.username, inline=True)
            embed.add_field(name="Reviewed At", value=application.reviewed_at.astimezone(pytz.timezone('Asia/Kolkata')).strftime("%Y-%m-%d %H:%M IST"), inline=True)
            
            embed.set_thumbnail(url=user.avatar_url)
            
            # Set image based on status
            if application.status == 'approved':
                embed.set_image(url="https://res.cloudinary.com/dsodx3ntj/image/upload/v1744445339/1_m1klpk.jpg")
            else:
                embed.set_image(url="https://res.cloudinary.com/dsodx3ntj/image/upload/v1744445339/2_xq0z7y.jpg")

            # Mention the user in the channel message content
            await channel.send(content=f"Status update for <@{user.discord_id}>:", embed=embed)
            
            # Assign whitelist role if approved
            if application.status == 'approved':
                try:
                    guild = bot.get_guild(int(settings.DISCORD_GUILD_ID))
                    if not guild:
                        print(f"Guild not found: {settings.DISCORD_GUILD_ID}")
                        return
                    
                    member = await guild.fetch_member(int(user.discord_id))
                    if not member:
                        print(f"Member not found: {user.discord_id}")
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
                
                member = await guild.fetch_member(int(user.discord_id))
                if not member:
                    print(f"Member not found: {user.discord_id}")
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
                    dm_embed.set_image(url="https://res.cloudinary.com/dsodx3ntj/image/upload/v1744445339/1_m1klpk.jpg")
                else:
                    dm_embed.set_image(url="https://res.cloudinary.com/dsodx3ntj/image/upload/v1744445339/2_xq0z7y.jpg")

                await member.send(embed=dm_embed)
            except Exception as e:
                print(f"Error sending DM to user: {e}")
        
        except Exception as e:
            print(f"Error sending application result notification: {e}")
    
    asyncio.run_coroutine_threadsafe(send(), bot.loop)

def send_job_application_result(application):
    """Sends notification about job application results to channel and DM, and manages Discord roles."""
    print(f"[JobAppNotify-{application.id}] Received request to notify.") # DEBUG
    if not bot_ready.is_set():
        print(f"[JobAppNotify-{application.id}] Bot not ready, waiting...")
        bot_ready.wait(timeout=15)
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
            if not applicant_obj:
                print(f"[JobAppNotify-{application.id}] No applicant found.")
                return
            
            applicant_discord_tag = await sync_to_async(lambda: applicant_obj.discord_tag)()
            applicant_username = await sync_to_async(lambda: applicant_obj.username)()
            applicant_discord_id = await sync_to_async(lambda: applicant_obj.discord_id)()
            applicant_avatar_url = await sync_to_async(lambda: applicant_obj.avatar_url)()

            # Get the guild and member
            guild_id = int(settings.DISCORD_GUILD_ID)
            guild = bot.get_guild(guild_id)
            if not guild:
                print(f"[JobAppNotify-{application.id}] Guild not found: {guild_id}")
                return
            
            member = await guild.fetch_member(int(applicant_discord_id))
            if not member:
                print(f"[JobAppNotify-{application.id}] Member not found: {applicant_discord_id}")
                return

            # --- Role Management Logic --- #
            try:
                interview_roles = [
                    int(settings.DISCORD_SASP_INTERVIEW_ROLE_ID),
                    int(settings.DISCORD_EMS_INTERVIEW_ROLE_ID),
                    int(settings.DISCORD_MECHANIC_INTERVIEW_ROLE_ID)
                ]
                hired_roles = [
                    int(settings.DISCORD_SASP_HIRED_ROLE_ID),
                    int(settings.DISCORD_EMS_HIRED_ROLE_ID),
                    int(settings.DISCORD_MECHANIC_HIRED_ROLE_ID)
                ]
                # Remove all interview and hired roles first
                for role_id in interview_roles + hired_roles:
                    try:
                        role = guild.get_role(role_id)
                        if role and role in member.roles:
                            await member.remove_roles(role)
                            print(f"[JobAppNotify-{application.id}] Removed role {role_id} from {member.name}")
                    except Exception as e:
                        print(f"[JobAppNotify-{application.id}] Error removing role {role_id}: {e}")
                # Add the appropriate role
                if application.status == 'INTERVIEW_PENDING':
                    if application.job_type == 'SASP':
                        role_id = int(settings.DISCORD_SASP_INTERVIEW_ROLE_ID)
                    elif application.job_type == 'EMS':
                        role_id = int(settings.DISCORD_EMS_INTERVIEW_ROLE_ID)
                    else:
                        role_id = int(settings.DISCORD_MECHANIC_INTERVIEW_ROLE_ID)
                    role = guild.get_role(role_id)
                    if role:
                        await member.add_roles(role)
                        print(f"[JobAppNotify-{application.id}] Added interview role {role_id} to {member.name}")
                elif application.status == 'HIRED':
                    if application.job_type == 'SASP':
                        role_id = int(settings.DISCORD_SASP_HIRED_ROLE_ID)
                    elif application.job_type == 'EMS':
                        role_id = int(settings.DISCORD_EMS_HIRED_ROLE_ID)
                    else:
                        role_id = int(settings.DISCORD_MECHANIC_HIRED_ROLE_ID)
                    role = guild.get_role(role_id)
                    if role:
                        await member.add_roles(role)
                        print(f"[JobAppNotify-{application.id}] Added hired role {role_id} to {member.name}")
                # For FIRED and REJECTED, only removal is needed (already done above)
            except Exception as e:
                print(f"[JobAppNotify-{application.id}] Error in role management: {e}")

            # --- Notification Logic (existing code) --- #
            # ... existing notification code here ...
            # (Keep the rest of the function as previously refactored)

            # Determine status color and text for embeds
            status_color = discord.Color.default()
            if application.status == 'HIRED': status_color = discord.Color.green()
            elif application.status == 'INTERVIEW_PENDING': status_color = discord.Color.blue()
            elif application.status == 'PENDING': status_color = discord.Color.gold()
            elif application.status == 'FIRED': status_color = discord.Color.dark_gray()
            elif 'REJECTED' in application.status: status_color = discord.Color.red()

            status_text = application.get_status_display()
            final_feedback = application.interview_feedback if application.status in ['HIRED', 'FIRED', 'REJECTED_INTERVIEW'] else application.form_feedback

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
                    
                    if final_feedback:
                         channel_embed.add_field(name="Feedback", value=final_feedback[:1020] + "..." if len(final_feedback)>1024 else final_feedback, inline=False)

                    # Add job-specific image based on status
                    if application.status == 'FIRED':
                        if application.job_type == 'SASP':
                            channel_embed.set_image(url="https://res.cloudinary.com/dsodx3ntj/image/upload/v1744445310/1_hwtnj7.jpg")
                        elif application.job_type == 'EMS':
                            channel_embed.set_image(url="https://res.cloudinary.com/dsodx3ntj/image/upload/v1744445258/2_n3ynli.jpg")
                        elif application.job_type == 'MECHANIC':
                            channel_embed.set_image(url="https://res.cloudinary.com/dsodx3ntj/image/upload/v1744445290/1_klkkrk.jpg")

                    await channel.send(content=f"Job application update for <@{applicant_discord_id}>:", embed=channel_embed)
                    print(f"[JobAppNotify-{application.id}] Sent channel message for status {status_text}")
            except Exception as e:
                print(f"[JobAppNotify-{application.id}] Error sending to channel: {e}")

            # --- Send DM to user --- #
            try:
                dm_embed = discord.Embed(
                    title=f"Update on your {application.get_job_type_display()} Application",
                    color=status_color
                )

                if application.status == 'FIRED':
                    dm_embed.description = f"You have been removed from the **{application.get_job_type_display()}** team."
                    dm_embed.add_field(
                        name="What This Means",
                        value="Your job role has been removed from Discord. You may reapply for this position after a cooldown period.",
                        inline=False
                    )
                    if final_feedback:
                        dm_embed.add_field(
                            name="Reason",
                            value=final_feedback,
                            inline=False
                        )
                    # Add job-specific image for fired status
                    if application.job_type == 'SASP':
                        dm_embed.set_image(url="https://res.cloudinary.com/dsodx3ntj/image/upload/v1744445310/1_hwtnj7.jpg")
                    elif application.job_type == 'EMS':
                        dm_embed.set_image(url="https://res.cloudinary.com/dsodx3ntj/image/upload/v1744445258/2_n3ynli.jpg")
                    elif application.job_type == 'MECHANIC':
                        dm_embed.set_image(url="https://res.cloudinary.com/dsodx3ntj/image/upload/v1744445290/1_klkkrk.jpg")
                elif application.status == 'HIRED':
                    dm_embed.description = f"**Congratulations! You have been HIRED for the {application.get_job_type_display()} position at Vibe City RP!**"
                    dm_embed.add_field(name="Next Steps", value="Please contact the relevant department lead or HR in Discord for onboarding instructions.", inline=False)
                    if final_feedback:
                        dm_embed.add_field(name="Additional Comments from Hiring Manager", value=final_feedback, inline=False)
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
                    if application.job_type == 'SASP':
                        dm_embed.set_image(url="https://res.cloudinary.com/dsodx3ntj/image/upload/v1744445310/1_hwtnj7.jpg")
                    elif application.job_type == 'EMS':
                        dm_embed.set_image(url="https://res.cloudinary.com/dsodx3ntj/image/upload/v1744445258/2_n3ynli.jpg")
                    elif application.job_type == 'MECHANIC':
                        dm_embed.set_image(url="https://res.cloudinary.com/dsodx3ntj/image/upload/v1744445290/1_klkkrk.jpg")

                await member.send(embed=dm_embed)
                print(f"[JobAppNotify-{application.id}] Sent DM for status {status_text}")
            except Exception as e:
                print(f"[JobAppNotify-{application.id}] Error sending DM: {e}")

            # --- Send to Public Job Responses Channel --- #
            try:
                public_channel_id_setting = getattr(settings, 'DISCORD_JOB_RESPONSES_CHANNEL_ID', None)
                print(f"[JobAppNotify-{application.id}] DISCORD_JOB_RESPONSES_CHANNEL_ID: {public_channel_id_setting}")
                print(f"[JobAppNotify-{application.id}] Bot can see these channels:")
                for ch in bot.get_all_channels():
                    print(f"  - {ch.id}: {ch.name} (type: {type(ch)})")
                if public_channel_id_setting:
                    public_channel_id = int(public_channel_id_setting)
                    public_channel = bot.get_channel(public_channel_id)
                    if not public_channel:
                        print(f"[JobAppNotify-{application.id}] Public responses channel not found: {public_channel_id}")
                    else:
                        print(f"[JobAppNotify-{application.id}] Sending to public channel: {public_channel.name} (ID: {public_channel.id})")
                        public_embed = discord.Embed(
                            title=f"Job Application Update: {application.get_job_type_display()}",
                            color=status_color
                        )
                        mention = f"<@{applicant_discord_id}>"
                        # Tailor message based on status
                        if application.status == 'HIRED':
                            public_embed.description = f"🎉 **Congratulations!**"
                            public_embed.add_field(
                                name="New Team Member",
                                value=f"{mention} has been **HIRED** for the **{application.get_job_type_display()}** team!",
                                inline=False
                            )
                            public_embed.add_field(
                                name="Achievement",
                                value="Successfully completed the application and interview process.",
                                inline=False
                            )
                            public_embed.set_footer(text="Vibe City RP | Department Recruitment")
                        elif application.status == 'INTERVIEW_PENDING':
                            public_embed.description = f"📋 **Application Update**"
                            public_embed.add_field(
                                name="Status Update",
                                value=f"{mention}'s application for **{application.get_job_type_display()}** has passed the initial review.",
                                inline=False
                            )
                            public_embed.add_field(
                                name="Next Stage",
                                value="Moving forward to the interview stage.",
                                inline=False
                            )
                            public_embed.set_footer(text="Vibe City RP | Department Recruitment")
                        elif application.status == 'FIRED':
                            public_embed.description = f"🚫 **Employment Update**"
                            public_embed.add_field(
                                name="Status Update",
                                value=f"{mention} has been **FIRED** from the **{application.get_job_type_display()}** team.",
                                inline=False
                            )
                            public_embed.set_footer(text="Vibe City RP | Department Recruitment")
                        elif application.status == 'REJECTED' or application.status == 'REJECTED_INTERVIEW':
                            stage = "Form Stage" if application.status == 'REJECTED' else "Interview Stage"
                            public_embed.description = f"📝 **Application Update**"
                            public_embed.add_field(
                                name="Status Update",
                                value=f"Regarding {mention}'s application for **{application.get_job_type_display()}**:",
                                inline=False
                            )
                            public_embed.add_field(
                                name="Decision",
                                value=f"The application was not successful at the **{stage}**.",
                                inline=False
                            )
                            public_embed.set_footer(text="Vibe City RP | Department Recruitment")
                        else:
                            public_embed = None
                        # Add appropriate image based on status
                        if public_embed:
                            if application.status == 'HIRED':
                                if application.job_type == 'SASP':
                                    public_embed.set_image(url="https://res.cloudinary.com/dsodx3ntj/image/upload/v1744445310/2_menxjj.jpg")
                                elif application.job_type == 'EMS':
                                    public_embed.set_image(url="https://res.cloudinary.com/dsodx3ntj/image/upload/v1744445258/1_vakqr9.jpg")
                                elif application.job_type == 'MECHANIC':
                                    public_embed.set_image(url="https://res.cloudinary.com/dsodx3ntj/image/upload/v1744445290/2_snyeko.jpg")
                            elif application.status == 'FIRED' or 'REJECTED' in application.status:
                                if application.job_type == 'SASP':
                                    public_embed.set_image(url="https://res.cloudinary.com/dsodx3ntj/image/upload/v1744445310/1_hwtnj7.jpg")
                                elif application.job_type == 'EMS':
                                    public_embed.set_image(url="https://res.cloudinary.com/dsodx3ntj/image/upload/v1744445258/2_n3ynli.jpg")
                                elif application.job_type == 'MECHANIC':
                                    public_embed.set_image(url="https://res.cloudinary.com/dsodx3ntj/image/upload/v1744445290/1_klkkrk.jpg")
                            await public_channel.send(content=f"Application update for <@{applicant_discord_id}>:", embed=public_embed)
                            print(f"[JobAppNotify-{application.id}] Sent PUBLIC response to channel {public_channel.name}.")
                else:
                    print(f"[JobAppNotify-{application.id}] DISCORD_JOB_RESPONSES_CHANNEL_ID not set. Skipping public notification.")
            except Exception as e:
                print(f"[JobAppNotify-{application.id}] Error sending to PUBLIC responses channel: {e}")

        except Exception as e:
            print(f"[JobAppNotify-{application.id}] General error: {e}")
            import traceback
            traceback.print_exc()

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
            submitted_at_str = application.submitted_at.astimezone(pytz.timezone('Asia/Kolkata')).strftime("%Y-%m-%d %H:%M IST")

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

def fire_employee(user, job_type, feedback=None):
    """Removes job role from a user when they are fired and updates their application status."""
    print(f"[FireEmployee-{user.id}] Received request to fire employee.") # DEBUG
    if not bot_ready.is_set():
        print(f"[FireEmployee-{user.id}] Bot not ready, waiting...")
        bot_ready.wait(timeout=15)
        if not bot_ready.is_set():
            print(f"[FireEmployee-{user.id}] Bot did not become ready after wait.")
            return
        print(f"[FireEmployee-{user.id}] Bot became ready after wait.")

    if not bot:
        print(f"[FireEmployee-{user.id}] Bot object is None.")
        return
    
    if not bot.loop.is_running():
        print(f"[FireEmployee-{user.id}] Bot event loop is not running.")
        return

    async def send():
        print(f"[FireEmployee-{user.id}] Entering async send() coroutine.")
        try:
            user_discord_id = await sync_to_async(lambda: user.discord_id)()
            if not user_discord_id:
                print(f"[FireEmployee-{user.id}] User has no Discord ID.")
                return

            # Get the guild and member
            guild_id = int(settings.DISCORD_GUILD_ID)
            guild = bot.get_guild(guild_id)
            if not guild:
                print(f"[FireEmployee-{user.id}] Guild not found: {guild_id}")
                return
            
            member = await guild.fetch_member(int(user_discord_id))
            if not member:
                print(f"[FireEmployee-{user.id}] Member not found: {user_discord_id}")
                return

            # Remove all job-related roles
            all_job_roles = [
                int(settings.DISCORD_SASP_INTERVIEW_ROLE_ID),
                int(settings.DISCORD_SASP_HIRED_ROLE_ID),
                int(settings.DISCORD_EMS_INTERVIEW_ROLE_ID),
                int(settings.DISCORD_EMS_HIRED_ROLE_ID),
                int(settings.DISCORD_MECHANIC_INTERVIEW_ROLE_ID),
                int(settings.DISCORD_MECHANIC_HIRED_ROLE_ID)
            ]

            for role_id in all_job_roles:
                try:
                    role = guild.get_role(role_id)
                    if role and role in member.roles:
                        await member.remove_roles(role)
                        print(f"[FireEmployee-{user.id}] Removed role {role_id} from {member.name}")
                except Exception as e:
                    print(f"[FireEmployee-{user.id}] Error removing role {role_id}: {e}")

            # Update user's employment status
            if job_type == 'SASP':
                user.is_sasp_employee = False
            elif job_type == 'EMS':
                user.is_ems_employee = False
            elif job_type == 'MECHANIC':
                user.is_mechanic_employee = False
            
            await sync_to_async(user.save)()
            print(f"[FireEmployee-{user.id}] Updated user employment status")

            # Update job application status
            from jobs.models import JobApplication
            from django.utils import timezone
            
            job_app = await sync_to_async(lambda: JobApplication.objects.filter(
                applicant=user,
                job_type=job_type,
                status='HIRED'
            ).first())()
            
            if job_app:
                print(f"[FireEmployee-{user.id}] Found job application {job_app.id} to update")
                job_app.status = 'FIRED'
                job_app.interview_feedback = feedback if feedback else "No reason provided"
                job_app.interview_reviewed_at = timezone.now()
                await sync_to_async(job_app.save)()
                print(f"[FireEmployee-{user.id}] Updated job application status to FIRED")

                # Send notification about the status change
                try:
                    send_notification_func = import_string('discord_bot.bot.send_job_application_result')
                    await sync_to_async(send_notification_func)(job_app)
                    print(f"[FireEmployee-{user.id}] Sent job application result notification")
                except Exception as e:
                    print(f"[FireEmployee-{user.id}] Error sending job application notification: {e}")

            # Send DM to user
            try:
                dm_embed = discord.Embed(
                    title="Employment Status Update",
                    description=f"You have been removed from the {job_type} team.",
                    color=discord.Color.red()
                )
                dm_embed.add_field(
                    name="What This Means",
                    value="Your job role has been removed from Discord. You may reapply for this position after a cooldown period.",
                    inline=False
                )
                if feedback:
                    dm_embed.add_field(
                        name="Reason",
                        value=feedback,
                        inline=False
                    )
                await member.send(embed=dm_embed)
                print(f"[FireEmployee-{user.id}] Sent firing notification DM to {member.name}")
            except Exception as e:
                print(f"[FireEmployee-{user.id}] Error sending DM to user: {e}")

        except Exception as e:
            print(f"[FireEmployee-{user.id}] General error in fire_employee: {e}")
            import traceback
            traceback.print_exc()

    # Schedule the async function to run in the bot's event loop
    print(f"[FireEmployee-{user.id}] Scheduling send() coroutine.")
    asyncio.run_coroutine_threadsafe(send(), bot.loop)
    print(f"[FireEmployee-{user.id}] Coroutine scheduled.")