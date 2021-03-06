#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Utility commands to be used throughout the cogs
"""

import asyncio
import datetime
import os
import re
import sys
import traceback as tb
from enum import Enum
from typing import Optional, Tuple, Union

import discord
from pytz import timezone

EMOJI_REGEX = re.compile(
    "["
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F680-\U0001F6FF"  # transport & map symbols
    "\U0001F1E0-\U0001F1FF"  # flags (iOS)
    "]+",
    flags=re.UNICODE,
)


class LogLevel(Enum):
    INFO = 1
    WARNING = 2
    ERROR = 3


def log(message, level=LogLevel.INFO, error=None):
    if level is LogLevel.INFO:
        # Do basic output
        print(message)
        if error:
            tb.print_exception(type(error), error, error.__traceback__)
    else:
        # Do output, but more warny
        print(message, file=sys.stderr)
        if error:
            tb.print_exception(type(error), error, error.__traceback__,
                               file=sys.stderr)

        if level is LogLevel.ERROR:
            print("Critical error above, exiting program", file=sys.stderr)
            raise SystemExit


# Create a regex for finding id's within messages
re_message_id = re.compile(r"\d{18}")


async def find_id(msg):
    result = re_message_id.search(msg)
    if result:
        return int(msg[result.start():result.end()])
    return False


async def get_confirmation(channel, user, bot, message,
                           embed: discord.Embed = None):
    confirm_message = await channel.send(message, embed=embed)
    await confirm_message.add_reaction("👍")
    await confirm_message.add_reaction("👎")

    def check(check_reaction, check_user):
        return ((check_user == user)
                and check_reaction.message.id == confirm_message.id
                and str(check_reaction.emoji) in ("👍", "👎"))

    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=30.0,
                                            check=check)
    except asyncio.TimeoutError:
        await confirm_message.delete()
        return False, "Timeout"
    else:
        await confirm_message.delete()
        if str(reaction.emoji) == "👍":
            return True, None
        return False, "Rejected"


def get_utc_time(timestamp: int = None) -> datetime.datetime:
    if timestamp is None:
        return datetime.datetime.utcnow()

    return datetime.datetime.utcfromtimestamp(timestamp)


def get_uk_time(utc_time: datetime.datetime = None) -> datetime.datetime:
    # Converts a naive datetime to an aware datetime in UTC
    utc_time = utc_time.replace(tzinfo=datetime.timezone.utc)

    tz = timezone('Europe/London')
    if utc_time is None:
        return get_utc_time().astimezone(tz)

    return utc_time.astimezone(tz)


ChannelType = Union[discord.abc.GuildChannel,
                    Tuple[discord.abc.GuildChannel, ...]]


def find_channel_by_name(
    name: str,
    guild: discord.Guild,
    channel_types: ChannelType = discord.TextChannel
) -> Optional[discord.abc.GuildChannel]:
    """
    Finds a channel within a guild by name. Name is case-insensitive.

    Optionally specify type(s) that the channel.
    """
    for channel in guild.channels:
        if (
            isinstance(channel, channel_types)
            and channel.name.lower() == name.lower()
        ):
            return channel


def find_role_by_name(
    name: str,
    guild: discord.Guild,
) -> Optional[discord.Role]:
    """
    Finds a role within a guild by name. Name is case-insensitive.
    """
    for role in guild.roles:
        if role.name.lower() == name.lower():
            return role


class RemoveReaction:
    """
    A context manager that removes a reaction on exit.

    This is intended to be used with the `on_raw_reaction_add` event
    within a cog.
    """

    def __init__(self, cog, payload):
        self.cog = cog
        self.payload = payload

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        channel = await self.cog.bot.fetch_channel(self.payload.channel_id)
        message = await channel.fetch_message(self.payload.message_id)
        await message.remove_reaction(self.payload.emoji, self.payload.member)


def is_admin(user):
    for role in user.roles:
        if role.name.lower() == "admin":
            return True

    return False


async def add_role(member, role_id):
    role = member.guild.get_role(role_id)
    if role:
        await member.add_roles(role)


async def remove_role(member, role_id):
    role = member.guild.get_role(role_id)
    if role:
        await member.remove_roles(role)


def demojify(s: str):
    """
    Removes emojis from the given string
    """
    return EMOJI_REGEX.sub("", s)


async def send_and_delete_file(messageable: discord.abc.Messageable,
                               filename: str):
    """
    Sends a file specified by the file to the messageable,
    and deletes the file regardless of message success
    """
    try:
        with open(filename, "rb") as f:
            file = discord.File(f)
            await messageable.send(file=file)
    finally:
        if os.path.exists(filename):
            os.remove(filename)
