#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
The Urban Dictionary cog written by Ben Ridings,
You can randomly search a word or search a specific word
"""
import asyncio
import json

import aiohttp
import discord
from discord.ext import commands

# Constants
BASEURL = 'https://api.urbandictionary.com/v0/'
NEXT_DEFINITION = '➡️'
EMBED_COLOUR = 0xcf1e25


class UrbanDictionaryCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def create_embed(self, definitions, ctx):
        def check_reaction(reaction, user):
            return (str(reaction.emoji) == NEXT_DEFINITION
                    and reaction.message.id == message.id
                    and user.id != self.bot.user.id)

        counter = 0
        display = True
        message = None

        while display:

            definition = definitions[counter]['definition']
            example = definitions[counter]['example']
            word = definitions[counter]['word']

            embed = discord.Embed(title="Defining...", color=EMBED_COLOUR)

            embed.add_field(name='Word', value=word)
            embed.add_field(name="Definition", value=definition)
            embed.add_field(name='Example', value=example)

            if message is None:
                message = await ctx.send(embed=embed)
                # add emoji to message
                await message.add_reaction(NEXT_DEFINITION)
            else:
                await message.edit(embed=embed)
            try:
                reaction, user = await self.bot.wait_for(
                    'reaction_add', check=check_reaction, timeout=60.0)
                counter = (counter + 1) % len(definitions)
            except asyncio.TimeoutError:
                await message.delete()
                break
            await reaction.remove(user)

    # Search a word the user types in
    async def search_query(self, ctx, *, querystring):
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
    @commands.command(name='ud',
                      help='use $ud <term> to search for a word.'
                      + 'You can also use $ud to search for a random word')
    async def search_dictionary(self, ctx, *, query=None):
        if query is None:
            definition_list = json.loads(
                await self.search_random_word())['list']

        else:
            # Gets the typed in query and parses it
            querystring = query
            definition_list = json.loads(
                await self.search_query(ctx, querystring))['list']

        await self.create_embed(definition_list, ctx)


def setup(bot):
    bot.add_cog(UrbanDictionaryCog(bot))
