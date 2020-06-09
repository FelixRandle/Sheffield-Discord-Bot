#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Cog for organising polls"""

import datetime

import discord
from discord.ext import commands

import database as db
import utils as ut
import re

DURATION_REGEX = re.compile(
    r"((?P<hours>\d+?)h)?((?P<minutes>\d+?)m)?((?P<seconds>\d+?)s)?")


class PollsCog(commands.Cog, name="Polls"):
    """Class for polls cog"""

    def __init__(self, bot):
        """Save our bot argument that is passed in to the class."""
        self.bot = bot

    async def parse_time_as_delta(self, time: str):
        match = DURATION_REGEX.match(time)
        if match:
            values_dict = match.groupdict()
            for key in values_dict:
                if values_dict[key] is None:
                    values_dict[key] = 0
                values_dict[key] = int(values_dict[key])

            return datetime.timedelta(**values_dict)

    @commands.command(
        name="createpoll",
        help="Creates a poll. You can add responses to it later")
    @commands.has_role("Member")
    async def create_poll(self, ctx, title, duration=None):
        """
        Allows a user to create a poll.

        Users are limited to one ongoing poll
        """

        user_poll = await db.user_has_poll(ctx.author.id)
        if user_poll:
            await ctx.send("You have a poll ongoing! Contact an adminstrator "
                           "if you think this is a mistake")
        else:
            if duration is None:
                duration = datetime.timedelta(hours=1)
            else:
                duration = await self.parse_time_as_delta(duration)

            if not duration:
                await ctx.send("Poll must have a valid duration "
                               "that is greater than zero")

            end_date = datetime.datetime.now() + duration
            description = end_date.strftime("Poll ends: %d/%m/%Y %H:%M:%S")

            embed = discord.Embed(title=title, description=description,
                                  color=0x0000aa)
            message = await ctx.send(embed=embed)

            await db.user_create_poll(ctx.author.id, message.id,
                                      title, int(end_date.timestamp()))


def setup(bot):
    """
    Add the cog we have made to our bot.

    This function is necessary for every cog file, multiple classes in the
    same file all need adding and each file must have their own setup function.
    """
    bot.add_cog(PollsCog(bot))
