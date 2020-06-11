#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Cog for organising polls"""

import asyncio
import datetime
import re
import time

import discord
from discord.ext import commands, tasks

import database as db
import utils as ut
import traceback

DURATION_REGEX = re.compile(
    r"((?P<hours>\d+?)h)?((?P<minutes>\d+?)m)?((?P<seconds>\d+?)s)?")


class PollsCog(commands.Cog, name="Polls"):
    """Class for polls cog"""

    def __init__(self, bot):
        """Save our bot argument that is passed in to the class."""
        self.bot = bot
        self.poll_daemon.start()

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

    async def get_new_choice(self, poll, message, user):
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
        if await db.get_poll_choice(poll['ID'], reaction):
            await message.channel.send(
                f"Choice already exists for {reaction}. "
                "Click ➕ to try again")
            return

        # Fetches embed from poll message
        embed = message.embeds[0]
        embed.add_field(name=f"{reaction} 0", value=text, inline=False)

        # Message must be updated with new embed
        await message.edit(embed=embed)
        await message.add_reaction(reaction)

        # Cleans up the message that had the choice info
        # sent by the user
        await response.delete()

        await db.add_poll_choice(poll['ID'], reaction, text)

    async def delete_poll(self, poll, message, user):
        poll_creator_id = poll['creator']
        current_user_id = int(await db.get_user_id(user.id))

        if poll_creator_id != current_user_id:
            await message.channel.send(
                "You don't have permission to delete this poll!")
            return

        result, reason = await ut.get_confirmation(
            message.channel, user, self.bot,
            "Are you sure you want to delete the poll? "
            "All responses and choices will be deleted")

        if result:
            await message.delete()
            await db.delete_poll(poll['ID'])

        return result

    async def toggle_poll_response(self, poll, user_id,
                                   reaction, message, is_add=True):
        end_date = int(poll['endDate'])
        if time.time() >= end_date or poll['ended']:
            return

        if is_add:
            result, reason = await db.user_add_response(
                user_id, poll['ID'], reaction)
        else:
            result, reason = await db.user_remove_response(
                user_id, poll['ID'], reaction)

        return result

    async def end_poll(self, poll):
        poll_id = int(poll['ID'])
        channel = self.bot.get_channel(int(poll['channelID']))
        message = await channel.fetch_message(int(poll['messageID']))

        await db.end_poll(poll_id)
        await message.remove_reaction('➕', self.bot.user)
        await message.remove_reaction('🛑', self.bot.user)

        embed = message.embeds[0]
        embed.description = ("Poll has now ended\n"
                             "React with ✖️ to delete the poll")

        await message.edit(embed=embed)

        await self.update_response_counts(poll)

    async def user_end_poll(self, poll, message, user):
        poll_creator_id = poll['creator']
        current_user_id = int(await db.get_user_id(user.id))

        if poll_creator_id != current_user_id:
            await message.channel.send(
                "You don't have permission to end this poll!")
            return

        result, reason = await ut.get_confirmation(
            message.channel, user, self.bot,
            "Are you sure you want to end the poll now?")

        # Brings forward the end date for the poll,
        # effectively ending it immediately
        # 
        # The poll task loop will perform the cleanup
        if result:
            await db.change_poll_end_date(poll['ID'], int(time.time()))

    async def update_response_counts(self, poll):
        channel = self.bot.get_channel(int(poll['channelID']))
        message = await channel.fetch_message(int(poll['messageID']))
        count_dict = await db.get_response_count_by_choice(poll['ID'])

        embed = message.embeds[0]
        for index, field in enumerate(embed.fields):
            reaction = field.name.split()[0]
            count = count_dict.get(reaction, 0)
            embed.set_field_at(index, name=f"{reaction} {count}",
                               value=field.value, inline=False)

        await message.edit(embed=embed)

    @tasks.loop(seconds=5.0)
    async def poll_daemon(self):
        """
        Task loop that ends any unended polls
        that are need to be ended
        """
        ongoing_polls = await db.get_all_ongoing_polls()
        for poll in ongoing_polls:
            end_date = poll['endDate']
            if time.time() >= end_date:
                await self.end_poll(poll)

            await self.update_response_counts(poll)

    @poll_daemon.before_loop
    async def before_poll_daemon_start(self):
        await self.bot.wait_until_ready()

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        """
        Listens for reactions that are removed from poll messages
        """
        emoji = payload.emoji
        if emoji.name in ('➕', '✖️', '🛑'):
            return

        message_id = payload.message_id
        poll = await db.get_poll(message_id)
        if not poll:
            return

        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(message_id)
        user = self.bot.get_user(payload.user_id)

        await self.toggle_poll_response(poll, user.id, emoji.name,
                                        message, False)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        """
        Listens for reactions to poll messages
        """
        emoji = payload.emoji
        if payload.member.bot:
            return

        message_id = payload.message_id
        poll = await db.get_poll(message_id)
        if not poll:
            return

        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(message_id)
        user = payload.member
        if emoji.name == '➕':
            await self.get_new_choice(poll, message, user)
        elif emoji.name == '✖️':
            deleted = await self.delete_poll(poll, message, user)
            if not deleted:
                await message.remove_reaction(emoji, user)
        elif emoji.name == '🛑':
            await self.user_end_poll(poll, message, user)
        else:
            await self.toggle_poll_response(poll, user.id, emoji.name,
                                            message, True)

        if emoji.name in ('➕', '🛑'):
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
        await message.add_reaction('🛑')

        await db.user_create_poll(
            ctx.author.id, message.id, message.channel.id,
            ctx.guild.id, title, int(end_date.timestamp()))


def setup(bot):
    """
    Add the cog we have made to our bot.

    This function is necessary for every cog file, multiple classes in the
    same file all need adding and each file must have their own setup function.
    """
    bot.add_cog(PollsCog(bot))
