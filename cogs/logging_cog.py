#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
An example cog to show how things should be done.

Also provides a simple base for starting a new cog.
"""
# In this case, discord import is not needed, in some cases it may be.
# import discord
from discord.ext import commands
from enum import Enum
import time

import database as db


class LoggingCog(commands.Cog):
    """Create a class that extends Cog to make our functionality in."""

    def __init__(self, bot):
        """Save our bot argument that is passed in to the class."""
        self.bot = bot

    @commands.Cog.listener('on_message')
    async def log_message_add(self, message):
        if message.author.bot:
            return
        await db.log_message(message.author.id, message.id,
                             message.content.encode('unicode-escape'), int(time.time()))


def setup(bot):
    """
    Add the cog we have made to our bot.

    This function is necessary for every cog file, multiple classes in the
    same file all need adding and each file must have their own setup function.
    """
    bot.add_cog(LoggingCog(bot))
