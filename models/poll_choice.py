from orator import Model
from orator.orm import belongs_to

from .poll import Poll


class PollChoice(Model):

    @belongs_to('poll')
    def poll(self):
        return Poll
