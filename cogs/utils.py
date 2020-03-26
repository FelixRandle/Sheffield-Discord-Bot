"""Cog for simple utility functions for the bot."""
# In this case, discord import is not needed, in some cases it may be.
# import discord
from discord.ext import commands

import database
import re


# Create a regex for finding id's within messages
re_message_id = re.compile("(?:<@&)([0-9])+(?:>)")


async def find_id(msg):
    result = re_message_id.match(msg)
    if result:
        return int(msg[result.start() + 3:result.end() - 1])
    return False


class UtilCog(commands.Cog):
    """Create a class that extends Cog to make our functionality in."""

    def __init__(self, bot):
        """Save our bot argument that is passed in to the class."""
        self.bot = bot

        self.db = database.Database()

    @commands.command(
        name="updateusers",
        help="Updates user list on the database")
    @commands.has_role("Admin")
    async def update_users(self, ctx):
        """
        Create a simple ping pong command.

        This command adds some help text and also required that the user
        have the Member role, this is case-sensitive.
        """
        await ctx.send("Updating user list...")
        for member in ctx.guild.members:
            self.db.add_user(member)

        await ctx.send("Added all users to database!")

    @commands.command(
        name="setregistering",
        help="Sets the role assigned to new members of the guild")
    @commands.has_role("Admin")
    async def set_registering_role(self, ctx, role):
        """
        Updates the registeringID for the guild.

        This command allows admins to update the role first given to users
        when they join the guild.
        """
        print("registering",role)

    @commands.command(
        name="setmember",
        help="Sets the role assigned to reigstered members of the guild")
    @commands.has_role("Admin")
    async def set_member_role(self, ctx, role):
        """
        Updates the memberID for the guild.

        This command allows admins to update the role given to users once
        they have 'accepted' the guilds rules.
        """
        role_id = await find_id(role)
        if role_id is False:
            await ctx.send("Could not find a valid role. Please tag the role you wish to set.")
            return
        print(role_id)
        role = ctx.guild.get_role(role_id)
        print(ctx.guild.roles)
        print(ctx.guild.get_role)
        print(role)
        if role is None:
            await ctx.send("Could not find a valid role. Please ensure you have properly entered the role ID.")

        result = await self.db.set_guild_info(ctx.guild.id, "memberID", role_id)
        if result is False:
            await ctx.send("Failed to update role id. Please try again later.")
        else:
            await ctx.send(f"Successfully updated member role to {role.name}.")


def setup(bot):
    """
    Add the cog we have made to our bot.

    This function is necessary for every cog file, multiple classes in the
    same file all need adding and each file must have their own setup function.
    """
    bot.add_cog(UtilCog(bot))
