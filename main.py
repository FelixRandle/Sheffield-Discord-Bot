"""
Main file of sheffield uni freshers comp sci discord bot.

Authored by:
Felix Randle
"""
import os
from discord.ext import commands

# Load our login details from environment variables and check they are set
BOT_TOKEN = os.getenv("BOT_TOKEN")
SQL_USER = os.getenv("SQL_USER")
SQL_PASS = os.getenv("SQL_PASS")

if BOT_TOKEN is None or SQL_USER is None or SQL_PASS is None:
    print("Cannot find required environment variables. Exiting Program...")
    exit()

# Set our bot's prefix to ! this must be typed before any command
bot = commands.Bot(command_prefix="!")


@bot.event
async def on_ready():
    """Run post-launch setup."""
    print(f'{bot.user.name} has successfully connected to Discord!')

    # Load all of our cogs
    if os.path.exists("./cogs"):
        for file in os.listdir("./cogs"):
            bot.load_extension("cogs." + file[:-3]) if file.endswith(".py") \
                else None

    # Connect to SQL database to store user data.


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


print("Starting bot...")
bot.run(BOT_TOKEN)
