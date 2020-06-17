from orator import Model
from orator.orm import belongs_to, has_many

from .channel import Channel
from .guild import Guild
from .message import Message
from .poll import Poll


class User(Model):

    def guild(self):
        return Guild

    @has_many('creator_id')
    def channels(self):
        return Channel

    @has_many('author_id')
    def messages(self):
        return Message

    @has_many('creator_id')
    def polls(self):
        return Poll
