import discord
from discord.ext import commands
from datetime import timedelta
import asyncio
import os

# Bot setup with required intents
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix=".", intents=intents)

@bot.event
async def on_ready():
    print(f'Bot is ready and logged in as {bot.user}')
    await bot.change_presence(activity=discord.Game(name="moderation"))

@bot.command()
async def ping(ctx):
    """Check bot's latency"""
    await ctx.send(f"Pong! Latency: {round(bot.latency * 1000)}ms")

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    """Kick a member"""
    try:
        await member.kick(reason=reason)
        await ctx.send(f'{member.mention} was kicked. Reason: {reason}')
    except:
        await ctx.send('Failed to kick member.')

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    """Ban a member"""
    try:
        await member.ban(reason=reason)
        await ctx.send(f'{member.mention} was banned. Reason: {reason}')
    except:
        await ctx.send('Failed to ban member.')

@bot.command()
@commands.has_permissions(manage_channels=True)
async def mute(ctx, member: discord.Member, duration: int = 10):
    """Mute a member for specified minutes"""
    try:
        await member.timeout(timedelta(minutes=duration))
        await ctx.send(f'{member.mention} has been muted for {duration} minutes.')
    except:
        await ctx.send('Failed to mute member.')

@bot.command()
@commands.has_permissions(manage_channels=True)
async def unmute(ctx, member: discord.Member):
    """Unmute a member"""
    try:
        await member.timeout(None)
        await ctx.send(f'{member.mention} has been unmuted.')
    except:
        await ctx.send('Failed to unmute member.')

@bot.command()
@commands.has_permissions(manage_channels=True)
async def lock(ctx):
    """Lock the current channel"""
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.send('Channel locked.')

@bot.command()
@commands.has_permissions(manage_channels=True)
async def unlock(ctx):
    """Unlock the current channel"""
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
    await ctx.send('Channel unlocked.')

@bot.command()
@commands.has_permissions(manage_channels=True)
async def slowmode(ctx, seconds: int):
    """Set slowmode delay"""
    try:
        await ctx.channel.edit(slowmode_delay=seconds)
        await ctx.send(f'Slowmode set to {seconds} seconds.')
    except:
        await ctx.send('Failed to set slowmode.')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have permission to use this command.")
    elif isinstance(error, commands.MemberNotFound):
        await ctx.send("Member not found.")
    else:
        await ctx.send(f"An error occurred: {str(error)}")

# For macOS SSL verification
if os.name == 'posix':  # macOS or Linux
    try:
        import certifi
        os.environ['SSL_CERT_FILE'] = certifi.where()
    except ImportError:
        pass

# Run the bot
def main():
    try:
        bot.run('MTMxOTY2MzQyNTg5ODY3NjMyNA.Gy7crb.pRHdmSH9rs4ckWtxU-aEV_Nlzk8P1IChVlmwjk')
    except Exception as e:
        print(f"Error starting bot: {e}")

if __name__ == "__main__":
    main()