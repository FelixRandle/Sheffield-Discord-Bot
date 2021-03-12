#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A cog for providing birthday celebration features on the bot
"""

import datetime as dt

from discord.ext import commands

from models import User


class BirthdayCog(commands.Cog, name="Birthdays"):
    """
    Help the bot celebrate your birthday
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        help="Add your birthday to the bot\n\n"
             "Enter your birthday as yyyy-mm-dd to have the bot "
             "record your entire date of birth, "
             "or just mm-dd to have it record your birthday"
    )
    async def birthday(self, ctx, date_of_birth):
        try:
            date = dt.date.strptime(
                date_of_birth,
                "%Y-%m-%d" if len(date_of_birth) > 5 else "%m-%d")
        except ValueError:
            return await ctx.send("Birthday given is an invalid date")

        user = User.find(ctx.author.id)
        user.date_of_birth = date
        user.save()
        await ctx.send("Added your birthday!")


def setup(bot):
    """
    Add the cog we have made to our bot.
    """
    bot.add_cog(BirthdayCog(bot))
