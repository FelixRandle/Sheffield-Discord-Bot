from orator.orm import belongs_to

from .base import BaseModel


class Role(BaseModel):

    @belongs_to('creator_by')
    def creator(self):
        from .user import User
        return User

    @belongs_to('guild_id')
    def guild(self):
        from .guild import Guild
        return Guild
