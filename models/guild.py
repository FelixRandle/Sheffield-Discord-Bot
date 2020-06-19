from orator.orm import has_many

from .base import BaseModel


class Guild(BaseModel):

    @has_many
    def users(self):
        from .user import User
        return User
