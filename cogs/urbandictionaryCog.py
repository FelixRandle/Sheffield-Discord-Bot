 #!/usr/bin/env python
# -*- coding: utf-8 -*- 
""" 
The Urban Dictionary cog written by Ben Ridings,
You can randomly search a word or search a specific word
"""
import json

import aiohttp
import discord
from discord.ext import commands

# Constants
LIST = 'list'
DEFINTION = 'definition'
EXAMPLE = 'example'
BASEURL = 'https://api.urbandictionary.com/v0/'

class UrbanDictionaryCog(commands.Cog):
   
    def __init__(self, bot):
        self.bot = bot
    
    # Search a word the user types in
    async def search_query(self, querystring):
        async with aiohttp.ClientSession() as session:
            data = await self.fetch(session, BASEURL+ f'define?term={querystring}')
            return data

    # Fetch the URL
    async def fetch(self, session, url):
        async with session.get(url) as response:
            return await response.text()

    # Search up a random word
    async def search_random_word(self):
        async with aiohttp.ClientSession() as session:
            data = await self.fetch(session, BASEURL+ 'random')
            return data

    # Parse the searched word and display here
    @commands.command(name='search')
    async def search_dictionary(self, ctx, *, query):
        # Gets the typed in query and parses it
        querystring = query
        definition_list = json.loads(await self.search_query(querystring))[LIST]

        definition = definition_list[0][DEFINTION]
        example = definition_list[0][EXAMPLE]

        await ctx.send("Definition of " + querystring + " :" + definition)
        await ctx.send("Example of " + querystring + " :" + example)

    # Parse the random word and display here
    @commands.command(name='random')
    async def random(self, ctx):
        definition_list = json.loads(await self.search_random_word())[LIST]

        definition = definition_list[0][DEFINTION]
        example = definition_list[0][EXAMPLE]
        await ctx.send("Random word -> " +definition_list[0]['word'])
        await ctx.send(definition)
        await ctx.send(example)

def setup(bot):
    bot.add_cog(UrbanDictionaryCog(bot))