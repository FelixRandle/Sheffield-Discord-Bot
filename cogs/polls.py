#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Cog for organising polls"""

import asyncio
import datetime
import re

import discord
from discord.ext import commands

import database as db
import utils as ut

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

    async def create_poll_embed(self, title: str, end_date: datetime.datetime):
        description = end_date.strftime(
            "Poll ends: %d/%m/%Y %H:%M:%S\n"
            "React with ➕ to add a choice\n"
            "React with ✖️ to delete the poll\n"
            "React with 🛑 to end the poll and show the results")
        return discord.Embed(title=title, description=description,
                             color=0x0000ff)

    async def get_new_choice(self, poll_id, message, user):
        prompt_msg = await message.channel.send(
            "Send a message for the choice in the format `<emoji> <text>`, "
            "e.g. :heart: Heart")

        # Checks that the author of the message
        # is the one that wants to add a new choice
        def check(m):
            return m.author == user

        try:
            response = await self.bot.wait_for('message', check=check, 
                                               timeout=30.0)
        except asyncio.TimeoutError:
            await message.channel.send("You didn't respond in time. "
                                       "Click ➕ again to add a new choice")
            return
        finally:
            await prompt_msg.delete()

        # Splits the message into emoji and text
        values = response.content.split(maxsplit=1)

        # Expect split be into 2 parts exactly
        if len(values) != 2:
            await message.channel.send(
                "New choice wasn't given the correct format. Try again.")
            return

        reaction, text = values
        if await db.get_poll_choice(poll_id, reaction):
            await message.channel.send(
                f"Choice already exists for {reaction}. "
                "Click ➕ to try again")
            return

        # Fetches embed from poll message
        embed = message.embeds[0]
        embed.add_field(name=reaction, value=text, inline=False)

        # Message must be updated with new embed
        await message.edit(embed=embed)
        await message.add_reaction(reaction)

        # Cleans up the message that had the choice info 
        # sent by the user
        await response.delete()

        await db.add_poll_choice(poll_id, reaction, text)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        """
        Listens for reactions to poll messages
        """
        emoji = payload.emoji
        if payload.member.bot or (emoji.name in ('➕', '✖️') 
                                  and payload.event_type == 'REACTION_REMOVE'):
            return

        message_id = payload.message_id
        poll = await db.get_poll(message_id, field="ID")
        if not poll:
            return

        poll_id = poll['ID']
        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(message_id)
        user = self.bot.get_user(payload.user_id)
        if emoji.name == '➕':
            await self.get_new_choice(poll_id, message, user)

        if emoji.name in ('➕', '✖️'):
            await message.remove_reaction(emoji, user)

    @commands.command(
        name="createpoll",
        help="Creates a poll. You can add choices to it later")
    @commands.has_role("Member")
    async def create_poll(self, ctx, title, duration=None):
        """
        Allows a user to create a poll.
        """

        if duration is None:
            duration = datetime.timedelta(hours=1)
        else:
            duration = await self.parse_time_as_delta(duration)

        if not duration:
            await ctx.send("Poll must have a valid duration "
                           "that is greater than zero")
            return

        end_date = datetime.datetime.now() + duration
        embed = await self.create_poll_embed(title, end_date)
        message = await ctx.send(embed=embed)

        await message.add_reaction('➕')
        await message.add_reaction('✖️')

        await db.user_create_poll(ctx.author.id, message.id, ctx.guild.id,
                                  title, int(end_date.timestamp()))


def setup(bot):
    """
    Add the cog we have made to our bot.

    This function is necessary for every cog file, multiple classes in the
    same file all need adding and each file must have their own setup function.
    """
    bot.add_cog(PollsCog(bot))
