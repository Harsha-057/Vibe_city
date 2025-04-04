import discord
from discord.ext import commands
import asyncio
import os
from django.conf import settings
import threading

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
                title="New Whitelist Application",
                description=f"A new application has been submitted by {application.user.discord_tag}",
                color=discord.Color.blue()
            )
            
            embed.add_field(name="Age", value=str(application.age), inline=True)
            embed.add_field(name="Submitted At", value=application.created_at.strftime("%Y-%m-%d %H:%M"), inline=True)
            embed.add_field(name="Status", value="Pending Review", inline=True)
            
            embed.set_thumbnail(url=application.user.avatar_url)
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
                title=f"Application {status_text}",
                description=f"{application.user.username}'s whitelist application has been {application.status}.",
                color=status_color
            )
            
            if application.feedback:
                embed.add_field(name="Feedback", value=application.feedback, inline=False)
            
            embed.add_field(name="Reviewed By", value=application.reviewed_by.discord_tag or application.reviewed_by.username, inline=True)
            embed.add_field(name="Reviewed At", value=application.reviewed_at.strftime("%Y-%m-%d %H:%M"), inline=True)
            
            embed.set_thumbnail(url=application.user.avatar_url)
            
            await channel.send(embed=embed)
            
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
                
                user_embed = discord.Embed(
                    title=f"Your Application Has Been {status_text}",
                    color=status_color
                )
                
                if application.status == 'approved':
                    user_embed.description = "Congratulations! Your whitelist application for Vibe City RP has been approved."
                    user_embed.add_field(name="Next Steps", value="You can now join our server! Check the #server-info channel for connection details.", inline=False)
                else:
                    user_embed.description = "We're sorry, but your whitelist application for Vibe City RP has been rejected."
                    user_embed.add_field(name="What Next?", value="You can reapply after addressing the feedback below.", inline=False)
                
                if application.feedback:
                    user_embed.add_field(name="Feedback", value=application.feedback, inline=False)
                
                await member.send(embed=user_embed)
            except Exception as e:
                print(f"Error sending DM to user: {e}")
        
        except Exception as e:
            print(f"Error sending application result notification: {e}")
    
    asyncio.run_coroutine_threadsafe(send(), bot.loop)