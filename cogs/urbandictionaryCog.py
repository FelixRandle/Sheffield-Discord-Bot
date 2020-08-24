#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
The Urban Dictionary cog written by Ben Ridings,
You can randomly search a word or search a specific word
"""
import json

import aiohttp
from discord.ext import commands

# Constants
BASEURL = 'https://api.urbandictionary.com/v0/'

class UrbanDictionaryCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def create_embed(definitions, ctx):
        def check_reaction(reaction, user):
            return (str(reaction.emoji) == NEXT_DEFINITION
            and reaction.message.id == message.id
            and user.id != bot.user.id)

        counter = 0
        display = True
        message = None

        while display:

            definition = definitions[counter][DEFINTION]
            example = definitions[counter][EXAMPLE]
            word = definitions[counter]['word']

            embed = discord.Embed(title="Defining...", color=EMBED_COLOUR)

            embed.add_field(name='Word', value= word)
            embed.add_field(name="Definition", value= definition)
            embed.add_field(name='Example', value= example)

            if message is None:
                message = await ctx.send(embed=embed)
                # add emoji to message
                await message.add_reaction(NEXT_DEFINITION)
            else:
                await message.edit(embed=embed)
            
            try:
                reaction, user = await bot.wait_for(
                    'reaction_add', check=check_reaction, timeout=60.0)
                counter = (counter + 1) % len(definitions)
            except asyncio.TimeoutError:
                await message.delete()
                break
            await reaction.remove(user)

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

        await ctx.send(self.create_embed(definitions_list, ctx))

    # Help command
    @commands.command(name='help')
    async def bot_help(self, ctx, *, query=None):
        await ctx.send("Type in $ud<word> to define a word or $ud to search a random word")


def setup(bot):
    bot.add_cog(UrbanDictionaryCog(bot))

