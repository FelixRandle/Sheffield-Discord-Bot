from orator.orm import belongs_to

from .base import BaseModel


class Voice(BaseModel):
    __table__ = 'voice'

    @belongs_to('user_id')
    def user(self):
        from .user import User
        return User

    @belongs_to('guild_id')
    def guild(self):
        from .guild import Guild
        return Guild
