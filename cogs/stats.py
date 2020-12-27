#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
An extension for providing message-related statistics
"""

import datetime as dt
import random

import matplotlib.pyplot as plt
import utils as ut
from discord.ext import commands
from matplotlib.patches import Rectangle


class StatsCog(commands.Cog, name="Statistics"):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="channelActivity",
        help=(
            "Creates a graph of message frequency within a given timeframe. "
            "Defaults to messages in the last 30 days in the current channel"
        )
    )
    async def channel_activity(self, ctx, days: int = 30, channel=None):
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
        async with ctx.typing():
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
            f"Number of messages sent to #{ut.demojify(channel.name)} "
            f"in the past {days} days")
        plt.xlabel("Date")
        plt.ylabel("Number of messages")
        plt.xticks(date_ticks, rotation=90)

        filename = f"{ctx.message.id}.png"
        plt.savefig(filename, bbox_inches="tight")

        await ut.send_and_delete_file(ctx, filename)

    @commands.command(
        name="channelHistory",
        help=("Shows a visualisation of a channel's history "
              "by which member sent those messages"))
    async def channel_history(self, ctx, limit: int = 500, channel=None):
        if not ctx.message.channel_mentions:
            channel = ctx.channel
        else:
            channel = ctx.message.channel_mentions[0]

        # Maps members to a tuple of RGB floats
        history = []
        member_to_color = {}

        async with ctx.typing():
            async for msg in channel.history(limit=limit):
                if msg.author not in member_to_color:
                    new_color = [random.random() for _ in range(3)]
                    member_to_color[msg.author] = new_color
                else:
                    color = member_to_color[msg.author]
                history.append(msg.author)

        plt.figure(ctx.message.id)

        ax = plt.gca()
        x = 0
        member_to_artist = {}

        for member in history:
            color = member_to_color[member]
            line = plt.axvline(x, color=color)
            if member not in member_to_artist:
                member_to_artist[member] = line
            x += 1
        ax.axes.xaxis.set_visible(False)
        ax.axes.yaxis.set_visible(False)

        plt.title(
            "Visualisation of members' message activity "
            f"in #{ut.demojify(channel.name)}, using last {limit} messages")
        plt.legend(
            *zip(*[(v, k) for k, v in member_to_artist.items()]),
            bbox_to_anchor=(0, 0, 1, 0), loc="upper left",
            mode="expand", ncol=2)

        filename = f"{ctx.message.id}.png"
        plt.savefig(filename, bbox_inches="tight")

        await ut.send_and_delete_file(ctx, filename)

    @commands.command(
        name="channelSummary",
        help=("Shows a visualisation of members and the number of messages "
              "they've sent in a channel."))
    async def channel_summary(self, ctx, limit: int = 500, channel=None):
        if not ctx.message.channel_mentions:
            channel = ctx.channel
        else:
            channel = ctx.message.channel_mentions[0]

        # Maps members to a tuple of RGB floats
        member_to_message_count = {}
        member_to_color = {}

        async with ctx.typing():
            async for msg in channel.history(limit=limit):
                if msg.author not in member_to_color:
                    new_color = [random.random() for _ in range(3)]
                    member_to_color[msg.author] = new_color
                else:
                    color = member_to_color[msg.author]

                member_to_message_count.setdefault(msg.author, 0)
                member_to_message_count[msg.author] += 1

        plt.figure(ctx.message.id)

        ax = plt.gca()
        x = 0
        artist_members = []

        member_to_message_count = {
            k: v
            for (k, v)
            in sorted(
                member_to_message_count.items(),
                key=lambda x: x[1],
                reverse=True
            )
        }

        for member, count in member_to_message_count.items():
            color = member_to_color[member]
            rect = Rectangle((x, 0), count, 1, facecolor=color, fill=True)
            ax.add_patch(rect)
            x += count
            artist_members.append((rect, member))
        plt.xlim(0, x)
        ax.axes.xaxis.set_visible(False)
        ax.axes.yaxis.set_visible(False)

        plt.title(
            "Visualisation of members' number of messages "
            f"in #{ut.demojify(channel.name)}, using last {limit} messages")
        plt.legend(*(zip(*artist_members)), bbox_to_anchor=(0, 0, 1, 0),
                   loc="upper left", mode="expand", ncol=2)

        filename = f"{ctx.message.id}.png"
        plt.savefig(filename, bbox_inches="tight")

        await ut.send_and_delete_file(ctx, filename)


def setup(bot):
    """
    Add the cog we have made to our bot.

    This function is necessary for every cog file, multiple classes in the
    same file all need adding and each file must have their own setup function.
    """
    bot.add_cog(StatsCog(bot))
