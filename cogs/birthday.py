#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A cog for providing birthday celebration features on the bot
"""

import asyncio
import datetime as dt
from calendar import isleap

from discord.ext import commands, tasks

import utils as ut
from models import User

# A leap year to store in place of an actual birth year
LEAP_YEAR = 1600
# Day that 02-29 birthdays are celebrated on non-leap years
# Format is (month, day)
FEB_29_DAY = (2, 28)


class BirthdayCog(commands.Cog, name="Birthdays"):
    """
    Help the bot celebrate your birthday
    """

    def __init__(self, bot):
        self.bot = bot
        self._birthday_user_ids = []

        self.birthday_task.start()

    async def _say_happy_birthday(self, user):
        if isinstance(user, int):
            user = self.bot.get_user(user)
        await user.send("Happy birthday!")

    @tasks.loop(hours=24)
    async def birthday_task(self):
        today = dt.date.today()
        raw_where_clause = \
            "(MONTH(date_of_birth) = %s AND DAY(date_of_birth) = %s)"
        if (today.month, today.day) == FEB_29_DAY and not isleap(today.year):
            raw_where_clause += \
                " OR (MONTH(date_of_birth) = 2 AND DAY(date_of_birth) = 29)"
        query = User.where_raw(raw_where_clause, [today.month, today.day])
        birthday_users = query.get()

        # Stores IDs of users with birthdays for quick reference
        self._birthday_user_ids = [user.id for user in birthday_users]
        for user_id in self._birthday_user_ids:
            await self._say_happy_birthday(user_id)

    @birthday_task.before_loop
    async def before_birthday_task_loop(self):
        # One-time call to birthday_task coroutine
        await self.birthday_task.coro(self)
        # Waits until midnight to start the task loop
        now = dt.datetime.now()
        tomorrow = (now + dt.timedelta(days=1))
        midnight_tomorrow = tomorrow.replace(
            hour=0, minute=0, second=0, microsecond=0)
        sleep_time = (midnight_tomorrow - now).total_seconds()
        await asyncio.sleep(sleep_time)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if message.author.id in self._birthday_user_ids:
            await message.add_reaction("🎂")

    @commands.command(
        help="Add your birthday to the bot\n\n"
             "Enter your birthday as yyyy-mm-dd to have the bot "
             "record your entire date of birth, "
             "or just mm-dd to have it record your birthday",
        aliases=("bday", "dateOfBirth", "dayOfMyBirth", "spawnDate")
    )
    async def birthday(self, ctx, date_of_birth):
        user = User.find(ctx.author.id)
        if user.date_of_birth is not None:
            return await ctx.send(
                "Your birthday has already been set. "
                "Contact an admin if you've made a mistake."
            )
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

        result, _ = await ut.get_confirmation(
            ctx.channel,
            ctx.author,
            self.bot,
            (
                f"Set your birthday as **{date_of_birth}**? "
                "You can't change once you've set it!"
            )
        )
        if not result:
            return

        today = dt.date.today()
        if (
            (date.month, date.day) == (today.month, today.day)
            or (
                not isleap(today.year)
                and (date.month, date.day) == (2, 29)
                and (today.month, today.day) == FEB_29_DAY
            )
        ):
            self._birthday_user_ids.append(ctx.author.id)
            await self._say_happy_birthday(ctx.author)

        user.date_of_birth = date
        user.save()
        await ctx.send("Added your birthday!")


def setup(bot):
    """
    Add the cog we have made to our bot.
    """
    bot.add_cog(BirthdayCog(bot))
