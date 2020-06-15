#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Cog for simple utility functions for the bot."""

from discord.ext import commands

import database as db
import utils as ut


class BasicCommandsCog(commands.Cog):
    """Create a class that extends Cog to make our functionality in."""

    def __init__(self, bot):
        """Save our bot argument that is passed in to the class."""
        self.bot = bot

    @commands.command(
        name="updateUsers",
        help="Updates user list on the database")
    @commands.has_role("Admin")
    async def update_users(self, ctx):
        """
        Create a simple ping pong command.

        This command adds some help text and also required that the user
        have the Member role, this is case-sensitive.
        """
        for member in ctx.guild.members:
            await db.add_user(member.id, member.bot)

        await ctx.send("Added all users to database!")

    @commands.command(
        name="setRegistering",
        help="Sets the role assigned to new members of the guild")
    @commands.has_role("Admin")
    async def set_registering_role(self, ctx, role_id):
        """
        Updates the registeringID for the guild.

        This command allows admins to update the role first given to users
        when they join the guild.
        """

        role = ctx.guild.get_role(role_id)
        if role is None:
            await ctx.send("Could not find a valid role. Please ensure you "
                           "have properly entered the role ID.")

        result = await db.set_guild_info(ctx.guild.id, "registeringID",
                                         role_id)
        if result is False:
            await ctx.send("Failed to update role id. Please try again later.")
        else:
            await ctx.send(f"Successfully updated member role to {role.name}.")

    @commands.command(
        name="setMember",
        help="Sets the role assigned to registered members of the guild")
    @commands.has_role("Admin")
    async def set_member_role(self, ctx, role_id):
        """
        Updates the memberID for the guild.

        This command allows admins to update the role given to users once
        they have 'accepted' the guilds rules.
        """

        role = ctx.guild.get_role(role_id)
        if role is None:
            await ctx.send("Could not find a valid role. Please ensure you "
                           "have properly entered the role ID.")

        result = await db.set_guild_info(ctx.guild.id, "memberID", role_id)
        if result is False:
            await ctx.send("Failed to update role id. Please try again later.")
        else:
            await ctx.send(f"Successfully updated member role to {role.name}.")

    @commands.command(
        name="setWelcomeMsg",
        help="Creates a welcome message for users to react to"
             "to become members.")
    @commands.has_role("Admin")
    async def set_welcome_msg(self, ctx, *, content: str):
        """
        Updates the welcome message for the guild.

        This command allows admins to update the welcome message that
        users must react to when they wish to become members.
        """
        if len(content) == 0:
            await ctx.send("You must include a message.")
            return

        if await ut.get_confirmation(ctx.channel, ctx.author, self.bot,
                                     "You are about to set the servers welcome"
                                     f"message to\n ```{content}```\n"
                                     "Please react with a thumbs up "
                                     "to confirm."):
            message = await ctx.send(content)
            await message.add_reaction(u"\u2705")
            await message.add_reaction(u"\u274E")

            await db.set_guild_info(ctx.guild.id, "welcomeMessageID",
                                    message.id)

    @commands.command(
        name="echo",
        help="Repeats after you.")
    @commands.has_role("Admin")
    async def echo(self, ctx, *, content: str):
        """
        Repeats the users message

        This command allows admins to get the bot to create messages.
        Mainly for announcement purposes.
        """
        if len(content) == 0:
            await ctx.send("You must include a message.")
            return

        await ctx.send(content)

    @commands.command(
        name="clear",
        help="Clears messages from the channel")
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, message_count: int):
        """
        Clears the given amount of messages from the channels history.

        Clears an extra one to remove the commands message.
        """
        await ctx.channel.purge(limit=message_count + 1)


def setup(bot):
    """
    Add the cog we have made to our bot.

    This function is necessary for every cog file, multiple classes in the
    same file all need adding and each file must have their own setup function.
    """
    bot.add_cog(BasicCommandsCog(bot))
