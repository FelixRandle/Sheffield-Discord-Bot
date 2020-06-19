from orator.orm import belongs_to

from .base import BaseModel


class Message(BaseModel):

    @belongs_to('author_id')
    def author(self):
        from .user import User
        return User
