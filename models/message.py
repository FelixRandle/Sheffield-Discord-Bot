from orator import Model
from orator.orm import belongs_to

from .user import User


class Message(Model):

    @belongs_to('author_id')
    def author(self):
        return User
