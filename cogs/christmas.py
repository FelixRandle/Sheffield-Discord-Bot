#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
A christmas cog to be festive and shit

Also provides a simple base for starting a new cog.
"""
from random import random

from discord.ext import commands


class ChristmasCog(commands.Cog):
    """Festive commands for the server."""

    def __init__(self, bot):
        """Save our bot argument that is passed in to the class."""
        self.bot = bot
        self.christmas_mode = False

    @commands.Cog.listener()
    async def on_message(self, message):
        if self.christmas_mode:
            await message.add_reaction(u"🎄")

    @commands.command(
        name="christmasMode",
        help="Enables christmas mode")
    @commands.has_role("Admin")
    async def toggle_christmas_mode(self, ctx):
        self.christmas_mode = not self.christmas_mode
        await ctx.send("Toggled christmas mode!")

    @commands.command(
        name="christmasTree",
        help="Produces a lovely christmas tree"
    )
    async def christmas_tree(self, ctx,
                             tree_size: int = 10,
                             bauble_probability: float = 0.2):
        """
        Creates a christmas tree and outputs it to the context's channel
        :param ctx: Context the command was sent in
        :param tree_size: Height of the tree
        :param bauble_probability: Probability of a point being a bauble
        """
        # Limit tree size to stop errors and unintended behaviour.
        tree_size = max(min(tree_size, 29), 5)

        # Generate our tree
        output = "```gherkin\n"
        line_width = 2 * tree_size
        for i in range(1, line_width, 2):
            output += ("".join(["*" if random() > bauble_probability
                                else "o" for _ in range(i)])
                       .center(line_width) + "\n")

        for _leg in range(3):
            output += ("| |".center(line_width) + "\n")

        output += ("\=====/".center(line_width) + "\n")  # noqa: W605
        output += "```"
        await ctx.send(output)


def setup(bot):
    """
    Add the cog we have made to our bot.

    This function is necessary for every cog file, multiple classes in the
    same file all need adding and each file must have their own setup function.
    """
    bot.add_cog(ChristmasCog(bot))
