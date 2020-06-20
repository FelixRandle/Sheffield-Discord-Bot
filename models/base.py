from orator import Model


class BaseModel(Model):

    __unguarded__ = True
    __timestamps__ = False
