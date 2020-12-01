#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
A cog to check that users do not end up with duplicate nicknames.
"""
# In this case, discord import is not needed, in some cases it may be.
# import discord
from discord.ext import commands


class DuplicateNameCog(commands.Cog):
    def __init__(self, bot):
        """Save our bot argument that is passed in to the class."""
        self.bot = bot
        self.ignore_users = []

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        """
        Checks the users nickname to see if it is already in use.
        :param before: User before update.
        :param after: User after update.
        """
        # Check if name is same before and after
        # Also check they weren't just updated, just so we don't end up
        # with infinite loops.
        if (
            after.nick and before.nick != after.nick
            and before not in self.ignore_users
        ):
            # Loop over each member
            for member in after.guild.members:
                # Check that they are not the same user
                # and that the nick we are setting to is not the same as the
                # members display name.
                if (
                    member != after
                    and member.display_name.lower() == after.nick.lower()
                ):
                    # Add user to ignore list, update and then remove.
                    self.ignore_users.append(after)
                    await after.edit(nick=before.nick)
                    self.ignore_users.remove(after)
                    # Send the user a message that their nick wasn't updated.
                    await after.send("Someone else appears to have that "
                                     "nickname already, we like being able to "
                                     "distinguish people so please try "
                                     "something else, even just a "
                                     "single character")


def setup(bot):
    """
    Add the cog we have made to our bot.
    """
    bot.add_cog(DuplicateNameCog(bot))
