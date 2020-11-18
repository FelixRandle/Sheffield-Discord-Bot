#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Utility commands to be used throughout the cogs
"""

import asyncio
import datetime
import os
import re
from typing import Optional, Tuple, Union

import discord
from pytz import timezone

ENVIRONMENT = os.getenv("ENVIRONMENT")

# Create a regex for finding id's within messages
re_message_id = re.compile(r"\d{18}")


async def find_id(msg):
    result = re_message_id.search(msg)
    if result:
        return int(msg[result.start():result.end()])
    return False


async def get_confirmation(channel, user, bot, message):
    confirm_message = await channel.send(message)
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
    for channel in guild.channels:
        if isinstance(channel, channel_types) and channel.name == name:
            return channel


def find_role_by_name(
    name: str,
    guild: discord.Guild,
) -> Optional[discord.Role]:
    for role in guild.roles:
        if role.name == name:
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


def log_error(error):
    # At some point, I want to perform different operations here between
    # Production and development.
    raise Exception from error


def log_info(message):
    # Again, at some point this will be different between production and
    # Development.
    print(message)
