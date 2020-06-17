from orator import Model
from orator.orm import has_many

from .user import User


class Guild(Model):

    @has_many
    def users(self):
        return User
