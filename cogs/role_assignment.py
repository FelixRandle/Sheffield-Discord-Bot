#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Cog for assigning roles to users
"""

from discord.ext import commands

import utils as ut
from models import Guild

EMOJI_TO_ROLES = {
    "1️⃣": "First Year",
    "2️⃣": "Second Year",
    "3️⃣": "Third Year",
    "4️⃣": "Fourth Year",
    "🇵": "Postgraduate",
    "🎮": "Gamers",
}

ROLE_ASSIGNMENT_MESSAGE = (
    "Hi everyone!\n\n"
    "Please assign yourself with the correct role for your year, "
    "and if you're interested in playing games on a regular basis, "
    "then please assign your the Gamers roles to be pinged for games.\n\n"
    "Thanks,\n"
    "The Admin Team\n\n"
) + "\n".join(f"{emoji} {role}" for emoji, role in EMOJI_TO_ROLES.items())

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

    @commands.Cog.listener('on_raw_reaction_add')
    async def on_raw_reaction_add(self, payload):
        # Member is bot, or the emoji is not relevant,
        # or the message reacted to is not the role assignment message
        guild = Guild.find(payload.guild_id)
        if (payload.member.bot or str(payload.emoji) not in EMOJI_TO_ROLES
                or payload.message_id != guild.role_assignment_msg_id):
            return
        async with ut.RemoveReaction(self, payload):
            # Get the corresponding role name for the emoji
            role_name = EMOJI_TO_ROLES[str(payload.emoji)]
            # Get member's existing roles
            member_role_names = [str(role) for role in payload.member.roles]
            if role_name in member_role_names:
                return  # Return if the member is already assigned the role
            # Fetch the available roles from the server
            roles = await payload.member.guild.fetch_roles()
            # Get roles that are mutually exclusive
            mutex_roles = [role for role in roles if str(role) in MUTEX_ROLES]
            # Role to be assigned
            for role in roles:
                if str(role) == role_name:
                    role_to_be_assigned = role
                    break
            else:  # End of for loop means role was not found
                channel = await self.bot.fetch_channel(payload.channel_id)
                return await channel.send(
                    f"Role {role_name!r} does not exist. "
                    "Please report this issue to an admin.")
            # Removes existing mutually exclusive roles
            if role_to_be_assigned in mutex_roles:
                await payload.member.remove_roles(*mutex_roles)
            # Adds the required role
            await payload.member.add_roles(role_to_be_assigned)


def setup(bot):
    """
    Add the cog to the bot
    """
    bot.add_cog(RoleAssignmentCog(bot))
