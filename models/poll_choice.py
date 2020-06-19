from orator.orm import belongs_to, belongs_to_many

from .base import BaseModel


class PollChoice(BaseModel):

    @belongs_to('poll_id')
    def poll(self):
        from .poll import Poll
        return Poll

    @belongs_to_many('poll_responses', 'choice', 'user')
    def users(self):
        from .user import User
        return User
