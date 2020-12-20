#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A cog for showcasing GitHub project repos
"""

from discord.ext import commands


class ProjectsCog(commands.Cog, name="Projects"):
    """Show off your projects"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(help="Showcase your projects on GitHub")
    @commands.has_role("Member")
    async def projects(self, ctx):
        """
        Allows users to showcase projects from GitHub using GitHub repo links

        Extracts info from the repo and displays it in an embed
        """
        pass


def setup(bot):
    """
    Add the cog to the bot.
    """
    bot.add_cog(ProjectsCog(bot))
