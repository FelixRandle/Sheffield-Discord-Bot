#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
An example cog to show how things should be done.

Also provides a simple base for starting a new cog.
"""
from discord.ext import commands, tasks

from cogs.core import CoreCog
from models import Message
from models.voice import Voice

VOICE_CHECK_FREQUENCY = 10.0


class LoggingCog(commands.Cog):
    """Create a class that extends Cog to make our functionality in."""

    def __init__(self, bot):
        """Save our bot argument that is passed in to the class."""
        self.bot = bot

        self.voice_channel_check.start()

        CoreCog.add_user_info("Voice Time", self.get_user_voice_time,
                              True)

    @staticmethod
    def get_user_voice_time(user):
        try:
            time = Voice.where('user_id', user.id) \
                .where('guild_id', user.guild.id).first().time
            secs = time % 60
            mins = time // 60 % 60
            hrs = time // 60 // 60
            return f"{hrs} Hours {mins} Minutes {secs} Seconds"
        except AttributeError:
            return "No Voice Time"

    @commands.Cog.listener('on_message')
    async def log_message_add(self, message):
        if message.author.bot:
            return

        Message.create(id=message.id, author_id=message.author.id,
                       content=message.content)

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

    @tasks.loop(seconds=VOICE_CHECK_FREQUENCY)
    async def voice_channel_check(self):
        """
        Task loop that updates the time users have spent
        in voice chat.
        """

        for guild in self.bot.guilds:
            for channel in guild.voice_channels:
                for member in channel.members:
                    Voice.first_or_create(user_id=member.id,
                                          guild_id=guild.id)

                    Voice.where('user_id', member.id)\
                        .where('guild_id', guild.id)\
                        .increment('time', VOICE_CHECK_FREQUENCY)


def setup(bot):
    """
    Add the cog we have made to our bot.

    This function is necessary for every cog file, multiple classes in the
    same file all need adding and each file must have their own setup function.
    """
    bot.add_cog(LoggingCog(bot))
