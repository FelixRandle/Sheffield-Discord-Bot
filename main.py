#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Main file of sheffield uni freshers comp sci discord bot.

Authored by:
Felix Randle
"""
import os

from discord.ext import commands
from dotenv import load_dotenv
from orator import Model
import discord
from pretty_help import PrettyHelp

import utils as ut
from database import db
from models import Guild

# Tells Orator models which database to use
Model.set_connection_resolver(db)

def load_environment():
    # We must load env variables in order to retrieve the bot token
    load_dotenv()

    # Load our login details from environment variables and check they are set
    token = os.getenv("BOT_TOKEN")
    if token is None:
        ut.log("Cannot find required bot token.", ut.LogLevel.ERROR)
    return token

# Set our bot's intents
bot_intents = discord.Intents.default()
bot_intents.members = True
bot_intents.typing = False

# Set our bot's prefix to $. This must be typed before any command
bot = commands.Bot(
    command_prefix="$",
    case_insensitive=True,
    intents=bot_intents,
    help_command=PrettyHelp()
)

def load_cogs():
    # Set cogs that require loading in a specific order
    # They will be loaded in the order of the list, followed by all
    # other cogs in the /cogs folder
    cogs = [
        "core"
    ]

    if os.path.exists("./cogs"):
        for file in os.listdir("./cogs"):
            if file.endswith(".py"):
                cog_name = file[:-3]
                if cog_name not in cogs:
                    cogs.append(cog_name)

    for cog in cogs:
        try:
            bot.load_extension(f'cogs.{cog}')
            ut.log(f'Loaded cog: {cog}')
        except commands.errors.ExtensionNotFound:
            ut.log(f'Failed to load cog: {cog}')

@bot.event
async def on_ready():
    """Run post-launch setup."""
    ut.log(f'{bot.user.name} has successfully connected to Discord!')

    # Ensure all guilds are in the DB (In case we joined one while not running)

    for guild in bot.guilds:
        Guild.first_or_create(id=guild.id)


# Implement errors from
# https://discordpy.readthedocs.io/en/latest/ext/commands/api.html#exceptions
# Not all of these need to be put in, but a fair few would be good.
@bot.event
async def on_command_error(ctx, error):
    """Handle any command errors that may appear."""
    if str(error) != "":
        await ctx.send(error)
    elif isinstance(error, commands.errors.CheckFailure):
        await ctx.send(
            "You do not have the correct permissions for this command."
            "If you believe this is an error, please contact an Admin.")
    elif isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send(
            f"Missing argument: {error.param.name}. "
            "Please add in the argument before running the command again."
        )
    elif isinstance(error, commands.errors.UserInputError):
        await ctx.send(
            "I couldn't recognise one or more of your inputs, "
            "are you sure they're in the correct format. :thinking:"
        )
    elif isinstance(error, commands.errors.CommandNotFound):
        await ctx.send(
            "I don't recognize that command. :thinking:"
        )
    else:
        await ctx.send("Error running command. "
                       "Please try again later or contact an administrator.")
        ut.log("An unhandled error occured whilst a command was run",
               ut.LogLevel.WARNING, error)

if __name__ == '__main__':
    bot_token = load_environment()
    load_cogs()
    # Start the bot
    ut.log("Starting bot...")
    bot.run(bot_token)
