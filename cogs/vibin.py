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


class VibinCog(commands.Cog, name="Vibin"):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def change_vibin(
        self,
        guild: discord.Guild,
        visibility: bool,
    ):
        channel = ut.find_channel_by_name("vibin", guild)
        if channel is None:
            return
        role = ut.find_role_by_name("Member", guild)
        if role is None:
            return
        await channel.set_permissions(role, read_messages=visibility)
        if visibility:
            await channel.purge(limit=10000)
            msg = await channel.send(PLAYLIST_LINK)
            await msg.pin()

    @commands.Cog.listener()
    async def on_ready(self):
        while True:
            now = dt.datetime.now()
            for visibility, time in zip(
                (True, False),
                (
                    now.replace(day=now.day, hour=1, minute=0, second=0),
                    now.replace(day=now.day, hour=4, minute=0, second=0),
                ),
            ):
                now = dt.datetime.now()
                delay = (time - now).total_seconds() % 86400
                await asyncio.sleep(delay)
                for guild in self.bot.guilds:
                    await self.change_vibin(guild, visibility)


def setup(bot: commands.Bot):
    bot.add_cog(VibinCog(bot))
