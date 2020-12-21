#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A cog for showcasing GitHub project repos
"""

import json
import re

import aiohttp
import discord
from discord.ext import commands

import utils as ut


GITHUB_LINK_REGEX = re.compile(
    r"github.com/(?P<owner>[a-zA-Z0-9-]+)/(?P<repo>[a-zA-Z0-9-_]+)")
API_TEMPLATE = "https://api.github.com/repos/{owner}/{repo}"

FIELD_PARAMS = [
    ("Link", ("html_url",), False),
    ("Language", ("language",), True),
    ("Stars", ("stargazers_count",), True),
]


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
        projects_channel = ut.find_channel_by_name("projects", ctx.guild)
        if projects_channel is None:
            return await ctx.send(
                "Could not find projects channel to post project in")

        match = GITHUB_LINK_REGEX.search(repo_link)
        if not match:
            return await ctx.send("GitHub repo link is invalid")

        params = match.groupdict()
        url = API_TEMPLATE.format(**params)

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    return await ctx.send(
                        "Could not access repo. "
                        "Check that the repo exists and is not private")
                body = await response.text()

        data = json.loads(body)
        embed = discord.Embed(
            title=data["name"], description=data["description"])
        embed.set_author(
            name=data["owner"]["login"],
            url=data["owner"]["html_url"],
            icon_url=data["owner"]["avatar_url"]
        )

        for name, keys, inline in FIELD_PARAMS:
            value = data
            for key in keys:
                value = value[key]
            embed.add_field(name=name, value=value, inline=inline)

        await projects_channel.send(ctx.author.mention, embed=embed)


def setup(bot):
    """
    Add the cog to the bot.
    """
    bot.add_cog(ProjectsCog(bot))
