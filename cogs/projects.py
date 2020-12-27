#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A cog for showcasing GitHub project repos
"""

import json
import re
from typing import Optional

import aiohttp
import discord
from discord.ext import commands, tasks

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
        self.update_repo_stats.start()

    async def create_repo_embed(
        self,
        url: str,
        session: aiohttp.ClientSession
    ):
        """
        Creates a Discord embed from a GitHub repo link,
        using the given aiohttp client session

        Returns None if the repo cannot be accessed
        """
        info = self.extract_info_from_url(url)
        data = await self.get_repo_data(session, **info)
        if data is None:
            return None
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

        embed.set_footer(text=data["html_url"])
        return embed

    @staticmethod
    def extract_info_from_url(url: str):
        """
        Extracts owner and repo name info from a GitHub repo link
        """
        match = GITHUB_LINK_REGEX.search(url)
        if not match:
            return None

        info = match.groupdict()
        return info

    async def get_repo_data(
        self,
        session: aiohttp.ClientSession,
        owner: str,
        repo: str,
    ) -> Optional[dict]:
        """
        Retrieves repo data from the GitHub API for the given owner
        and repo number, using the given aiohttp client session
        """
        url = API_TEMPLATE.format(owner=owner, repo=repo)
        async with session.get(url) as response:
            if response.status != 200:
                return None
            body = await response.text()
        data = json.loads(body)
        return data

    @tasks.loop(hours=24)
    async def update_repo_stats(self):
        async with aiohttp.ClientSession() as session:
            for guild in self.bot.guilds:
                projects_channel = ut.find_channel_by_name("projects", guild)
                if projects_channel is None:
                    continue

                async for msg in projects_channel.history():
                    embed = msg.embeds[0]
                    url = embed.footer.text
                    embed = await self.create_repo_embed(url, session)
                    if embed is None:
                        await msg.delete()
                    else:
                        await msg.edit(embed=embed)

    @update_repo_stats.before_loop
    async def before_update_repo_stats(self):
        await self.bot.wait_until_ready()

    @commands.command(help="Showcase your projects on GitHub")
    async def project(self, ctx, *, repo_link: str):
        """
        Allows users to showcase projects from GitHub using GitHub repo links

        Extracts info from the repo and displays it in an embed
        """
        projects_channel = ut.find_channel_by_name("projects", ctx.guild)
        if projects_channel is None:
            return await ctx.send(
                "Could not find projects channel to post project in")

        async with aiohttp.ClientSession() as session:
            embed = await self.create_repo_embed(repo_link, session)

        if embed is None:
            return await ctx.send(
                "Could not access repo. "
                "Check that the repo exists and is not private")

        await projects_channel.send(
            f"{ctx.author.mention} has shared this project on GitHub:",
            embed=embed)

        await ctx.send("GitHub repo shared!")


def setup(bot):
    """
    Add the cog to the bot.
    """
    bot.add_cog(ProjectsCog(bot))
