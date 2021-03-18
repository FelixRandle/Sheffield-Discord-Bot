#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
A cog to support users sending anonymous confessions to the bot.
"""

import datetime as dt
import re
from typing import Tuple

import discord
from discord.ext import commands

import utils as ut
from models import Compfession

MENTION_REGEX = re.compile(
    "@"  # Starting @ symbol
    r"((?P<last>last|latest|recent)?"  # Checks for references to most recent
    r"(confession|compfession|sheffession)?)?"  # Optional confession word
    r"(?P<id>(?(last)|\d+))(\s+|$)"  # ID is matched if 'last' is not matched
)


def generate_compfession_embed(compfession):
    embed = discord.Embed(color=0xf71e1e)
    embed.add_field(name=f"Confession #{compfession.approved_id}",
                    value=compfession.confession)

    created_at = ut.get_uk_time(compfession.created_at).strftime(
        "%Y-%m-%d %H:%M:%S")
    updated_at = ut.get_uk_time(compfession.updated_at).strftime(
        "%Y-%m-%d %H:%M:%S")
    embed.set_footer(text=f"Created {created_at}\n"
                          f"Approved {updated_at}")

    return embed


class CompfessionsCog(commands.Cog):
    """
    Sheffessions but for computer science
    """

    def __init__(self, bot):
        """Save our bot argument that is passed in to the class."""
        self.bot = bot

    async def _get_compfession_mention(
        self,
        content: str,
        guild: discord.Guild,
        channel: discord.TextChannel = None,
        *,
        before: dt.datetime = None,
    ) -> Tuple[discord.Message, Compfession]:
        """
        Takes a compfession's content, and looks for a mention
        for other compfessions.

        Matches with `@<id>`, `@compfession<id>` or similar,
        and `@lastcompfession` or similar.

        Only returns with the first mention found.
        Subsequent mentions are ignored.

        If specified channel is `None`,
        then corresponding message is not fetched
        """
        content = content.lower()
        match = MENTION_REGEX.search(content)
        if not match:
            return None, None
        if match.group('last'):
            query = Compfession \
                .where('guild_id', guild.id)
            if before is not None:
                query = query.where('updated_at', '<=', before)
            compfession = query \
                .order_by('approved_id', 'desc') \
                .first()
        else:
            query = Compfession \
                .where('guild_id', guild.id) \
                .where('approved_id', match.group('id'))

            compfession = query.first()

        if channel is not None and compfession.message_id is not None:
            message = await channel.fetch_message(compfession.message_id)
        else:
            message = None
        return message, compfession

    @commands.command(
        name="confess",
        aliases=["compfession", "sheffession"],
        help="Confess your darkest secrets and have"
             " them broadcast anonymously.")
    @commands.dm_only()
    async def confess(self, ctx, *, message: str):
        """
        Create a simple ping pong command.

        This command adds some help text and also required that the user
        have the Member role, this is case-sensitive.
        """
        # XXX: Temporary solution before discord.py==1.7.0 release
        mutual_guilds = list(
            filter(lambda guild: ctx.author in guild.members, self.bot.guilds)
        )
        if not mutual_guilds:
            return await ctx.send("You don't share any guilds with the bot!")
        if len(mutual_guilds) > 1:
            guild = await ut.get_choice(
                ctx.channel, ctx.author, self.bot, mutual_guilds,
            )
            if guild is ut.NO_CHOICE:
                return await ctx.send(
                    "You didn't choose a server in time, "
                    "so your compfession hasn't be submitted"
                )
        else:
            guild = mutual_guilds[0]

        Compfession.create(confession=message, guild_id=guild.id)
        await ctx.send("Sent your confession, it will need to get "
                       "moderated before it is posted to servers.")

        confession_channel = discord.utils.get(
            guild.text_channels,
            name="compfessions-notifications")

        if confession_channel:
            await confession_channel.send(
                "There is a new confession to be checked")

    @commands.command(
        name="moderateConfessions",
        help="Moderate outstanding confessions."
    )
    @commands.has_role("Admin")
    async def moderate_confessions(self, ctx):
        compfessions = Compfession \
            .where('approved', False) \
            .where('guild_id', ctx.guild.id) \
            .get()

        for compfession in compfessions:
            embed = discord.Embed(color=0xf71e1e)
            embed.add_field(name="Confession",
                            value=compfession.confession)

            result, reason = await ut.get_confirmation(
                ctx.channel, ctx.author, self.bot, None, embed)

            if result:
                await self.publish_compfession(
                    compfession, ctx.guild, ctx.author)
            elif reason == "Timeout":
                return
            else:
                compfession.delete()

    async def publish_compfession(self, compfession, guild, moderator):
        last_compfession = Compfession \
            .where('guild_id', guild.id) \
            .order_by('approved_id', 'desc') \
            .first()
        if last_compfession is not None:
            compfession.approved_id = last_compfession.approved_id + 1
        else:
            compfession.approved_id = 1
        confession_channel = discord.utils.get(guild.text_channels,
                                               name="compfessions")

        if not confession_channel:
            ut.log(f"Guild {guild.id} is missing 'compfessions' channel")

        embed = generate_compfession_embed(compfession)
        reference, _ = await self._get_compfession_mention(
            compfession.confession,
            guild,
            confession_channel,
            before=compfession.created_at,
        )
        msg = await confession_channel.send(embed=embed, reference=reference)
        compfession.approved = True
        compfession.approved_by = moderator.id
        compfession.message_id = msg.id
        compfession.save()

    @commands.Cog.listener('on_message')
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return
        _, compfession = await self._get_compfession_mention(
            message.content, message.guild)
        if compfession is not None:
            embed = generate_compfession_embed(compfession)
            await message.channel.send(embed=embed)


def setup(bot):
    """
    Add the cog we have made to our bot.

    This function is necessary for every cog file, multiple classes in the
    same file all need adding and each file must have their own setup function.
    """
    bot.add_cog(CompfessionsCog(bot))
