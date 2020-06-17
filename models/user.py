from orator import Model
from orator.orm import belongs_to, has_many

from .channel import Channel
from .guild import Guild

class User(Model):

    __primary_key__ = 'userId'

    @belongs_to('guildId')
    def guild(self):
        return Guild

    @has_many('creator')
    def channels(self):
        return Channel
