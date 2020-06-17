from orator import Model
from orator.orm import has_many


class Guild(Model):

    __primary_key__ = 'guildId'
