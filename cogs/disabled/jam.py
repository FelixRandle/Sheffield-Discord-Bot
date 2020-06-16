#!/usr/bin/env python
# -*- coding: utf-8 -*- 
"""
An example cog to show how things should be done.

Also provides a simple base for starting a new cog.
"""
# In this case, discord import is not needed, in some cases it may be.
# import discord
import asyncio

from discord.ext import commands

import database as db
import utils as ut

# TODO: Change ut.get_confirmation calls to match changes to the coroutine

class JamCog(commands.Cog):
    """Create a class that extends Cog to make our functionality in."""

    def __init__(self, bot):
        """Save our bot argument that is passed in to the class."""
        self.bot = bot

    @commands.command(
        name="jamming",
        help="Let's people know whether you're jamming or not.")
    @commands.has_role("Member")
    async def jamming(self, ctx):
        """
        Create a simple jamming command.

        This command adds some help text and also required that the user
        have the Member role, this is case-sensitive.
        """
        result = await db.set_jamming(ctx.author.id, True)
        if result:
            await ctx.send("You're jamming! :jam_jar:")

    @commands.command(
        name="stopjamming",
        help="Let's people know whether you're jamming or not.")
    @commands.has_role("Member")
    async def stop_jamming(self, ctx):
        """
        Create a simple ping pong command.

        This command adds some help text and also required that the user
        have the Member role, this is case-sensitive.
        """
        result, reason = await ut.get_confirmation(ctx, self.bot, "Please react with a thumbs up to stop jamming. "
                                                                  "This will also remove you from any team.")

        print(result, reason)
        if result:
            ctx.send("You have been removed as a jammer :frowning:")
            await db.set_jamming(ctx.author.id, False)
        else:
            ctx.send("Jam on! :jam_jar:")

    @commands.command(
        name="createteam",
        help="Let's people know whether you're jamming or not.")
    @commands.has_role("Member")
    async def create_team(self, ctx, name: str, git: str):
        """
        Allows a user to create a Jam Team

        This command creates a Jam Team with the creator as the only team member.
        """
        user_team = await db.get_user_jam_team(ctx.author.id)
        if len(name) == 0 or len(git) == 0:
            ctx.send("Please pass in both a team name and a git link.")
        result, reason = await ut.get_confirmation(ctx, self.bot, "Please react with a thumbs up to stop jamming. "
                                                                  "This will also remove you from any team.")

        if result:
            ctx.send("You have been removed as a jammer :frowning:")
            await db.set_jamming(ctx.author.id, False)
        else:
            ctx.send("Jam on! :jam_jar:")


def setup(bot):
    """
    Add the cog we have made to our bot.

    This function is necessary for every cog file, multiple classes in the
    same file all need adding and each file must have their own setup function.
    """
    bot.add_cog(JamCog(bot))
