#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A cog for providing birthday celebration features on the bot
"""

from discord.ext import commands


class BirthdayCog(commands.Cog, name="Birthdays"):
    """
    Help the bot celebrate your birthday
    """

    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    """
    Add the cog we have made to our bot.
    """
    bot.add_cog(BirthdayCog(bot))
