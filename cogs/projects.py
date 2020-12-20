#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A cog for showcasing GitHub project repos
"""

import re

from discord.ext import commands


GITHUB_LINK_REGEX = re.compile(r"github.com/(?P<owner>\S+)/(?P<repo>\S+)")
API_TEMPLATE = "https://api.github.com/repos/{owner}/{repo}"


class ProjectsCog(commands.Cog, name="Projects"):
    """Show off your projects"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(help="Showcase your projects on GitHub")
    @commands.has_role("Member")
    async def project(self, ctx, *, repo_link: str):
        """
        Allows users to showcase projects from GitHub using GitHub repo links

        Extracts info from the repo and displays it in an embed
        """
        match = GITHUB_LINK_REGEX.search(repo_link)
        await ctx.send("Link valid" if match else "Link invalid")


def setup(bot):
    """
    Add the cog to the bot.
    """
    bot.add_cog(ProjectsCog(bot))
