#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Cog for the vibin channel
"""

import asyncio
import datetime as dt

import discord
from discord.ext import commands, tasks

import utils as ut

PLAYLIST_LINK = "https://open.spotify.com/playlist/45ugA3rSKs5C9jpuC8ihva"
START_TIME = dt.time(hour=1, minute=0, second=0)
LENGTH = dt.timedelta(hours=3)


class VibinCog(commands.Cog, name="Vibin"):
    """Vibe."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._vibin = False

        self.vibin_loop.start()

    @property
    def now(self):
        return ut.get_uk_time()

    @property
    def start_dt(self):
        start_dt = ut.uk_normalize_time(
            self.now.replace(
                hour=START_TIME.hour,
                minute=START_TIME.minute,
                second=START_TIME.second,
                microsecond=0,
            )
        )
        return start_dt

    @property
    def end_dt(self):
        return ut.uk_normalize_time(self.start_dt + LENGTH)

    async def change_vibin(self, visibility: bool):
        if visibility == self._vibin:
            return
        for guild in self.bot.guilds:
            text_channel = discord.utils.get(guild.text_channels, name="vibin")
            voice_channel = discord.utils.get(
                guild.voice_channels, name="vibin")
            if text_channel is None or voice_channel is None:
                continue
            member_role = discord.utils.get(guild.roles, name="Member")
            if member_role is None:
                continue
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
        self._vibin = visibility

    @tasks.loop()
    async def vibin_loop(self):
        end_dt = self.end_dt
        if end_dt < self.now:
            end_dt = ut.uk_normalize_time(end_dt + dt.timedelta(days=1))
        sleep_timedelta = (
            self.end_dt
            if self._vibin
            else self.start_dt
        ) - self.now
        sleep_time = sleep_timedelta.seconds
        await asyncio.sleep(sleep_time)
        await self.change_vibin(False if self._vibin else True)

    @vibin_loop.before_loop
    async def before_vibin_loop(self):
        await self.bot.wait_until_ready()
        if self.start_dt <= self.now <= self.end_dt:
            await self.change_vibin(True)
        else:
            await self.change_vibin(False)


def setup(bot: commands.Bot):
    bot.add_cog(VibinCog(bot))
