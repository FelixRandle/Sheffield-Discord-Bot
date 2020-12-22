#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Cog for the vibin channel
"""

import asyncio
import datetime as dt

import discord
import utils as ut
from discord.ext import commands


PLAYLIST_LINK = "https://open.spotify.com/playlist/45ugA3rSKs5C9jpuC8ihva"
START_TIME = dt.time(hour=9, minute=23, second=0)
END_TIME = dt.time(hour=4, minute=0, second=0)


class VibinCog(commands.Cog, name="Vibin"):
    """Vibe."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

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
            text_channel = discord.utils.get(guild.text_channels, name="vibin")
            voice_channel = discord.utils.get(
                guild.voice_channels, name="vibin")
            if text_channel is None or voice_channel is None:
                return
            member_role = discord.utils.get(guild.roles, name="Member")
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

    @commands.Cog.listener()
    async def on_ready(self):
        first_loop = True
        while True:
            if (
                not first_loop
                or not START_TIME <= dt.datetime.now().time() <= END_TIME
            ):
                await self.change_vibin_at(START_TIME, True)
                first_loop = False
            await self.change_vibin_at(END_TIME, False)


def setup(bot: commands.Bot):
    bot.add_cog(VibinCog(bot))
