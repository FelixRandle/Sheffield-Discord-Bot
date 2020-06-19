from orator import Model
from orator.orm import belongs_to, has_many


class Poll(Model):

    @belongs_to('creator_id')
    def creator(self):
        from .user import User
        return User

    @has_many('poll')
    def choices(self):
        from .poll_choice import PollChoice
        return PollChoice
