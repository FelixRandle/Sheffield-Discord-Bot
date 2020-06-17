from orator import Model
from orator.orm import belongs_to

from .user import User

class Message(Model):

    __primary_key__ = 'messageId'

    @belongs_to('authorId')
    def author(self):
        return User
