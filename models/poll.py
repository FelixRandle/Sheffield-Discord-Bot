from orator.orm import belongs_to, has_many

from .base import BaseModel


class Poll(BaseModel):

    @belongs_to('creator_id')
    def creator(self):
        from .user import User
        return User

    @has_many('poll_id')
    def choices(self):
        from .poll_choice import PollChoice
        return PollChoice
