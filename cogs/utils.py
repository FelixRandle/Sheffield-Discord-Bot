"""Cog for simple utility functions for the bot."""
# In this case, discord import is not needed, in some cases it may be.
# import discord
from discord.ext import commands

import database


class UtilCog(commands.Cog):
    """Create a class that extends Cog to make our functionality in."""

    def __init__(self, bot):
        """Save our bot argument that is passed in to the class."""
        self.bot = bot

        self.db = database.Database()

    @commands.command(
        name="updateusers",
        help="Updates user list on the database")
    @commands.has_role("Admin")
    async def update_users(self, ctx):
        """
        Create a simple ping pong command.

        This command adds some help text and also required that the user
        have the Member role, this is case-sensitive.
        """
        await ctx.send("Updating user list...")
        for member in ctx.guild.members:
            self.db.add_user(member)

        await ctx.send("Added all users to database!")


def setup(bot):
    """
    Add the cog we have made to our bot.

    This function is necessary for every cog file, multiple classes in the
    same file all need adding and each file must have their own setup function.
    """
    bot.add_cog(UtilCog(bot))
