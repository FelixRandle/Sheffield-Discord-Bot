#!/usr/bin/env python
# -*- coding: utf-8 -*- 
"""Cog for simple utility functions for the bot."""
# In this case, discord import is not needed, in some cases it may be.
# import discord
import asyncio

from discord.ext import commands

import database as db
import re

# Create a regex for finding id's within messages
re_message_id = re.compile("\d{18}")


async def find_id(msg):
    result = re_message_id.search(msg)
    if result:
        return int(msg[result.start():result.end()])
    return False


class BasicCommandsCog(commands.Cog):
    """Create a class that extends Cog to make our functionality in."""

    def __init__(self, bot):
        """Save our bot argument that is passed in to the class."""
        self.bot = bot

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
        with ctx.typing():
            for member in ctx.guild.members:
                await db.add_user(member)

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
        with ctx.typing:
            role_id = await find_id(role)
            if role_id is False:
                await ctx.send("Could not find a valid role. Please tag the role you wish to set.")
                return

            role = ctx.guild.get_role(role_id)
            if role is None:
                await ctx.send("Could not find a valid role. Please ensure you have properly entered the role ID.")

            result = await db.set_guild_info(ctx.guild.id, "registeringID", role_id)
            if result is False:
                await ctx.send("Failed to update role id. Please try again later.")
            else:
                await ctx.send(f"Successfully updated member role to {role.name}.")

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
        with ctx.typing:
            role_id = await find_id(role)
            if role_id is False:
                await ctx.send("Could not find a valid role. Please tag the role you wish to set.")
                return

            role = ctx.guild.get_role(role_id)
            if role is None:
                await ctx.send("Could not find a valid role. Please ensure you have properly entered the role ID.")

            result = await db.set_guild_info(ctx.guild.id, "memberID", role_id)
            if result is False:
                await ctx.send("Failed to update role id. Please try again later.")
            else:
                await ctx.send(f"Successfully updated member role to {role.name}.")

    @commands.command(
        name="setwelcomemsg",
        help="Creates a welcome message for users to react to to become members.")
    @commands.has_role("Admin")
    async def set_welcome_msg(self, ctx, *, content: str):
        """
        Updates the welcome message for the guild.

        This command allows admins to update the welcome message that users must
        react to when they wish to become members.
        """
        if len(content) == 0:
            await ctx.send("You must include a message.")
            return

        confirm_message = await ctx.send("You are about to set the servers welcome message to\n"
                                         "```" + content + "```\n"
                                                           "Please react with a thumbs up to confirm.")

        def check(check_reaction, check_user):
            return check_user == ctx.author and str(check_reaction.emoji) == u"\u1F44D" \
                   and check_reaction.message == confirm_message

        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
        except asyncio.TimeoutError:
            await confirm_message.delete()
            await ctx.send('You didn\'t respond in time. '
                           'Please enter the command again if you wish to change the welcome message')
        else:
            await confirm_message.delete()

            message = await ctx.send(content)
            await message.add_reaction(u"\u2705")
            await message.add_reaction(u"\u274E")

            await db.set_guild_info(ctx.guild.id, "welcomeMessageID", message.id)

    @commands.command(
        name="echo",
        help="Repeats after you.")
    @commands.has_role("Admin")
    async def echo(self, ctx, *, content: str):
        """
        Repeats the users message

        This command allows admins to get the bot to create messages. Mainly for announcement purposes
        """
        if len(content) == 0:
            await ctx.send("You must include a message.")
            return

        await ctx.send(content)


def setup(bot):
    """
    Add the cog we have made to our bot.

    This function is necessary for every cog file, multiple classes in the
    same file all need adding and each file must have their own setup function.
    """
    bot.add_cog(BasicCommandsCog(bot))
