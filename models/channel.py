from orator import Model
from orator.orm import belongs_to

from .user import User


class Channel(Model):

    __primary_key__ = 'channelId'

    @belongs_to('creator')
    def creator(self):
        return User