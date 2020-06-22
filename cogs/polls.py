#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Cog for organising polls

Author: William Lee
"""

import asyncio
import datetime
import re
import time
import traceback

import discord
from discord.ext import commands, tasks

import utils as ut
from models import User, Poll, PollChoice

# Regex from extracting time from format 00h00m00s
DURATION_REGEX = re.compile(
    r"((?P<days>\d+?)d)?((?P<hours>\d+?)h)?"
    r"((?P<minutes>\d+?)m)?((?P<seconds>\d+?)s)?")

# Emoji for controlling polls
ADD_CHOICE_EMOJI = '➕'
DELETE_POLL_EMOJI = '✖️'
END_POLL_EMOJI = '🛑'

# Tuple of control emoji for convenience
POLL_CONTROL_EMOJI = (
    ADD_CHOICE_EMOJI,
    DELETE_POLL_EMOJI,
    END_POLL_EMOJI
)

# Color of poll embed
POLL_COLOR = 0x009fe3

# Number of polls per page
POLLS_PER_PAGE = 10

# Emoji for showing polls
FIRST_PAGE_EMOJI = '⏮'
PREVIOUS_PAGE_EMOJI = '⏪'
CLEAR_POLLS_EMOJI = '⏹️'
NEXT_PAGE_EMOJI = '⏩'
LAST_PAGE_EMOJI = '⏭️'

# Tuple of emoji for convenience
SHOW_POLLS_EMOJI = (
    FIRST_PAGE_EMOJI,
    PREVIOUS_PAGE_EMOJI,
    CLEAR_POLLS_EMOJI,
    NEXT_PAGE_EMOJI,
    LAST_PAGE_EMOJI,
)

class PollsCog(commands.Cog, name="Polls"):
    """Class for polls cog"""

    def __init__(self, bot):
        """Save our bot argument that is passed in to the class."""
        self.bot = bot
        self.poll_daemon.start()

    async def parse_time_as_delta(self, time: str):
        """
        Uses a regex to extract a duration in the format 00h00m00s
        to a `datetime.timedelta`
        """

        # Duration string is converted to lowercase
        # so 10h30m5 is equivalent to 10H30M5S
        match = DURATION_REGEX.match(time.lower())
        if match:
            values_dict = match.groupdict()
            for key in values_dict:
                # If no value for a time unit is found
                # then it is assumed to be 0
                if values_dict[key] is None:
                    values_dict[key] = 0
                values_dict[key] = int(values_dict[key])

            return datetime.timedelta(**values_dict)

    async def check_add_new_choice(self, poll, message, response):
        # Checks an edited message against a given message
        def get_message_edit_check(message):
            def check(_, m):
                return m.id == message.id

            return check

        # Splits the message into emoji and text
        values = response.content.split(maxsplit=1)

        error_msg = None

        # Expect split be into 2 parts exactly
        if len(values) != 2:
            error_msg = "New choice wasn't given in the correct format."

        if error_msg is None:
            reaction, text = values
            if reaction in POLL_CONTROL_EMOJI:
                error_msg = f"You can't use {reaction} as a choice."
            elif poll.choices().where('reaction', reaction).first():
                error_msg = f"Choice already exists for {reaction}."
            else:
                try:
                    await message.add_reaction(reaction)
                except discord.errors.HTTPException:
                    error_msg = f"'{reaction}' is an unknown emoji."

        if error_msg is not None:
            error_prompt = await message.channel.send(
                f"{error_msg} You may edit your original message.")

            check = get_message_edit_check(response)

            try:
                _, new_response = await self.bot.wait_for(
                    'message_edit', check=check, timeout=30.0)
            except asyncio.TimeoutError:
                await response.delete()
                await error_prompt.delete()
            else:
                await error_prompt.delete()
                await self.check_add_new_choice(poll, message, new_response)
        else:
            await response.delete()

            new_choice = PollChoice(reaction=reaction, text=text)
            poll.choices().save(new_choice)

            await self.update_response_counts(poll)

    async def get_new_choice_from_user(self, poll, message,
                                       user: discord.User):

        # Checks that the author of the message
        # is the one that wants to add a new choice
        def author_check(m):
            return m.author == user

        prompt_msg = await message.channel.send(
            "Send a message for the choice in the format `<emoji> <text>`, "
            "e.g. :heart: Red Heart")

        try:
            response = await self.bot.wait_for('message', check=author_check,
                                               timeout=30.0)
        except asyncio.TimeoutError:
            pass
        else:
            await self.check_add_new_choice(poll, message, response)
        finally:
            await prompt_msg.delete()

    async def user_delete_poll(self, poll, message, user: discord.User):
        # Only the creator of the poll or admins can delete it
        if poll.creator_id != user.id and not ut.is_admin(user):
            return

        # Awaits confirmation of the deletion
        result, reason = await ut.get_confirmation(
            message.channel, user, self.bot,
            "Are you sure you want to delete the poll? "
            "The poll will be deleted from the conversation.\n"
            "You can use the `summonpoll` command to bring the poll back")

        if result:
            # The message containing the poll is deleted
            await message.delete()

        return result

    async def toggle_poll_response(self, choice, message, user: discord.User):
        user = User.find(user.id)
        response = choice.users().where('user_id', user.id).first()

        if response:
            choice.users().detach(user)
        else:
            choice.users().save(user)

    async def end_poll(self, poll):
        channel = self.bot.get_channel(poll.channel_id)

        poll.ended = True
        poll.save()

        # If the message has been deleted
        try:
            message = await channel.fetch_message(poll.message_id)
        except discord.errors.NotFound:
            return

        # Removes all reactions but the delete poll reaction
        for reaction in message.reactions:
            if str(reaction.emoji) == END_POLL_EMOJI:
                continue
            await message.remove_reaction(reaction.emoji, self.bot.user)

        embed = message.embeds[0]
        embed.description = (
            "Poll has now ended\n"
            f"React with {DELETE_POLL_EMOJI} to delete the poll")

        try:
            await message.edit(embed=embed)
        except discord.errors.NotFound:
            pass

    async def user_end_poll(self, poll, message, user: discord.User):
        # Only the creator of the poll can end the poll
        if poll.creator_id != user.id and not ut.is_admin(user):
            return

        result, reason = await ut.get_confirmation(
            message.channel, user, self.bot,
            "Are you sure you want to end the poll now?")

        # Brings forward the end date for the poll to current time
        #
        # The poll will end the poll on its next iteration
        if result:
            poll.end_date = ut.get_utc_time()
            poll.save()

    async def update_response_counts(self, poll):

        def key(choice):
            try:
                return emojis.index(choice.reaction)
            except ValueError:
                # If emoji isn't found, then return 0
                return 0

        channel = self.bot.get_channel(poll.channel_id)

        # If the message is deleted, then ignore and return
        try:
            message = await channel.fetch_message(poll.message_id)
        except discord.errors.NotFound:
            return

        # Eager-loads choice for poll
        poll.load('choices')
        choices = list(poll.choices().get())

        # Choices are sorted in the order of appearance
        # of the emoji in the message - also the order in which they are added
        emojis = [str(reaction.emoji) for reaction in message.reactions]
        choices.sort(key=key)

        embed = message.embeds[0]
        embed.clear_fields()

        user_limit = 3
        for choice in choices:
            count = choice.users().count()
            first_users = choice.users().limit(user_limit).get()

            users = ', '.join([f"<@{user.id}>" for user in first_users])
            if count > user_limit:
                users += f" and {count - user_limit} more"

            field_value = choice.text + (f" - {users}" if users else "")
            embed.add_field(name=f"{choice.reaction} {count}",
                            value=field_value, inline=False)

        embed.timestamp = ut.get_utc_time()
        embed.set_footer(text=f"Poll ID: {poll.id}")

        # Again, if the message is deleted
        try:
            await message.edit(embed=embed)
        except discord.errors.NotFound:
            return

    async def create_poll_embed(self, title, end_date: datetime.datetime,
                                ended, choices=[]):
        if ended:
            description = (
                "Poll has now ended\n"
                f"React with {DELETE_POLL_EMOJI} to delete the poll")
        else:
            description = ut.get_uk_time(end_date).strftime(
                "Poll ends: %d/%m/%Y %H:%M:%S %Z\n") + (
                f"React with {ADD_CHOICE_EMOJI} to add a choice\n"
                f"React with {DELETE_POLL_EMOJI} to delete the poll\n"
                f"React with {END_POLL_EMOJI} to end the poll, "
                "and finalise the results\n"
                "React with the emoji shown below to vote for that option")

        embed = discord.Embed(title=title, description=description,
                              color=POLL_COLOR)

        return embed

    async def user_show_polls(self, user: discord.User, channel,
                              *, message=None, page=1):

        def check(reaction, check_user):
            return (str(reaction.emoji) in SHOW_POLLS_EMOJI
                    and check_user == user)

        if ut.is_admin(user):
            polls = Poll.paginate(POLLS_PER_PAGE, page)
        else:
            polls = Poll.where('creator_id', user.id) \
                .paginate(POLLS_PER_PAGE, page)

        embed = discord.Embed(title="Your Polls", color=POLL_COLOR)
        for poll in polls:
            field_value = (
                f"Poll ID: {poll.id}. This poll "
                + ("has ended" if poll.ended else "is ongoing"))

            embed.add_field(
                name=f"{poll.title}", value=field_value, inline=False)

        first_poll = polls.per_page * (page - 1) + 1
        last_poll = first_poll + polls.count() - 1
        total = polls.total

        embed.set_footer(text=f"Showing polls {first_poll} - {last_poll} "
                              f"of {total}\n"
                              f"Page {page} of {polls.last_page}")

        if message is None:
            message = await channel.send(embed=embed)
        else:
            await message.edit(embed=embed)

        if page != 1:
            await message.add_reaction(FIRST_PAGE_EMOJI)
            await message.add_reaction(PREVIOUS_PAGE_EMOJI)
        else:
            try:
                await message.remove_reaction(FIRST_PAGE_EMOJI, self.bot.user)
                await message.remove_reaction(
                    PREVIOUS_PAGE_EMOJI, self.bot.user)
            except discord.errors.NotFound:
                pass

        await message.add_reaction(CLEAR_POLLS_EMOJI)

        if page != polls.last_page:
            await message.add_reaction(NEXT_PAGE_EMOJI)
            await message.add_reaction(LAST_PAGE_EMOJI)
        else:
            try:
                await message.remove_reaction(NEXT_PAGE_EMOJI, self.bot.user)
                await message.remove_reaction(LAST_PAGE_EMOJI, self.bot.user)
            except discord.errors.NotFound:
                pass

    @tasks.loop(seconds=1.0)
    async def poll_daemon(self):
        """
        Task loop that update response counts
        and ends polls that need to be ended
        """

        # try-except can be replaced with a coroutine
        # wrapped with discord.ext.tasks.Loop.error on release of 1.4
        try:
            ongoing_polls = Poll.where('ended', False).get()
            for poll in ongoing_polls:
                if ut.get_utc_time() >= poll.end_date:
                    await self.end_poll(poll)
        except Exception:
            traceback.print_exc()

    @poll_daemon.before_loop
    async def before_poll_daemon_start(self):
        # Waits until the bot is ready before starting the task loop
        await self.bot.wait_until_ready()

    @commands.Cog.listener('on_raw_reaction_add')
    async def on_poll_react(self, payload):
        """
        Listens for reactions to poll messages
        """

        # Ignores if any bots reacts
        if payload.member.bot:
            return

        # Ignores react if the message doesn't correspond to a poll
        message_id = payload.message_id
        poll = Poll.where('message_id', message_id).first()
        if not poll:
            return

        channel = self.bot.get_channel(payload.channel_id)
        try:
            message = await channel.fetch_message(message_id)
        except discord.errors.NotFound:
            return

        user = payload.member
        emoji = payload.emoji
        if emoji.name == DELETE_POLL_EMOJI:
            deleted = await self.user_delete_poll(poll, message, user)
            if not deleted:
                await message.remove_reaction(emoji, user)
            return

        # New responses after the poll has ended are not accepted
        end_date = poll.end_date
        if ut.get_utc_time() >= end_date or poll.ended:
            try:
                await message.remove_reaction(emoji, user)
            except discord.errors.NotFound:
                pass
            return

        if emoji.name == ADD_CHOICE_EMOJI:
            await self.get_new_choice_from_user(poll, message, user)
        elif emoji.name == END_POLL_EMOJI:
            await self.user_end_poll(poll, message, user)
        else:
            choice = poll.choices().where('reaction', str(emoji)).first()
            await self.toggle_poll_response(choice, message, user)

        try:
            await message.remove_reaction(emoji, user)
        except discord.errors.NotFound:
            pass

        if emoji.name not in POLL_CONTROL_EMOJI:
            await self.update_response_counts(poll)

    @commands.command(
        name="createpoll",
        help="Creates a poll. You can add choices to it later")
    @commands.has_role("Member")
    async def create_poll(self, ctx, duration, *, title):
        """
        Allows a user to create a poll.
        """

        duration = await self.parse_time_as_delta(duration)

        if not duration:
            await ctx.send("Poll must have a valid duration "
                           "that is greater than zero")
            return

        end_date = ut.get_utc_time() + duration
        embed = await self.create_poll_embed(title, end_date, False)
        message = await ctx.send(embed=embed)

        # Adds control emojis
        for emoji in POLL_CONTROL_EMOJI:
            await message.add_reaction(emoji)

        # Deletes the original command message
        await ctx.message.delete()

        poll = Poll.create(
            title=title, creator_id=ctx.author.id,
            message_id=message.id, channel_id=message.channel.id,
            end_date=end_date)

        await self.update_response_counts(poll)

    @commands.command(
        name="summonpoll",
        help="Moves an existing poll to the bottom of the channel")
    async def summon_poll(self, ctx, poll_id: int):
        """
        Allows a user to bring forward a poll in the conversation,
        for the benefit of longer-duration polls
        """

        poll = Poll.find(poll_id)
        if not poll:
            await ctx.send(f"Poll with ID {poll_id} could not found.")
            return

        if ctx.author.id != poll.creator_id and not ut.is_admin(ctx.author):
            await ctx.send("You don't have permission to summon that poll!")

        old_channel = self.bot.get_channel(poll.channel_id)

        try:
            old_message = await old_channel.fetch_message(poll.message_id)
            await old_message.delete()
        except discord.errors.NotFound:
            pass

        embed = await self.create_poll_embed(
            poll.title, poll.end_date, poll.ended)
        new_message = await ctx.send(embed=embed)

        if not poll.ended:
            await new_message.add_reaction(ADD_CHOICE_EMOJI)

        await new_message.add_reaction(DELETE_POLL_EMOJI)

        if not poll.ended:
            await new_message.add_reaction(END_POLL_EMOJI)
            for choice in poll.choices:
                await new_message.add_reaction(choice.reaction)

        await ctx.message.delete()

        poll.message_id = new_message.id
        poll.channel_id = ctx.channel.id
        poll.save()

        await self.update_response_counts(poll)

    @commands.command(
        name="showpolls",
        help="Shows polls that you have control over")
    async def show_polls(self, ctx):
        await ctx.message.delete()
        await self.user_show_polls(ctx.author, ctx.channel)


def setup(bot):
    """
    Add the cog we have made to our bot.

    This function is necessary for every cog file, multiple classes in the
    same file all need adding and each file must have their own setup function.
    """
    bot.add_cog(PollsCog(bot))
