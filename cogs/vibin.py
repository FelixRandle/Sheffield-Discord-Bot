#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Cog for the vibin channel
"""

import asyncio
import datetime as dt

import discord
import utils as ut
from discord.ext import commands, tasks


PLAYLIST_LINK = "https://open.spotify.com/playlist/45ugA3rSKs5C9jpuC8ihva"
START_TIME = dt.time(hour=1, minute=0, second=0)
END_TIME = dt.time(hour=4, minute=0, second=0)


class VibinCog(commands.Cog, name="Vibin"):
    """Vibe."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.first_loop = True

        self.vibin_loop.start()

    async def change_vibin_at(
        self,
        time: dt.time,
        visibility: bool,
    ):
        now = dt.datetime.now()
        next_time = now.replace(
            hour=time.hour, minute=time.minute, second=time.second)
        delay = (next_time - now).total_seconds() % 86400
        await asyncio.sleep(delay)
        for guild in self.bot.guilds:
            text_channel = ut.find_channel_by_name("vibin", guild)
            voice_channel = ut.find_channel_by_name(
                "vibin", guild, channel_types=discord.VoiceChannel)
            if text_channel is None or voice_channel is None:
                return
            member_role = ut.find_role_by_name("Member", guild)
            if member_role is None:
                return
            if visibility:
                # Clear the text channel and send playlist link
                await text_channel.purge(limit=10000)
                msg = await text_channel.send(PLAYLIST_LINK)
                await msg.pin()
            else:
                for member in voice_channel.members:
                    await member.move_to(None)
            await text_channel.set_permissions(
                member_role, read_messages=visibility)
            await voice_channel.set_permissions(
                member_role, view_channel=visibility)

    @tasks.loop()
    async def vibin_loop(self):
        if (
            not self.first_loop
            or not START_TIME <= dt.datetime.now().time() <= END_TIME
        ):
            await self.change_vibin_at(START_TIME, True)
            self.first_loop = False
        await self.change_vibin_at(END_TIME, False)

    @vibin_loop.before_loop
    async def before_vibin_loop(self):
        await self.bot.wait_until_ready()


def setup(bot: commands.Bot):
    bot.add_cog(VibinCog(bot))
