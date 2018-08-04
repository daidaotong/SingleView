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


    def _set_kafka_client(self,kafkaClient):
        self.kafka_client = kafkaClient

    def _set_mongod_client(self, mongodClient):
        self.mongod_client = mongodClient


    def get_kafka_topic(self,topicName):
        return  self.kafka_client.topics[topicName]

    def remove_id(self, singleRecord):
        if singleRecord.has_key('_id'):
            del singleRecord['_id']
        return singleRecord

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
        return self

    def withFieldName(self,fieldName):
        self.fieldname = fieldName
        return self

    def withLocalQueryResults(self,localQuery):
        self.localquery = localQuery
        return self

    def withReturnTopic(self,topic):
        self.returntopic = topic
        return self

    def withUUID(self,uuid):
        self.uuid = uuid
        return self
    def withSimilarity(self,similarity):
        self.sim = similarity
        return self

