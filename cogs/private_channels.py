#!/usr/bin/env python
# -*- coding: utf-8 -*- 
"""
An example cog to show how things should be done.

Also provides a simple base for starting a new cog.
"""
# In this case, discord import is not needed, in some cases it may be.
import discord
from discord.ext import commands

import database as db
import utils as ut


class PrivateChannels(commands.Cog):
    """Create a class that extends Cog to make our functionality in."""

    def __init__(self, bot):
        """Save our bot argument that is passed in to the class."""
        self.bot = bot

    @commands.command(
        name="newChannel",
        help="Creates a new private voice channel for you to use.")
    @commands.has_role("Member")
    async def new_channel(self, ctx, limit: int = 0, voice: bool = 1):
        """
        Creates a new voice channel.

        This command creates a new voice channel for the user to use with friends.
        They can specify how many people should be limited to the channel.
        """
        category = discord.utils.get(ctx.guild.categories, name='Private Channels')
        if category is None:
            await ctx.send("I couldn't find the required category, please contact an admin.")
            return

        if await db.user_has_channel(ctx.author.id):
            await ctx.send("You already have a channel! If you believe this is an error then "
                           "please contact an admin.")
        else:
            channel = await ctx.guild.create_voice_channel(ctx.author.name+"'s Channel",
                                                           category=category,
                                                           user_limit=limit)

            await db.user_create_channel(ctx.author.id, channel.id, True)
            await ctx.send("Successfully made you a new channel!")

    @commands.command(
        name="deleteChannel",
        help="Deletes your channel if you have one.")
    @commands.has_role("Member")
    async def delete_channel(self, ctx):
        channel_id = await db.user_has_channel(ctx.author.id)
        if not channel_id:
            await ctx.send("You do not have a channel to delete!")
        else:
            await db.user_delete_channel(ctx.author.id)
            voice_channel = ctx.guild.get_channel(int(channel_id))
            await voice_channel.delete()
            await ctx.send("Successfully deleted your channel")


def setup(bot):
    """
    Add the cog we have made to our bot.

    This function is necessary for every cog file, multiple classes in the
    same file all need adding and each file must have their own setup function.
    """
    bot.add_cog(PrivateChannels(bot))
