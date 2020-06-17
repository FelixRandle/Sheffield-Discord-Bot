from orator import Model
from orator.orm import belongs_to, has_many

from .user import User


class Poll(Model):

    @belongs_to('creatorId')
    def creator(self):
        return User
