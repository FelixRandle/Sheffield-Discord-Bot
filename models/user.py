from orator.orm import belongs_to, has_many

from .base import BaseModel


class User(BaseModel):

    def guild(self):
        from .guild import Guild
        return Guild

    @has_many('creator_id')
    def channels(self):
        from .channel import Channel
        return Channel

    @has_many('author_id')
    def messages(self):
        from .message import Message
        return Message

    @has_many('creator_id')
    def polls(self):
        from .poll import Poll
        return Poll
