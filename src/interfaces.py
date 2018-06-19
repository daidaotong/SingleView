import logging

#the application warehouse class holds the ether the single view database or the individual database before merged
class ApplicationWarehouseABC(object):

    name = None
    kafka_client = None
    mongod_client = None
    delta_sending_topic = None
    #source_db = None

    def __init__(self, name=None, **kwargs):
        if name is not None:
            self.name = name
        elif not getattr(self, 'name', None):
            raise ValueError("%s must have a name" % type(self).__name__)
        self.__dict__.update(kwargs)


    @classmethod
    def register(cls, kafkaclient,mongodclient,zkclient,*args, **kwargs):

        s = cls(*args, **kwargs)
        s._set_kafka_client(kafkaclient)
        s._set_mongod_client(mongodclient)
        s.zkclient = zkclient
        s.db_repo = s.mongod_client.get_database()[s.name]
        #s.get_kafka_topic()
        #s.get_mongod()

        return s

    def _set_kafka_client(self,kafkaClient):
        self.kafka_client = kafkaClient

    def _set_mongod_client(self, mongodClient):
        self.mongod_client = mongodClient


    def get_kafka_topic(self):
        return  self.kafka_client.topics[self.name]

    def get_mongod(self):
        return self.db_repo


    def insert_one(self,record):
        self.db_repo.insert_one(record)

    def insert_many(self,records):
        self.db_repo.insert_many(records)

    def get_one(self):
        return self.db_repo.find_one()

    def get_many(self):
        recordPointer = self.db_repo.find()
        return [record for record in recordPointer]


#the search engine class holds the infos of similarity and will forward the searching into the singleview database
class SearchCacheABC(object):

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    @classmethod
    def initSearchCache(cls,confdLevel,fieldNameSimilarity,hybridSimilarity, *args, **kwargs):

        #fieldname similarity holds the
        if isinstance(fieldNameSimilarity,dict) and isinstance(hybridSimilarity,dict):
            s = cls(*args, **kwargs)
            #s._content = content
            s._fieldNameSimilarity = fieldNameSimilarity
            s._HybridSimilarity = hybridSimilarity
            s._confdLevel = confdLevel

        else:
            raise ValueError("Content must be dict")



    def resetContent(self,content):
        self._content = content

    def resetConfdLevel(self,confdLevel):
        self._confdLevel = confdLevel

    def searchCache(self,isFieldName,searchContent):
        if isFieldName:
            pass
        else:
            pass


class sendingMessage():

    def __init__(self,type,value):
        self.type = type
        self.value = value

    def withSource(self,source):
        self.source = source
