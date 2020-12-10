#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
A christmas cog to be festive and shit

Also provides a simple base for starting a new cog.
"""
from discord.ext import commands


class ChristmasCog(commands.Cog):
    """Festive commands for the server."""

    def __init__(self, bot):
        """Save our bot argument that is passed in to the class."""
        self.bot = bot
        self.christmas_mode = False

    @commands.Cog.listener()
    async def on_message(self, message):
        if self.christmas_mode:
            await message.add_reaction(u"🎄")

    @commands.command(
        name="christmasMode",
        help="Enables christmas mode")
    @commands.has_role("Admin")
    async def toggle_christmas_mode(self, ctx):
        self.christmas_mode = not self.christmas_mode
        await ctx.send("Toggled christmas mode!")


def setup(bot):
    """
    Add the cog we have made to our bot.

    This function is necessary for every cog file, multiple classes in the
    same file all need adding and each file must have their own setup function.
    """
    bot.add_cog(ChristmasCog(bot))
