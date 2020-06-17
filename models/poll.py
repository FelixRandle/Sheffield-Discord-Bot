from orator import Model
from orator.orm import belongs_to, has_many

from .user import User
from .poll_choice import PollChoice


class Poll(Model):

    @belongs_to('creatorId')
    def creator(self):
        return User

    @has_many('poll')
    def choices(self):
        return PollChoice
