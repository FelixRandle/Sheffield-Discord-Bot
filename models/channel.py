from orator import Model
from orator.orm import belongs_to


class Channel(Model):

    @belongs_to('creator_id')
    def creator(self):
        from .user import User
        return User
