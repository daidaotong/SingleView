from interfaces import *
import threading
import Queue as q
import json
from pykafka import *
from pykafka.common import OffsetType


class ComsumerThread(threading.Thread):
    def __init__(self, update_q,balancedConsumer):
        super(ComsumerThread, self).__init__()
        self.update_q = update_q
        self.stoprequest = threading.Event()
        self.balancedConsumer = balancedConsumer

    def run(self):
        while not self.stoprequest.isSet():
            try:
                for message in self.balancedConsumer:
                    if message is not None:
                        print '+++++++++++++'
                        print message.offset
                        print message.value
                        print '+++++++++++++'
                        receivedMessage = json.loads(message.value)
                        self.update_q.put(receivedMessage)
            except Exception,err:
                #print "OOPs"
                print err


    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()


class Consumer_Thread_Manager():
    def __init__(self,singleviewClient,topics,zk_connect,kafkaclient,*args, **kwargs):
        self.singleViewClient = singleviewClient
        self.event_queue = q.Queue()
        self.sourceDb_consumer_thread_map = dict()
        self.topics = topics
        self.zkconnect = zk_connect
        self.kafkaclient = kafkaclient
        self.stoprequest = threading.Event()

    @classmethod
    def create_all(cls, *args, **kwargs):
        s = cls(*args, **kwargs)
        s.create_all_consumers()
        s.start_event_queue_daemon()


    def create_all_consumers(self):
        for topic in self.topics:
            topickafka = self.kafkaclient.topics[topic]
            balanced_consumer = topickafka.get_simple_consumer(
                consumer_group='group1',
                auto_commit_enable=True,
                auto_commit_interval_ms=10,
                #auto_offset_reset=OffsetType.LATEST,
                #consumer_id='test',
                #reset_offset_on_start=True,
                #zookeeper_connect=self.zkconnect
            )
            w = ComsumerThread(update_q=self.event_queue,balancedConsumer=balanced_consumer)
            w.start()
            self.sourceDb_consumer_thread_map[topic] = w

        print  self.sourceDb_consumer_thread_map
        print threading.active_count()



    def __event_queue_daemon(self):
        while not self.stoprequest.isSet():
            try:
                update_body = self.event_queue.get(True, 0.5)

                print "fhfhfhfhff"
                print update_body
                print "fhfhfhfhff"
                if update_body.has_key('type') and update_body.has_key('value'):
                    if update_body['type'] == 'insert':
                        print "Insert lalalallala"
                        print json.loads(update_body['value'])
                        self.singleViewClient.insert_many(json.loads(update_body['value']))
                    elif update_body['type'] == 'delete':
                        print "Got delete command"
                        print update_body['value']
                        self.singleViewClient.remove(json.loads(update_body['value']))
                    elif update_body['type'] == 'update':
                        print "Got update command"
                        print update_body['value']
                        updateBodyQuery = json.loads(update_body['value']['query'])
                        updateBodyUpdate = {"$set":json.loads(update_body['value']['update'])}

                        self.singleViewClient.update(updateBodyQuery,updateBodyUpdate,upsert = False,multi = True)
                    elif update_body['type'] == 'query':
                        print "Got query command"
                        print update_body['value']
                        #TODO: 1. insery similarity tags 2. query 3 sent back
                        self.singleViewClient.find(json.loads(update_body['value']))

                    elif update_body['type'] == 'similarityquery':
                        print "Got similarityquery command"
                        print update_body['value']
                        #TODO: insery similarity tags
                        self.singleViewClient.find(json.loads(update_body['value']))

                    else:
                        raise Exception('Invalid Data format')
                else:
                    raise Exception('Invalid Data format')

            except q.Empty:
                print 'Empty Queue'
                continue


    def start_event_queue_daemon(self):
        self.reteiveQueueThread = threading.Thread(target=self.__event_queue_daemon,  name="singleviewworker")
        self.reteiveQueueThread.start()

    def stop_event_queue_daemon(self):
        self.stoprequest.set()


    def add_kafka_consumer(self):
        pass

    def delete_kafka_consumer(self):
        pass



