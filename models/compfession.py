from orator.orm import belongs_to

from .base import BaseModel


class Compfession(BaseModel):

    __timestamps__ = True

    @belongs_to('creator_id')
    def creator(self):
        from .user import User
        return User
