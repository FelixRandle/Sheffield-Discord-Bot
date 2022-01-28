#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
A cog to support users sending anonymous confessions to the bot.
"""

import datetime as dt
import re
from typing import Tuple

import discord
from discord import NotFound
from discord.ext import commands

import utils as ut
from models import Compfession

# Compfession mention mini-language
#
# mention          = at_symbol identifier terminator ;
# identifer        = id | last_word compfession_word | compfession_word id ;
# terminator       = whitespace+ | end-of-string ;
# id               = digit+ ;
# at_symbol        = "@" ;
# last_word        = "last" | "latest" | "recent" ;
# compfession_word = "compfession" | "confession" | "sheffession" ;
# whitespace       = " " | "\t" | "\n" | "\r" | "\f" | "\v" ;
# digit            = "0" | "1" | "2" | "3" | "4"
#                  | "5" | "6" | "7" | "8" | "9" ;

COMPFESSION_REGEX = r"((confe|compfe|sheffe)ssion)"
MENTION_REGEX = re.compile(
    "@"
    # Checks for references to most recent
    rf"(?P<last>(last|latest|recent){COMPFESSION_REGEX})?"
    # ID mentions are matched if 'last' is not matched
    rf"(?(last)|{COMPFESSION_REGEX}?(?P<id>\d+))(\s+|$)"
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


async def get_compfession_mention(
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

    if (
        channel is not None
        and compfession is not None
        and compfession.message_id is not None
    ):
        message = await channel.fetch_message(compfession.message_id)
    else:
        message = None
    return message, compfession


class CompfessionsCog(commands.Cog):
    """
    Sheffessions but for computer science
    """

    def __init__(self, bot):
        """Save our bot argument that is passed in to the class."""
        self.bot = bot

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
        name="moderateCompfessions",
        aliases=("moderateConfessions",),
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

            result = await ut.get_react(
                ctx.channel, ctx.author, self.bot, None, ["👍", "👎", "➡️"], embed)

            if result == "👍":
                last_compfession = Compfession.where(
                    "approved", True).order_by('id', 'desc').first()
                if last_compfession is not None:
                    compfession.approved_id = last_compfession.approved_id + 1
                else:
                    compfession.approved_id = 1
                compfession.approved = True
                compfession.approved_by = ctx.author.id
                compfession.save()
                print(compfession.created_at)
                print(compfession.updated_at)
                await self.publish_compfession(compfession, ctx.guild, ctx.author)
            elif result == "👎":
                compfession.delete()
            elif result == "➡️":
                continue

    @commands.command(
        name="deleteCompfession",
        aliases=("deleteConfession",),
    )
    @commands.has_role("Admin")
    async def delete_compfession(self, ctx, compfession: Compfession):
        result, _ = await ut.get_confirmation(
            ctx.channel,
            ctx.author,
            self.bot,
            "Are you sure you want to delete this compfession?"
        )
        if not result:
            return

        compfession.delete()
        if compfession.message_id is not None:
            channel = discord.utils.get(
                ctx.guild.text_channels, name="compfessions")
            if channel is not None:
                try:
                    compfession_msg = await channel.fetch_message(
                        compfession.message_id)
                except NotFound:
                    pass
                else:
                    await compfession_msg.delete()
        await ctx.send("Compfession deleted")

    async def publish_compfession(self, compfession, guild, moderator):
        last_compfession = Compfession \
            .where('guild_id', guild.id) \
            .order_by('approved_id', 'desc') \
            .first()
        if (
            last_compfession is not None
            and last_compfession.approved_id is not None
        ):
            compfession.approved_id = last_compfession.approved_id + 1
        else:
            compfession.approved_id = 1
        confession_channel = discord.utils.get(guild.text_channels,
                                               name="compfessions")

        if not confession_channel:
            ut.log(f"Guild {guild.id} is missing 'compfessions' channel")

        embed = generate_compfession_embed(compfession)
        reference, _ = await get_compfession_mention(
            compfession.confession,
            guild,
            confession_channel,
            before=compfession.created_at,
        )
        compfession.save()
        msg = await confession_channel.send(embed=embed, reference=reference)
        compfession.approved = True
        compfession.approved_by = moderator.id
        compfession.message_id = msg.id
        compfession.save()

    @commands.Cog.listener('on_message')
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return
        _, compfession = await get_compfession_mention(
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