class SingleViewDb(ApplicationWarehouseABC):
    def __init__(self, name=None, **kwargs):
        super(SingleViewDb,self).__init__(name,**kwargs)
        self.Databasetype = 1

    @classmethod
    def register(cls, kafkaclient, mongodclient,zkclient, *args, **kwargs):
        return super(SingleViewDb,cls).register(kafkaclient,mongodclient,zkclient,*args, **kwargs)


    def create_consumer_manager(self):
        self.consume_manager = Consumer_Thread_Manager.create_all(singleviewClient = self.get_mongod(),topics = self.topics,kafkaclient = self.kafka_client,zk_connect = self.zkclient)

    def set_up_topics(self,topics):
        self.topics = topics

    def set_up_searchingCache(self):
        self.similarityCache =








class SourceDb(ApplicationWarehouseABC):
    def __init__(self, name=None,tagName = 'prescription_type', **kwargs):
        super(SourceDb,self).__init__(name,**kwargs)
        self.Databasetype = 0
        self.TagName = tagName

    @classmethod
    def register(cls, kafkaclient, mongodclient,zkclient, *args, **kwargs):
        return super(SourceDb,cls).register(kafkaclient,mongodclient,zkclient,*args, **kwargs)

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
        if singleRecord.has_key('_id'):
            del singleRecord['_id']
        return singleRecord


    def insert_query_tag(self,query):
        query[self.TagName] = self.name
        return query

    def initial_load(self):

        records = self.get_many()
        print records
        records = [self.insert_tag(r) for r in records]

        recordsJson = json.dumps(records)

        sendingobject = sendingMessage('insert',recordsJson)

        if self.kafka_client != None:
            try:
                sendingTopic = self.get_kafka_topic()
                with sendingTopic.get_sync_producer() as producer:
                    producer.produce(json.dumps(sendingobject.__dict__))
            except Exception as e:
                print 'got exception'
                print e

    def delta_load(self,type,record,query,update):

        sendingTopic = self.get_kafka_topic()


        if type == 'insert':

            recordSend = self.insert_tag(record)

            recordSendJson = json.dumps([recordSend])

            sendingobject = sendingMessage('insert', recordSendJson)

            if self.kafka_client != None:

                try:
                    with sendingTopic.get_sync_producer() as producer:
                        producer.produce(json.dumps(sendingobject.__dict__))
                except Exception as e:
                    print 'got exception'
                    print e

            self.db_repo.insert_one(record)

        elif type == 'delete':

            queryWithTag = self.insert_query_tag(query)

            queryJson = json.dumps(queryWithTag)

            sendingobject = sendingMessage('delete',queryJson)

            if self.kafka_client != None:

                try:
                    with sendingTopic.get_sync_producer() as producer:
                        producer.produce(json.dumps(sendingobject.__dict__))
                except Exception as e:
                    print 'got exception'
                    print e

            self.db_repo.remove(query)



        elif type == 'update':

            queryWithTag = self.insert_query_tag(query)

            queryJson = json.dumps(queryWithTag)

            updateJson = json.dumps(update)

            sendingobject = sendingMessage('update', {'query':queryJson,'update':updateJson})

            if self.kafka_client != None:

                try:
                    with sendingTopic.get_sync_producer() as producer:
                        producer.produce(json.dumps(sendingobject.__dict__))
                except Exception as e:
                    print 'got exception'
                    print e

            self.db_repo.update(query,update)



    def local_query(self,query):
        return self.db_repo.find(query)

    def singleview_query(self,type,query):

        sendingTopic = self.get_kafka_topic()

        querySendJson = json.dumps(query)

        sendingobject = None

        if type == 'query':
            #calculate the similarities of the field levenstein distance or word2vec
            sendingobject = sendingMessage('query', querySendJson)

        elif type == 'similarityquery':
            #calculate the similarities of the field levenstein distance or word2vec
            sendingobject = sendingMessage('similarityquery', querySendJson)


        if self.kafka_client != None:

            try:
                with sendingTopic.get_sync_producer() as producer:
                    producer.produce(json.dumps(sendingobject.__dict__))
            except Exception as e:
                print 'got exception'
                print e


