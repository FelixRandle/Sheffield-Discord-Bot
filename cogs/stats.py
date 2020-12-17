#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
An extension for providing message-related statistics
"""

import re
import datetime as dt

import matplotlib.pyplot as plt
# In this case, discord import is not needed, in some cases it may be.
# import discord
from discord.ext import commands


EMOJI_REGEX = re.compile(
    "["
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F680-\U0001F6FF"  # transport & map symbols
    "\U0001F1E0-\U0001F1FF"  # flags (iOS)
    "]+",
    flags=re.UNICODE,
)


class StatsCog(commands.Cog, name="Statistics"):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="historyGraph",
        help=(
            "Creates a graph of message frequency within a given timeframe. "
            "Defaults to messages in the last 30 days in the current channel"
        )
    )
    @commands.has_role("Member")
    async def historyGraph(self, ctx, channel=None, days: int = 30):
        """
        A command that generates a graph of message frequency against date.

        Uses `matplotlib.pyplot` to create the graph,
        and exports a temporary graph to be sent.

        The graph is deleted after being successfully sent
        """
        if not ctx.message.channel_mentions:
            channel = ctx.channel
        else:
            channel = ctx.message.channel_mentions[0]

        # Retrieves the current time
        now = dt.datetime.now()
        # Retrives the current date as a datetime from midnight today
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)

        dates = []
        message_nums = []

        # Calculates the oldest day to look at
        date = today - dt.timedelta(days=days - 1)

        for _ in range(days):
            # Adds the date label
            dates.append(date.strftime("%Y-%m-%d"))

            # Retrieves the history of messages
            history = channel.history(
                limit=None,
                after=date,
                before=(
                    date
                    + dt.timedelta(days=1)
                    - dt.timedelta(microseconds=1)
                )
            )
            # Finds the number of messages in it
            num_messages = 0
            async for _ in history:
                num_messages += 1

            message_nums.append(num_messages)

            date += dt.timedelta(days=1)


def setup(bot):
    """
    Add the cog we have made to our bot.

    This function is necessary for every cog file, multiple classes in the
    same file all need adding and each file must have their own setup function.
    """
    bot.add_cog(StatsCog(bot))
