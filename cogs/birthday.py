#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A cog for providing birthday celebration features on the bot
"""

import datetime as dt

from discord.ext import commands, tasks

from models import User

# A leap year to store in place of an actual birth year
LEAP_YEAR = 1600


class BirthdayCog(commands.Cog, name="Birthdays"):
    """
    Help the bot celebrate your birthday
    """

    def __init__(self, bot):
        self.bot = bot
        self._birthday_user_ids = []

        self.birthday_task.start()

    @tasks.loop(hours=24)
    async def birthday_task(self):
        today = dt.date.today()
        query = User.where_raw(
            "MONTH(date_of_birth) = %s AND DAY(date_of_birth) = %s",
            (today.month, today.day)
        )
        birthday_users = query.get()

        # Stores IDs of users with birthdays for quick reference
        self._birthday_user_ids = [user.id for user in birthday_users]

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id in self._birthday_user_ids:
            await message.add_reaction("🎂")

    @commands.command(
        help="Add your birthday to the bot\n\n"
             "Enter your birthday as yyyy-mm-dd to have the bot "
             "record your entire date of birth, "
             "or just mm-dd to have it record your birthday"
    )
    async def birthday(self, ctx, date_of_birth):
        try:
            date = dt.datetime.strptime(
                (
                    date_of_birth
                    if len(date_of_birth) > 5
                    else f"{LEAP_YEAR}-{date_of_birth}"
                ),
                "%Y-%m-%d"
            )
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
