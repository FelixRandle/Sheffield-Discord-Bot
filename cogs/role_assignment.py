#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Cog for assigning roles to users
"""

from discord.ext import commands

from models import Guild

ROLE_ASSIGNMENT_MESSAGE = (
    "Hi everyone!\n"
    "To make it easier for everyone to see who's in which year, "
    "and make sure you get stuff targeted for your year group,\n"
    "please react below with your year to assign yourself your year's role.\n"
    "If you misclick, just react again with the correct year to be reassigned"
)

EMOJI_TO_ROLES = {
    "1️⃣": "First Year",
    "2️⃣": "Second Year",
    "3️⃣": "Third Year",
    "4️⃣": "Fourth Year",
}


class RoleAssignmentCog(commands.Cog, name="Role Assignment"):

    def __init__(self, bot):
        """
        Instantiates an instance of the cog.
        Takes the bot object as its single argument.
        """
        self.bot = bot

    @commands.command(name="sendRoleAssignmentMsg")
    @commands.has_permissions(manage_messages=True)
    async def send_role_assignment_message(self, ctx):
        """
        Sends the role assignment message
        """
        guild = Guild.find(ctx.guild.id)
        message = await ctx.send(ROLE_ASSIGNMENT_MESSAGE)

        for emoji in EMOJI_TO_ROLES:
            await message.add_reaction(emoji)

        guild.role_assignment_msg_id = message.id
        guild.save()


def setup(bot):
    """
    Add the cog to the bot
    """
    bot.add_cog(RoleAssignmentCog(bot))
