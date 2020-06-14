#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
An example cog to show how things should be done.

Also provides a simple base for starting a new cog.
"""
# In this case, discord import is not needed, in some cases it may be.
# import discord
from discord.ext import commands
from enum import Enum
import time

import database as db


class LoggingCog(commands.Cog):
    """Create a class that extends Cog to make our functionality in."""

    def __init__(self, bot):
        """Save our bot argument that is passed in to the class."""
        self.bot = bot

    @commands.Cog.listener('on_message')
    async def log_message_add(self, message):
        if message.author.bot:
            return
        await db.log_message(message.author.id, message.id,
                             message.content.encode('unicode-escape'), int(time.time()))

    @commands.Cog.listener('on_message_delete')
    async def on_message_delete(self, message):
        # TODO Implement
        pass

    @commands.Cog.listener('on_bulk_message_delete')
    async def on_bulk_message_delete(self, messages):
        # TODO Implement
        pass

    @commands.Cog.listener('on_raw_message_delete')
    async def on_raw_message_delete(self, payload):
        # TODO Implement
        pass

    @commands.Cog.listener('on_raw_bulk_message_delete')
    async def on_raw_bulk_message_delete(self, payload):
        # TODO Implement
        pass

    @commands.Cog.listener('on_message_edit')
    async def on_message_edit(self, before, after):
        # TODO Implement
        pass

    @commands.Cog.listener('on_raw_message_edit')
    async def on_raw_message_edit(self, payload):
        # TODO Implement
        pass

    @commands.Cog.listener('on_guild_channel_delete')
    async def on_bulk_message_delete(self, channel):
        # TODO Implement
        pass

    @commands.Cog.listener('on_guild_channel_create')
    async def on_guild_channel_create(self, channel):
        # TODO Implement
        pass

    @commands.Cog.listener('on_guild_channel_update')
    async def on_guild_channel_update(self, before, after):
        # TODO Implement
        pass

    @commands.Cog.listener('on_guild_role_create')
    async def on_guild_role_create(self, role):
        # TODO Implement
        pass

    @commands.Cog.listener('on_guild_role_delete')
    async def on_guild_role_delete(self, role):
        # TODO Implement
        pass

    @commands.Cog.listener('on_guild_role_update')
    async def on_guild_role_update(self, before, after):
        # TODO Implement
        pass

    @commands.Cog.listener('on_member_ban')
    async def on_member_ban(self, guild, user):
        # TODO Implement
        pass

    @commands.Cog.listener('on_member_unban')
    async def on_member_unban(self, guild, user):
        # TODO Implement
        pass

    @commands.Cog.listener('on_invite_create')
    async def on_invite_create(self, invite):
        # TODO Implement
        pass

    @commands.Cog.listener('on_invite_delete')
    async def on_invite_delete(self, invite):
        # TODO Implement
        pass


def setup(bot):
    """
    Add the cog we have made to our bot.

    This function is necessary for every cog file, multiple classes in the
    same file all need adding and each file must have their own setup function.
    """
    bot.add_cog(LoggingCog(bot))
