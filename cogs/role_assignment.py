#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Cog for assigning roles to users
"""
import random

from discord import Colour, Embed
from discord.ext import commands
import Levenshtein as lev

import utils as ut
from models import Guild, Role

EMOJI_TO_ROLES = {
    "1️⃣": "First Year",
    "2️⃣": "Second Year",
    "3️⃣": "Third Year",
    "4️⃣": "Fourth Year",
    "🇵": "Postgraduate"
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

ROLE_COLOURS = [
    0x1abc9c,
    0x11806a,
    0x2ecc71,
    0x1f8b4c,
    0x3498db,
    0x206694,
    0x9b59b6,
    0x71368a,
    0xe91e63,
    0xad1457,
    0xf1c40f,
    0xc27c0e,
    0xe67e22,
    0xa84300,
    0xe74c3c,
    0x992d22,
    0x7289da,
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

    @commands.command(
        name="lockRole",
        help="Locks off a role, disallowing users to join it.")
    @commands.has_role("Admin")
    async def lock_role(self, ctx, role_name):
        """
        Locks off the given role.
        """

        found_role = Role.where('name', role_name) \
            .where('guild_id', ctx.guild.id).first()
        if found_role:
            if found_role.is_locked:
                await ctx.send("That role is already locked.")
                return
            found_role.is_locked = True
            found_role.save()
            await ctx.send(f"Locked role `{role_name}` :lock:")
            return

        await ctx.send(f"Could not find role with name`{role_name}`")

    @commands.command(
        name="unlockRole",
        help="Unlocks a role, allowing users to join it.")
    @commands.has_role("Admin")
    async def unlock_role(self, ctx, role_name):
        """
        Unlocks the given role.
        """

        found_role = Role.where('name', role_name) \
            .where('guild_id', ctx.guild.id).first()
        if found_role:
            if not found_role.is_locked:
                await ctx.send("That role is already unlocked.")
                return
            found_role.is_locked = False
            found_role.save()
            await ctx.send(f"Unlocked role `{role_name}` :unlock:")
            return

        await ctx.send(f"Could not find role with name`{role_name}`")

    @commands.command(
        name="deleteRole",
        help="Deletes a role, removing it from all users and "
             "from the database.")
    @commands.has_role("Admin")
    async def delete_role(self, ctx, role_name):
        """
        Deletes the given role.
        """

        found_role = Role.where('name', role_name) \
            .where('guild_id', ctx.guild.id).first()
        if found_role:
            discord_guild = self.bot.get_guild(found_role.guild_id)
            discord_role = discord_guild.get_role(found_role.role_id)

            result, reason = await ut.get_confirmation(
                ctx.channel, ctx.author, self.bot,
                f"Are you sure you wish to delete the role `{role_name}`")

            if result:
                try:
                    await discord_role.delete()
                except AttributeError:
                    ut.log_info(f"Role `{role_name}` was deleted incorrectly")
                finally:
                    found_role.delete()
                await ctx.send(f"Successfully deleted the role `{role_name}`")

            return

        await ctx.send(f"Could not find role with name`{role_name}`")

    @commands.command(
        name="mergeRoles",
        help="Merges two roles, intended for two similarly named roles that "
             "mean the same thing, moves all users from source to target "
             "and deletes source")
    @commands.has_role("Admin")
    async def merge_roles(self, ctx, source_role, target_role):
        """
        Merges the given roles by performing the following actions
        Moves all users from source_role into target_role
        Deletes role from server
        Deletes role from DB
        """

        # TODO: Future implementation, not a required feature for functionality
        pass

    @commands.command(
        name="getRole",
        help="Gives the issuing user a role",
        aliases=["iam", "iama", "gimme"])
    @commands.has_role("Member")
    async def get_role(self, ctx, role_name):
        """
        Gives the user the requested role if not locked..
        """

        found_role = Role.where('name', role_name)\
            .where('guild_id', ctx.guild.id).first()
        if found_role:
            if found_role.is_locked:
                await ctx.send("That role is currently locked and cannot be "
                               "assigned, if you believe this is an error "
                               "please contact an Admin")
                return
            discord_guild = self.bot.get_guild(found_role.guild_id)
            discord_role = discord_guild.get_role(found_role.role_id)
            if discord_role is None:
                await ctx.send("That role appears to be broken, "
                               "please contact an admin")
                return
            await ctx.author.add_roles(discord_role)
            await ctx.send(f"You have been given the role `{role_name}`")
            return

        for role in ctx.guild.roles:
            if lev.distance(role_name.lower(), role.name.lower()) <= 1:
                await ctx.send("That role does not exist but cannot be "
                               "created as it's name is too similar to "
                               f"`{role.name}`")
                return

        result, reason = await ut.get_confirmation(
            ctx.channel, ctx.author, self.bot,
            "It looks like that role doesn't exist, "
            "would you like to create it?")

        if result:
            role = Role()

            role.name = role_name

            role.guild_id = ctx.guild.id
            role.created_by = ctx.author.id

            discord_role = await ctx.guild.create_role(
                name=role_name,
                mentionable=True,
                colour=Colour(random.choice(ROLE_COLOURS)),
                reason="Auto-Generated")

            role.role_id = discord_role.id

            role.save()

            await ctx.author.add_roles(discord_role)
            await ctx.send(f"You have been given the role {role_name}")

    @commands.command(
        name="removeRole",
        help="Takes the role from the issuing user",
        aliases=["iamnot", "iamnota", "takie"])
    @commands.has_role("Member")
    async def remove_role(self, ctx, role_name):
        """
        Removes the given role from the user.
        """

        found_role = Role.where('name', role_name) \
            .where('guild_id', ctx.guild.id).first()

        if found_role:
            discord_guild = self.bot.get_guild(found_role.guild_id)
            discord_role = discord_guild.get_role(found_role.role_id)
            if discord_role is None:
                await ctx.send("That role appears to be broken, "
                               "please contact an admin")
                return
            await ctx.author.remove_roles(discord_role)
            await ctx.send(f"I have removed the role `{role_name}` from you")
            return

    @commands.command(
        name="listRoles",
        help="Takes the role from the issuing user",
        aliases=["roles", "listallroles"])
    @commands.has_role("Member")
    async def list_roles(self, ctx):
        """
        Lists all possible roles a user can get
        """

        found_roles = Role.where('guild_id', ctx.guild.id).get()

        roles = "\n".join([(f"~~{role.name}~~" if role.is_locked else role.name)
                           for role in found_roles])


        embed = Embed(title="Available Roles",
                      description="The following roles have been created by "
                                  "users to allow for more specific tagging, roles that are crossed out are currently locked and cannot be assigned, new roles can be created by requesting the role",
                      color=0x71368a)

        #embed.add_field(name="Roles", value=roles)
        locked_roles = []
        unlocked_roles = []

        for role in found_roles:
            locked_roles.append(role.name) if role.is_locked else unlocked_roles.append(role.name)

        embed.add_field(name=":unlock:", value="\n".join(unlocked_roles))
        embed.add_field(name=":lock:", value="\n".join(locked_roles))

        await ctx.send(embed=embed)


def setup(bot):
    """
    Add the cog to the bot
    """
    bot.add_cog(RoleAssignmentCog(bot))

