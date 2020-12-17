#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
An extension for providing message-related statistics
"""

# In this case, discord import is not needed, in some cases it may be.
# import discord
from discord.ext import commands


class StatsCog(commands.Cog, name="Statistics"):

    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    """
    Add the cog we have made to our bot.

    This function is necessary for every cog file, multiple classes in the
    same file all need adding and each file must have their own setup function.
    """
    bot.add_cog(StatsCog(bot))
