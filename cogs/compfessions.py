#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
A cog to support users sending anonymous confessions to the bot.
"""

import discord
from discord.ext import commands

import utils as ut
from models.compfession import Compfession


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
        compfession = Compfession()
        compfession.confession = message
        compfession.save()

        await ctx.send("Sent your confession, it will need to get "
                       "moderated before it is posted to servers.")

        for guild in self.bot.guilds:
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
        compfessions = Compfession.where('approved', False).get()

        for compfession in compfessions:
            embed = discord.Embed(color=0xf71e1e)
            embed.add_field(name="Confession",
                            value=compfession.confession)

            result, reason = await ut.get_confirmation(
                ctx.channel, ctx.author, self.bot, None, embed)

            if result:
                last_compfession = Compfession.where(
                    "approved", True).order_by('id', 'desc').first()
                if last_compfession is not None:
                    compfession.approved_id = last_compfession.approved_id + 1
                else:
                    compfession.approved_id = 1
                compfession.approved = True
                compfession.approved_by = ctx.author.id
                compfession.save()
                await self.publish_compfession(compfession)
            elif reason == "Timeout":
                return
            else:
                compfession.delete()

    async def publish_compfession(self, compfession):
        for guild in self.bot.guilds:
            confession_channel = discord.utils.get(guild.text_channels,
                                                   name="compfessions")

            if confession_channel:
                embed = generate_compfession_embed(compfession)
                await confession_channel.send(embed=embed)
            else:
                ut.log(f"Guild {guild.id} is missing 'compfessions' channel")

    @commands.Cog.listener('on_message')
    async def on_message(self, message):
        content = message.content.lower()
        searching_id = None
        compfession = None
        if content.startswith('@compfession'):
            searching_id = content.split(" ")[0][12:]
        elif content.startswith('@confession'):
            searching_id = content.split(" ")[0][11:]
        elif content.startswith('@recentcompfession') \
                or content.startswith('@recentconfession') \
                or content.startswith('@latestconfession') \
                or content.startswith('@latestconfession'):
            compfession = Compfession.order_by('approved_id', 'desc').first()

        if searching_id is not None or compfession is not None:
            compfession = Compfession.where(
                "approved_id", searching_id).first() \
                if compfession is None else compfession

            if compfession is not None:
                embed = generate_compfession_embed(compfession)
                await message.channel.send(embed=embed)
            else:
                await message.channel.send(
                    "Sorry, I couldn't find a compfession with that ID")


def setup(bot):
    """
    Add the cog we have made to our bot.

    This function is necessary for every cog file, multiple classes in the
    same file all need adding and each file must have their own setup function.
    """
    bot.add_cog(CompfessionsCog(bot))
