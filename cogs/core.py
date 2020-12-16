#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Cog for simple utility functions for the bot."""
import discord
from discord.ext import commands

import utils as ut
from models import User, Guild, Role


class CoreCog(commands.Cog):
    """Basic server commands."""
    _user_info = []
    _server_info = []

    def __init__(self, bot):
        """Save our bot argument that is passed in to the class."""
        self.bot = bot


    @commands.Cog.listener("on_guild_join")
    async def on_guild_join(self, guild):
        registering_id = None
        member_id = None
        for role in guild.roles:
            if role.name.lower() == "registering":
                registering_id = role.id
            if role.name.lower() == "member":
                member_id = role.id

        Guild.first_or_create(
            id=guild.id, registering_id=registering_id, member_id=member_id)

    @commands.Cog.listener("on_member_join")
    async def on_member_join(self, member):
        """Send user a welcome message."""
        if member.bot:
            return

        try:  # Avoid throwing errors on users with friend-only DMs.
            await member.create_dm()
            await member.dm_channel.send(
                f'Hey {member.name}, welcome to the (unofficial) University of '
                'Sheffield Computer Science Discord!\n'
                'We like to know who we\'re talking to, so please change your '
                'nickname on the server to include your real name in some way.\n'
                'Apart from that, have fun on the server, get to know people and '
                'feel free to ask any questions about the course that you may have, '
                'we\'re all here to help each other!\n'
                'Many thanks,\n'
                'The Discord Server Admin Team\n\n'
                'As a note, all messages that you send on the server are logged.\n'
                'This is to help us in the case of messages that contain'
                'offensive content and need to be reported.\n'
                'If you would like your logged messages to be'
                'removed for any reason, please contact <@247428233086238720>.'
            )
        except discord.Forbidden:
            pass
        guild = Guild.find(member.guild.id)

        User.first_or_create(id=member.id, guild_id=guild.id)

        role_id = guild.registering_id
        await ut.add_role(member, role_id)


    @commands.Cog.listener("on_raw_reaction_add")
    async def on_raw_reaction_add(self, payload):
        if payload.member.bot:
            return

        guild = Guild.find(payload.guild_id)
        expected_id = guild.welcome_message_id
        if payload.message_id == expected_id:
            message = await payload.member.guild.get_channel(payload.channel_id) \
                .fetch_message(payload.message_id)
            await message.remove_reaction(payload.emoji, payload.member)
            if payload.emoji.name == u"\u2705":
                registering_id = guild.registering_id
                member_id = guild.member_id

                await ut.add_role(payload.member, member_id)
                await ut.remove_role(payload.member, registering_id)

            elif payload.emoji.name == u"\u274E":
                await payload.member.guild.kick(payload.member,
                                                reason="Rejected T's&C's")

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
        added_count = 0
        for member in ctx.guild.members:
            if not member.bot:
                User.first_or_create(id=member.id, guild_id=ctx.guild.id)
                added_count += 1

        await ctx.send(f"Added {added_count} new {'users' if added_count != 1 else 'user'} to database!")

    @commands.command(
        name="setRegistering",
        help="Sets the role assigned to new members of the guild")
    @commands.has_role("Admin")
    async def set_registering_role(self, ctx):
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
    async def set_member_role(self, ctx):
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
        if not ctx.message.mentions:
            raise commands.errors.UserInputError(message="Please tag a user")

        discord_user = ctx.message.mentions[0]

        if discord_user.bot:
            return await ctx.send("I can't help you with information "
                                  "about bots.")

        user = User.find(discord_user.id)

        if user is None:
            return await ctx.send("I couldn't find that user in my database, "
                                  "that's not supposed to happen...")

        join_date = ut.get_uk_time(discord_user.joined_at).strftime(
            "%Y-%m-%d %H:%M:%S")

        user_roles = " ".join(role.mention if role.name != "@everyone" else ""
                              for role in discord_user.roles)

        user = User.find(discord_user.id)

        message_count = user.messages.count()

        embed = (discord.Embed(title=f"{discord_user}",
                               description=f"{discord_user.mention}",
                               color=discord.Color.blurple())
                 .set_thumbnail(url=discord_user.avatar_url)
                 .add_field(name="Joined At", value=join_date)
                 .add_field(name="Assigned Roles",
                            value=user_roles, inline=False)
                 .add_field(name="Message Count", value=message_count)
                 .set_footer(text=f"User ID: {discord_user.id}"))

        for name, value_getter, inline in self._user_info:
            embed.add_field(name=name, value=value_getter(discord_user),
                            inline=inline)

        await ctx.send(embed=embed)

    @classmethod
    def add_user_info(cls, name, value_getter, inline=False):
        cls._user_info.append(
            (name, value_getter, inline)
        )

    @commands.command(
        name="serverinfo",
        aliases=["server"],
        help="Gives you information about the current server")
    @commands.has_role("Member")
    async def server_info(self, ctx):
        guild = ctx.guild

        custom_roles = [role.name for role in
                        Role.where('guild_id', ctx.guild.id).get()]

        custom_roles.append("@everyone")

        guild_roles = " ".join(role.mention
                               if role.name not in custom_roles else ""
                               for role in guild.roles)

        created_at = ut.get_uk_time(guild.created_at).strftime(
            "%Y-%m-%d %H:%M:%S")

        embed = (discord.Embed(title=f"{guild.name}",
                               color=discord.Color.blurple())
                 .set_thumbnail(url=str(guild.icon_url))
                 .add_field(name="Owner", value=guild.owner.mention)
                 .add_field(name="Created at", value=created_at)
                 .add_field(name="Region", value=guild.region)
                 .add_field(name="Member Count", value=guild.member_count)
                 .add_field(name="Text Channel Count",
                            value=len(guild.text_channels))
                 .add_field(name="Voice Channel Count",
                            value=len(guild.voice_channels))
                 .add_field(name="Available Roles", value=guild_roles,
                            inline=False)
                 .set_footer(text=f"Guild ID: {guild.id}"))

        for name, value_getter, inline in self._server_info:
            embed.add_field(name=name, value=value_getter(guild),
                            inline=inline)

        await ctx.send(embed=embed)

    @classmethod
    def add_server_info(cls, name, value_getter, inline=False):
        cls._server_info.append(
            (name, value_getter, inline)
        )


def setup(bot):
    """
    Add the cog we have made to our bot.

    This function is necessary for every cog file, multiple classes in the
    same file all need adding and each file must have their own setup function.
    """
    bot.add_cog(CoreCog(bot))
