from discord.ext.commands import Converter
from discord.ext.commands import BadArgument
from orator.orm import belongs_to

from .base import BaseModel


class Compfession(BaseModel, Converter):

    __timestamps__ = True

    @belongs_to('creator_id')
    def creator(self):
        from .user import User
        return User

    async def convert(self, ctx, id):
        compfession = type(self) \
            .where('approved_id', id) \
            .where('guild_id', ctx.guild.id) \
            .first()
        if compfession is None:
            raise BadArgument(f"Compfession with ID {id} was not found")
        return compfession
