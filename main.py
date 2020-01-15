"""
Main file of sheffield uni freshers comp sci discord bot.

Authored by:
Felix Randle
"""
import os
from discord.ext import commands

# Load our login details from environment variables and check they are set
BOT_TOKEN = os.getenv("BOT_TOKEN")

if BOT_TOKEN is None:
    raise("Cannot find required bot token.")

# Set our bot's prefix to ! this must be typed before any command
bot = commands.Bot(command_prefix="!")


@bot.event
async def on_ready():
    """Run post-launch setup."""
    print(f'{bot.user.name} has successfully connected to Discord!')

    # Load all of our cogs
    if os.path.exists("./cogs"):
        for file in os.listdir("./cogs"):
            if file.endswith(".py"):
                bot.load_extension("cogs." + file[:-3])
                print(f"Loaded cog {file[:-3]}")


@bot.event
async def on_member_join(member):
    """Send user a welcome message."""
    await member.create_dm()
    await member.dm_channel.send(
        f'Hey {member.name}, welcome to the University of Sheffield Computer '
        'Science Freshers Discord!\n'
        'We like to know who we\'re talking to, so please change your '
        'nickname on the server to include your real name in some way.\n'
        'Apart from that, have fun on the server, get to know people and '
        'feel free to ask any questions about the course that you may have, '
        'we\'re all here to help each other!\n'
        'Many thanks,\n'
        'The Discord Server Admin Team'
    )


@bot.event
async def on_command_error(ctx, error):
    """Handle any command errors that may appear."""
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send(
            "You do not have the correct permissions for this command."
            "If you believe this is an error, please contact an Admin.")


# Start the bot
print("Starting bot...")
bot.run(BOT_TOKEN)
