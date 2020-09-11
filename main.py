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

import utils as ut
from database import db
from models import Guild, User

# We must load env variables in order to retrieve the bot token
load_dotenv()

# Load our login details from environment variables and check they are set
BOT_TOKEN = os.getenv("BOT_TOKEN")
if BOT_TOKEN is None:
    raise Exception("Cannot find required bot token.")

# Set our bot's prefix to $. This must be typed before any command
bot = commands.Bot(command_prefix="$", case_insensitive=True)

# Load all of our cogs
if os.path.exists("./cogs"):
    for file in os.listdir("./cogs"):
        if file.endswith(".py"):
            bot.load_extension("cogs." + file[:-3])
            ut.log_info(f"Loaded cog {file[:-3]}")

# Tells Orator models which database to use
Model.set_connection_resolver(db)


@bot.event
async def on_ready():
    """Run post-launch setup."""
    ut.log_info(f'{bot.user.name} has successfully connected to Discord!')

    # Ensure all guilds are in the DB (In case we joined one while not running)

    for guild in bot.guilds:
        Guild.first_or_create(id=guild.id)


@bot.event
async def on_guild_join(guild):
    registering_id = None
    member_id = None
    for role in guild.roles:
        if role.name.lower() == "registering":
            registering_id = role.id
        if role.name.lower() == "member":
            member_id = role.id

    Guild.first_or_create(
        id=guild.id, registering_id=registering_id, member_id=member_id)


@bot.event
async def on_member_join(member):
    """Send user a welcome message."""
    if member.bot:
        return

    await member.create_dm()
    await member.dm_channel.send(
        f'Hey {member.name}, welcome to the (unofficial) University of '
        'Sheffield Computer Science Discord!\n'
        'We like to know who we\'re talking to, so please change your '
        'nickname on the server to include your real name in some way.\n'
        'Apart from that, have fun on the server, get to know people and '
        'feel free to ask any questions about the course that you may have, '
        'we\'re all here to help each other!\n'
        'Many thanks,\n'
        'The Discord Server Admin Team\n\n'
        'As a note, all messages that you send on the server are logged.\n'
        'This is to help us in the case of messages that contain'
        'offensive content and need to be reported.\n'
        'If you would like your logged messages to be'
        'removed for any reason, please contact <@247428233086238720>.'
    )
    guild = Guild.find(member.guild.id)

    User.first_or_create(id=member.id, guild_id=guild.id)

    role_id = guild.registering_id
    await add_role(member, role_id)


@bot.event
async def on_raw_reaction_add(payload):
    if payload.member.bot:
        return

    guild = Guild.find(payload.guild_id)
    expected_id = guild.welcome_message_id
    if payload.message_id == expected_id:
        message = await payload.member.guild.get_channel(payload.channel_id)\
            .fetch_message(payload.message_id)
        await message.remove_reaction(payload.emoji, payload.member)
        if payload.emoji.name == u"\u2705":
            registering_id = guild.registering_id
            member_id = guild.member_id

            await add_role(payload.member, member_id)
            await remove_role(payload.member, registering_id)

        elif payload.emoji.name == u"\u274E":
            await payload.member.guild.kick(payload.member,
                                            reason="Rejected T's&C's")


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
        ut.log_error(error)


async def add_role(member, role_id):
    role = member.guild.get_role(role_id)
    if role:
        await member.add_roles(role)


async def remove_role(member, role_id):
    role = member.guild.get_role(role_id)
    if role:
        await member.remove_roles(role)

# Start the bot
ut.log_info("Starting bot...")
bot.run(BOT_TOKEN)
