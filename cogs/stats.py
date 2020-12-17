#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
An extension for providing message-related statistics
"""

import datetime as dt
import os
import re

import discord
import matplotlib.pyplot as plt
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
        oldest_day = today - dt.timedelta(days=days - 1)

        date = oldest_day
        with ctx.typing():
            for _ in range(days):
                # Adds the date label
                date_str = date.strftime("%Y-%m-%d")
                dates.append(date_str)

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

        # Sets x-axis interval: 7 days if days < 60 otherwise 14 days
        interval = dt.timedelta(days=14 if days >= 60 else 7)
        date_ticks = []
        last_monday = today - dt.timedelta(days=today.weekday())

        date = last_monday
        while date >= oldest_day:
            date_ticks.insert(0, date.strftime("%Y-%m-%d"))
            date -= interval

        plt.figure()
        plt.plot(dates, message_nums)
        plt.title(
            f"Number of messages sent to #{EMOJI_REGEX.sub('', channel.name)} "
            f"in the past {days} days")
        plt.xlabel("Date")
        plt.ylabel("Number of messages")
        plt.xticks(date_ticks, rotation=90)

        filename = f"{ctx.message.id}.png"
        plt.savefig(filename, bbox_inches="tight")

        try:
            with open(filename, "rb") as f:
                file = discord.File(f)
                await ctx.send(file=file)
        finally:
            if os.path.exists(filename):
                os.remove(filename)


def setup(bot):
    """
    Add the cog we have made to our bot.

    This function is necessary for every cog file, multiple classes in the
    same file all need adding and each file must have their own setup function.
    """
    bot.add_cog(StatsCog(bot))
