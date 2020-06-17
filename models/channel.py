from orator import Model
from orator.orm import belongs_to

from .user import User


class Channel(Model):

    @belongs_to('creator_id')
    def creator(self):
        return User
