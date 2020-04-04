#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Utility commands to be used throughout the cogs
"""

import os
import asyncio


ENVIRONMENT = os.getenv("ENVIRONMENT")


async def get_confirmation(ctx, bot, message):
    confirm_message = await ctx.send(message)
    await confirm_message.add_reaction(u"👍")
    await confirm_message.add_reaction(u"👎")

    def check(check_reaction, check_user):
        return (check_user == ctx.author) \
            and check_reaction.message.id == confirm_message.id and \
            ((str(check_reaction.emoji) == u"👍") or (str(check_reaction.emoji) == u"👎"))

    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)
    except asyncio.TimeoutError:
        await confirm_message.delete()
        return False, "Timeout"
    else:
        await confirm_message.delete()
        if str(reaction.emoji) == u"\u1F44D":
            return True, None
        return False, "Rejected"


def log_error(message):
    # At some point, I want to perform different operations here between
    # Production and development.
    raise Exception(message)


def log_info(message):
    # Again, at some point this will be different between production and
    # Development.
    print(message)
