from orator import Model
from orator.orm import belongs_to


class Message(Model):

    @belongs_to('author_id')
    def author(self):
        from .user import User
        return User
