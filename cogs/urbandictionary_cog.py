#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
The Urban Dictionary cog written by Ben Ridings,
You can randomly search a word or search a specific word
"""
import json

import aiohttp
from discord.ext import commands

# Constantы
BASEURL = 'https://api.urbandictionary.com/v0/'


class UrbanDictionaryCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # Search a word the user types in
    async def search_query(self, querystring):
        async with aiohttp.ClientSession() as session:
            data = await self.fetch(
                session, BASEURL + f'define?term={querystring}')
            return data

    # Fetch the URL
    async def fetch(self, session, url):
        async with session.get(url) as response:
            return await response.text()

    # Search up a random word
    async def search_random_word(self):
        async with aiohttp.ClientSession() as session:
            data = await self.fetch(session, BASEURL + 'random')
            return data

    # Parse the searched word and display here
    @commands.command(name='ud')
    async def search_dictionary(self, ctx, *, query=None):
        if query is None:
            response_text = await self.search_random_word()
        else:
            response_text = await self.search_query(query)

        definitions_list = json.loads(response_text)['list']
        definition = definitions_list[0]

        await ctx.send(
            "Definition of {word}: {definition}".format(**definition))
        await ctx.send("Example of {word}: {example}".format(**definition))


def setup(bot):
    bot.add_cog(UrbanDictionaryCog(bot))
