from interfaces import *

class SingleViewDb(ApplicationWarehouseABC):
    def __init__(self, name=None, **kwargs):
        super(SingleViewDb,self).__init__(name,**kwargs)
        self.Databasetype = 1

    @classmethod
    def register(cls, kafkaclient, mongodclient, *args, **kwargs):
        return super(SingleViewDb,cls).register(kafkaclient,mongodclient,*args, **kwargs)


class SourceDb(ApplicationWarehouseABC):
    def __init__(self, name=None, **kwargs):
        super(SourceDb,self).__init__(name,**kwargs)
        self.Databasetype = 0

    @classmethod
    def register(cls, kafkaclient, mongodclient, *args, **kwargs):
        return super(SourceDb,cls).register(kafkaclient,mongodclient,*args, **kwargs)
