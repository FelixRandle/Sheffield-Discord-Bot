from orator import Model


class BaseModel(Model):

    __fillable__ = ['*']
    __timestamps__ = False
