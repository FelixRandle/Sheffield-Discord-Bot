#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Cog for assigning roles to users
"""

from discord.ext import commands

from models import Guild

ROLE_ASSIGNMENT_MESSAGE = (
    "Hi everyone!\n\n"
    "To make it easier for everyone to see who's in which year, "
    "and make sure you get stuff targeted for your year group,\n"
    "please react below with your year to assign yourself your year's role.\n"
    "**If you've already done this, then you do not need to do this again**.\n"
    "If you misclick, just react again "
    "with the correct year to be reassigned\n\n"
    "Thanks,\n"
    "The Admin Team"
)

EMOJI_TO_ROLES = {
    "1️⃣": "First Year",
    "2️⃣": "Second Year",
    "3️⃣": "Third Year",
    "4️⃣": "Fourth Year",
    "🇵": "Postgraduate",
    "🎮": "Gamers",
}

# Mutually exclusive roles
MUTEX_ROLES = [
    "First Year",
    "Second Year",
    "Third Year",
    "Fourth Year",
    "Postgraduate",
]


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

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        # Member is bot, or the emoji is not relevant
        if payload.member.bot or str(payload.emoji) not in EMOJI_TO_ROLES:
            return
        # Get the corresponding role name for the emoji
        role_name = EMOJI_TO_ROLES[str(payload.emoji)]
        # Get member's existing roles
        member_role_names = [str(role) for role in payload.member.roles]
        if role_name in member_role_names:
            return  # Return if the member is already assigned the correct role
        # Fetch the available roles from the server
        roles = await payload.member.guild.fetch_roles()
        # Year roles
        year_roles = [
            role for role in roles
            if str(role) in EMOJI_TO_ROLES.values()
        ]
        # Year role to be assigned
        for role in roles:
            if str(role) == role_name:
                assigned_year_role = role
                break
        else:  # End of for loop means role was not found
            await payload.channel.send(
                f"Role {role_name!r} does not exist. "
                "Please report this issue to an admin.")
        # Removes existing year roles
        await payload.member.remove_roles(*year_roles)
        # Adds the required year role
        await payload.member.add_roles(assigned_year_role)


def setup(bot):
    """
    Add the cog to the bot
    """
    bot.add_cog(RoleAssignmentCog(bot))
