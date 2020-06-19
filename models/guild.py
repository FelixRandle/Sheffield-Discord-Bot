from orator import Model
from orator.orm import has_many


class Guild(Model):

    @has_many
    def users(self):
        from .user import User
        return User
