from orator import Model
from orator.orm import belongs_to, belongs_to_many

from .poll import Poll
from .user import User


class PollChoice(Model):

    @belongs_to('poll_id')
    def poll(self):
        return Poll

    @belongs_to_many('poll_responses', 'choice', 'user')
    def users(self):
        return User
