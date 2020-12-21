#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
A cog to support users sending anonymous confessions to the bot.
"""
# In this case, discord import is not needed, in some cases it may be.
import discord
from discord.ext import commands

from models.compscession import Compscession
import utils as ut


class CompscessionsCog(commands.Cog):
    """The ping to your pong"""

    def __init__(self, bot):
        """Save our bot argument that is passed in to the class."""
        self.bot = bot

    @commands.command(
        name="confess",
        alias=["compscession", "sheffession"],
        help="Confess your darkest secrets and have"
             " them broadcast anonymously.")
    @commands.dm_only()
    async def confess(self, ctx, *, message: str):
        """
        Create a simple ping pong command.

        This command adds some help text and also required that the user
        have the Member role, this is case-sensitive.
        """
        compscession = Compscession()

        compscession.confession = message

        compscession.save()

        await ctx.send("Sent your confession, it will need to get "
                       "moderated before it is posted to servers.")

        for guild in self.bot.guilds:
            confession_channel = discord.utils.get(
                guild.text_channels,
                name="compscessions-notifications")

            if confession_channel:
                await confession_channel.send(
                    "There is a new confession to be checked")

    @commands.command(
        name="moderateConfessions",
        help="Moderate outstanding confessions."
    )
    @commands.has_role("Admin")
    async def moderate_confessions(self, ctx):
        compscessions = Compscession.where('approved', False).get()

        for compscession in compscessions:
            embed = discord.Embed(color=0xf71e1e)
            embed.add_field(name="Confession",
                            value=compscession.confession)

            result, reason = await ut.get_confirmation(ctx.channel,
                                                       ctx.author,
                                                       self.bot,
                                                       None, embed)

            if result:
                compscession.approved = True
                compscession.approved_by = ctx.author.id
                compscession.save()
                await self.publish_compscession(compscession)
            elif reason == "Timeout":
                return
            else:
                compscession.delete()

    async def publish_compscession(self, compscession):
        for guild in self.bot.guilds:
            confession_channel = discord.utils.get(guild.text_channels,
                                                   name="compscessions")

            if confession_channel:
                embed = discord.Embed(color=0xf71e1e)
                embed.add_field(name="Confession",
                                value=compscession.confession)

                created_at = ut.get_uk_time(compscession.created_at).strftime(
                    "%Y-%m-%d %H:%M:%S")
                updated_at = ut.get_uk_time(compscession.updated_at).strftime(
                    "%Y-%m-%d %H:%M:%S")
                embed.set_footer(text=f"Created {created_at}\n"
                                      f"Approved {updated_at}")
                await confession_channel.send(embed=embed)
            else:
                ut.log(f"Guild {guild.id} is missing 'compscessions' channel")


def setup(bot):
    """
    Add the cog we have made to our bot.

    This function is necessary for every cog file, multiple classes in the
    same file all need adding and each file must have their own setup function.
    """
    bot.add_cog(CompscessionsCog(bot))
