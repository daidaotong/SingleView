from interfaces import *
import json

class SingleViewDb(ApplicationWarehouseABC):
    def __init__(self, name=None, **kwargs):
        super(SingleViewDb,self).__init__(name,**kwargs)
        self.Databasetype = 1

    @classmethod
    def register(cls, kafkaclient, mongodclient, *args, **kwargs):
        return super(SingleViewDb,cls).register(kafkaclient,mongodclient,*args, **kwargs)



class SourceDb(ApplicationWarehouseABC):
    def __init__(self, name=None,tagName = 'prescription_type', **kwargs):
        super(SourceDb,self).__init__(name,**kwargs)
        self.Databasetype = 0
        self.TagName = tagName

    @classmethod
    def register(cls, kafkaclient, mongodclient, *args, **kwargs):
        return super(SourceDb,cls).register(kafkaclient,mongodclient,*args, **kwargs)

    def save_one(self,record):
        if self.mongod_client != None:
            self.insert_one(record)

        if self.kafka_client != None:
            self.insert_tag(record)
            self.delta_load(record)


    def save_many(self,records):
        if self.mongod_client != None:
            self.insert_many(records)

        if self.kafka_client != None:
            self.delta_load(records)

    def insert_tag(self,singleRecord):
        singleRecord[self.TagName] = self.name


    def initial_load(self):

        records = self.get_many()
        records = map(self.insert_tag,records)

        if self.kafka_client != None:
            sendingTopic = self.get_kafka_topic()
            with sendingTopic.get_sync_producer() as producer:
                producer.produce(json.dumps(records))



    def delta_load(self,record):

        self.insert_tag(record)

        if self.kafka_client != None:
            sendingTopic = self.get_kafka_topic()
            with sendingTopic.get_sync_producer() as producer:
                producer.produce(json.dumps(record))
