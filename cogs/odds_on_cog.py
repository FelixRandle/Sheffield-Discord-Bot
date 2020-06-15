#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
An example cog to show how things should be done.

Also provides a simple base for starting a new cog.
"""
# In this case, discord import is not needed, in some cases it may be.
import asyncio

import discord
from discord.ext import commands

import utils as ut


class OddsOnCog(commands.Cog):
    """Create a class that extends Cog to make our functionality in."""

    def __init__(self, bot):
        """Save our bot argument that is passed in to the class."""
        self.bot = bot

    @commands.command(
        name="oddsOn",
        help="Let's you play Odds On against other members")
    @commands.has_role("Member")
    async def odds_on(self, ctx, role, *, wager: str):
        """
        Challenge a user to odds on

        Challenge a specific user to a wager,
        that user then specifies the odds and
        both users then pick a number between 1
        and the chosen upper limit.
        """
        target_user_id = await ut.find_id(role)
        if target_user_id == ctx.author.id:
            raise commands.errors.UserInputError(
                message="You can't play with yourself here...")
        target_user = self.bot.get_user(target_user_id)
        if target_user is None:
            raise commands.errors.UserInputError(
                message="I couldn't find the user you tagged.")

        confirm_message = await ctx.send(
            f"<@{target_user_id}>, <@{ctx.author.id}> "
            f"has challenged you in odds on.\n"
            f"Reply to this message with a number (e.g. 7) "
            f"to set the odds or ignore it. (Number must"
            f"be greater than 1)")

        def check(check_message):
            try:
                return (int(check_message.content) > 1
                        and check_message.author == target_user)
            except ValueError:
                return False

        try:
            message = await self.bot.wait_for('message', timeout=100.0,
                                              check=check)
        except asyncio.TimeoutError:
            await confirm_message.delete()
            await ctx.send(
                f"<@{ctx.author.id}> "
                f"The person you challenged did not respond in time.")
            return
        upper_value = int(message.content)
        author_value, target_value = await asyncio.gather(
            self.get_number_in_dm(ctx.author, upper_value),
            self.get_number_in_dm(target_user, upper_value)
        )

        if author_value[0] is False:
            await ctx.send(
                f"I couldn't complete the game because <@{ctx.author.id}> "
                f"had the following error:\n"
                f"{author_value[1]}")
        elif target_value[0] is False:
            await ctx.send(
                f"I couldn't complete the game because <@{target_user_id}> "
                f"had the following error:\n"
                f"{target_value[1]}")
        else:
            winning_statement = (f"<@{target_user_id}> must {wager}" if author_value[1] == target_value[1]
                                 else f"<@{target_user_id}> doesn't have to do anything.")
            await ctx.send(f"<@{ctx.author.id}> chose {author_value[1]}, "
                           f"<@{target_user_id}> chose {target_value[1]}"
                           f"<@{winning_statement}>")

    async def get_number_in_dm(self, user, max_value):
        dm_channel = user.dm_channel
        if dm_channel is None:
            dm_channel = await user.create_dm()

        try:
            await dm_channel.send(
                f"Give me a number between 1 and {max_value}")
        except discord.errors.Forbidden:
            return False, "Cannot DM this user"

        def check(check_message):
            try:
                return 1 <= int(check_message.content) <= max_value \
                       and check_message.author == user
            except ValueError:
                return False

        try:
            message = await self.bot.wait_for('message', timeout=30.0,
                                              check=check)
        except asyncio.TimeoutError:
            return False, "Did not respond in time."
        return True, int(message.content)


def setup(bot):
    """
    Add the cog we have made to our bot.

    This function is necessary for every cog file, multiple classes in the
    same file all need adding and each file must have their own setup function.
    """
    bot.add_cog(OddsOnCog(bot))
