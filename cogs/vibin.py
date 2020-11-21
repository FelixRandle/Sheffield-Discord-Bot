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
        text_channel = ut.find_channel_by_name("vibin", guild)
        voice_channel = ut.find_channel_by_name(
            "vibin", guild, channel_types=discord.VoiceChannel)
        if text_channel is None or voice_channel is None:
            return
        member_role = ut.find_role_by_name("Member", guild)
        if member_role is None:
            return
        await text_channel.set_permissions(member_role, read_messages=visibility)
        await voice_channel.set_permissions(member_role, view_channel=visibility)
        if visibility:
            # Clear the text channel and send playlist link
            await text_channel.purge(limit=10000)
            msg = await text_channel.send(PLAYLIST_LINK)
            await msg.pin()
        else:
            for member in voice_channel.members:
                await member.move_to(None)

    @commands.Cog.listener()
    async def on_ready(self):
        while True:
            now = dt.datetime.now()
            for visibility, time in zip(
                (True, False),
                (
                    now.replace(day=now.day, hour=22, minute=42, second=0),
                    now.replace(day=now.day, hour=22, minute=43, second=0),
                ),
            ):
                now = dt.datetime.now()
                delay = (time - now).total_seconds() % 86400
                await asyncio.sleep(delay)
                for guild in self.bot.guilds:
                    await self.change_vibin(guild, visibility)


def setup(bot: commands.Bot):
    bot.add_cog(VibinCog(bot))
