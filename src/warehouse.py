from interfaces import *
import threading,Queue
import json


class ComsumerThread(threading.Thread):
    def __init__(self, update_q,balancedConsumer):
        super(ComsumerThread, self).__init__()
        self.update_q = update_q
        self.stoprequest = threading.Event()
        self.balancedConsumer = balancedConsumer

    def run(self):
        while not self.stoprequest.isSet():
            try:
                for message in self.balanced_consumer:
                    if message is not None:
                        receivedMessage = json.loads(message.value)
                        self.update_q.put(receivedMessage)
            except:
                print "OOPs"


    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()


class Consumer_Thread_Manager():
    def __init__(self,singleviewClient,topics):
        self.singleViewClient = singleviewClient
        self.event_queue = Queue.Queue()
        self.sourceDb_consumer_thread_map = dict()
        self.topics = topics

    @classmethod
    def create_all_consumers(cls):
        s=cls()
        for topic in s.topics:
            #Create all topic consumers
            pass





    def add_kafka_consumer(self):
        pass

    def delete_kafka_consumer(self):
        pass



class SingleViewDb(ApplicationWarehouseABC):
    def __init__(self, name=None, **kwargs):
        super(SingleViewDb,self).__init__(name,**kwargs)
        self.Databasetype = 1

    @classmethod
    def register(cls, kafkaclient, mongodclient, *args, **kwargs):
        return super(SingleViewDb,cls).register(kafkaclient,mongodclient,*args, **kwargs)

    def __init_consumer_thread(topic, stop):
        pass


    def create_consumer_manager(self):
        self.event_queue = Queue.Queue()






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
            try:
                sendingTopic = self.get_kafka_topic()
                print sendingTopic
                with sendingTopic.get_sync_producer() as producer:
                    producer.produce(json.dumps(records))
            except Exception as e:
                print 'got exception'
                print e



    def delta_load(self,record):

        self.insert_tag(record)

        if self.kafka_client != None:
            sendingTopic = self.get_kafka_topic()
            with sendingTopic.get_sync_producer() as producer:
                producer.produce(json.dumps(record))
