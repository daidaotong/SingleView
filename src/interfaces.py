import logging

#the application warehouse class holds the ether the single view database or the individual database before merged
class ApplicationWarehouseABC(object):

    name = None
    kafka_client = None
    mongod_client = None
    delta_sending_topic = None
    source_db = None

    def __init__(self, name=None, **kwargs):
        if name is not None:
            self.name = name
        elif not getattr(self, 'name', None):
            raise ValueError("%s must have a name" % type(self).__name__)
        self.__dict__.update(kwargs)


    @classmethod
    def register(cls, kafkaclient,mongodclient,*args, **kwargs):

        s = cls(*args, **kwargs)
        s._set_kafka_client(kafkaclient)
        s._set_mongod_client(mongodclient)
        s.get_kafka_topic()
        s.get_mongod()

        return s

    def _set_kafka_client(self,kafkaClient):
        self.kafka_client = kafkaClient

    def _set_mongod_client(self, mongodClient):
        self.mongod_client = mongodClient


    def get_kafka_topic(self):
        self.delta_sending_topic = self.kafka_client.topics[self.name]

    def get_mongod(self):
        self.source_db = self.mongod_client.get_database()[self.name]

    def delta_load(self,record):
        pass


    def insert_one(self,record):
        self.source_db.insert_one(record)

    def insert_many(self,records):
        self.source_db.insert_many(records)


#the search engine class holds the infos of similarity and will forward the searching into the singleview database
class SearchCacheABC(object):

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    @classmethod
    def initSearchCache(cls,confdLevel,content, *args, **kwargs):

        if isinstance(content,dict):
            s = cls(*args, **kwargs)
            s._content = content
            s._confdLevel = confdLevel

        else:
            raise ValueError("Content must be dict")



    def resetContent(self,content):
        self._content = content

    def resetConfdLevel(self,confdLevel):
        self._confdLevel = confdLevel

    def searchCache(self):
        pass




