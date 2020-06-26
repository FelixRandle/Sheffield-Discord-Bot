#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Cog for simple utility functions for the bot."""
import discord
from discord.ext import commands

import utils as ut
from models import User, Guild


class BasicCommandsCog(commands.Cog):
    """Create a class that extends Cog to make our functionality in."""
    _user_info = []

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
            if not member.bot:
                User.first_or_create(id=member.id, guild_id=ctx.guild.id)

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

        if not ctx.message.role_mentions:
            await ctx.send("Could not find a valid role. Please ensure you "
                           "have properly entered the role ID.")
            return

        guild = Guild.find(ctx.guild.id)
        if guild is None:
            await ctx.send("Failed to update role ID: guild was not found")
            return

        role = ctx.message.role_mentions[0]

        guild.registering_id = role.id
        guild.save()

        await ctx.send(
            f"Successfully updated registering role to {role.name}.")

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

        if not ctx.message.role_mentions:
            await ctx.send("Could not find a valid role. Please ensure you "
                           "have properly entered the role ID.")
            return

        guild = Guild.find(ctx.guild.id)
        if guild is None:
            await ctx.send("Failed to update role ID: guild was not found")
            return

        role = ctx.message.role_mentions[0]

        guild.member_id = role.id
        guild.save()

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

            guild = Guild.find(ctx.guild.id)
            guild.welcome_message_id = message.id

            guild.save()

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

    @commands.command(
        name="whois",
        help="Gives you information about a specific user")
    @commands.has_role("Member")
    async def who_is(self, ctx):
        if not len(ctx.message.mentions):
            raise commands.errors.UserInputError(message="Please tag a user")

        user = ctx.message.mentions[0]

        join_date = ut.get_uk_time(user.joined_at).strftime(
            "%Y-%m-%d %H:%M:%S")

        user_roles = " ".join(role.mention if role.name != "@everyone" else ""
                              for role in user.roles)

        embed = (discord.Embed(title=f"{user}", description=f"{user.mention}",
                               color=discord.Color.blurple())
                 .set_thumbnail(url=user.avatar_url)
                 .add_field(name="Joined At", value=join_date)
                 .add_field(name="Assigned Roles",
                            value=user_roles, inline=False)
                 .set_footer(text=f"User ID: {user.id}"))

        for name, value_getter, inline in self._user_info:
            embed.add_field(name=name, value=value_getter(user), inline=inline)

        await ctx.send(embed=embed)

    @staticmethod
    def add_user_info(name, value_getter, inline=False):
        BasicCommandsCog._user_info.append(
            (name, value_getter, inline)
        )

    @commands.command(
        name="serverinfo",
        help="Gives you information about the current server")
    @commands.has_role("Member")
    async def server_info(self, ctx):
        guild_roles = " ".join(role.mention if role.name != "@everyone" else ""
                               for role in ctx.guild.roles)

        created_at = ut.get_uk_time(ctx.guild.created_at).strftime(
            "%Y-%m-%d %H:%M:%S")

        embed = (discord.Embed(title=f"{ctx.guild.name}",
                               color=discord.Color.blurple())
                 .set_thumbnail(url=str(ctx.guild.icon_url))
                 .add_field(name="Owner", value=ctx.guild.owner.mention)
                 .add_field(name="Created at", value=created_at)
                 .add_field(name="Region", value=ctx.guild.region)
                 .add_field(name="Member Count", value=ctx.guild.member_count)
                 .add_field(name="Text Channel Count",
                            value=len(ctx.guild.text_channels))
                 .add_field(name="Voice Channel Count",
                            value=len(ctx.guild.voice_channels))
                 .add_field(name="Available Roles", value=guild_roles,
                            inline=False)
                 .set_footer(text=f"Guild ID: {ctx.guild.id}"))

        await ctx.send(embed=embed)


def setup(bot):
    """
    Add the cog we have made to our bot.

    This function is necessary for every cog file, multiple classes in the
    same file all need adding and each file must have their own setup function.
    """
    bot.add_cog(BasicCommandsCog(bot))
