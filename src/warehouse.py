from interfaces import *
import threading
import Queue as q
import json
from similarities import *
#from pykafka import *
#from pykafka.common import OffsetType
import uuid
from copy import deepcopy
from editdistance import *
import time


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
                        receivedMessage = json.loads(message.value)
                        self.update_q.put(receivedMessage)
            except Exception,err:
                print err


    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()


class Consumer_Thread_Manager():
    def __init__(self,singleviewDb,singleviewClient,topics,zk_connect,kafkaclient,*args, **kwargs):
        self.singleviewDb = singleviewDb
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
        return s


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


    def __query_table(self,querycommand,returntopic,uuid,sourceType):

        result = self.singleviewDb.expandSearch(querycommand,fuzzyquery=True,presType=sourceType)
        self.singleviewDb.send_back_queryresult(returntopic,result,uuid)


    def __query_table_with_similarities(self,querycommand,returntopic,uuid,localquery,sourceType,simLevel):

        print "Got similarityquery command"
        print querycommand

        rawresult = self.singleviewDb.expandSearch(querycommand)

        rawresultcopy = deepcopy(rawresult)
        filteredList = self.singleviewDb.similarityCache.getSimilarRecordWithThreshold(localQueries = localquery,rawResult = self.singleviewDb.separate_prescription(rawresultcopy),sourceType = sourceType,threshold = simLevel)

        print "rtrtrtrtrrt"
        print simLevel
        print "rtrtrtrtrrt"
        self.singleviewDb.send_back_queryresult(returntopic, [val[1] for val in zip(filteredList, rawresult) if val[0]], uuid)




    def __event_queue_daemon(self):
        while not self.stoprequest.isSet():
            try:
                update_body = self.event_queue.get(True, 0.5)

                if update_body.has_key('type') and update_body.has_key('value'):

                    if update_body['type'] == 'insert':
                        insertData = json.loads(update_body['value'])
                        if insertData:
                            self.singleViewClient.insert_many(insertData)
                            print "Time To Finish Load:{0}".format(str(time.time()))

                    elif update_body['type'] == 'delete':
                        print "Got delete command"
                        self.singleViewClient.remove(json.loads(update_body['value']))
                        print "Time To Finish Delete:{0}".format(str(time.time()))
                    elif update_body['type'] == 'update':
                        print "Got update command"
                        updateBodyQuery = json.loads(json.loads(update_body['value']))
                        updateBodyUpdate = {"$set": json.loads(json.loads(update_body['value']))}
                        print "Time To Finish Update:{0}".format(str(time.time()))

                        self.singleViewClient.update(updateBodyQuery, updateBodyUpdate, upsert=False, multi=True)
                    elif update_body['type'] == 'query':
                        if update_body['returntopic'] and update_body['uuid'] and update_body['source']:
                            threading.Thread(target=self.__query_table,
                                             args=( update_body['value'],update_body['returntopic'],update_body['uuid'],update_body['source'],)).start()
                        else:
                            raise Exception('No Returning Topic or uuid in Query')

                    elif update_body['type'] == 'similarityquery':
                        if update_body['returntopic'] and update_body['uuid']  and update_body['source']:
                            threading.Thread(target=self.__query_table_with_similarities,
                                             args=(update_body['value'],update_body['returntopic'],update_body['uuid'],update_body['localquery'],update_body['source'],update_body['sim'],)).start()
                        else:
                            raise Exception('No Returning Topic or uuid or local queries in Similarity Query')



                    else:
                        raise Exception('Invalid Data format')

                else:
                    raise Exception('Invalid Data format')

            except q.Empty:
                print 'Empty Queue'
                continue

    #TODO:update the prescription type here
    def update_db_prescription_type(self):
        pass

    def cache_query(self):
        pass


    def start_event_queue_daemon(self):
        self.reteiveQueueThread = threading.Thread(target=self.__event_queue_daemon,  name="singleviewworker")
        self.reteiveQueueThread.start()

    def stop_event_queue_daemon(self):
        self.stoprequest.set()
        self.handlingPools.close()
        self.handlingPools.join()


    def add_kafka_consumer(self):
        pass

    def delete_kafka_consumer(self):
        pass



class SingleViewDb(ApplicationWarehouseABC):
    def __init__(self, name=None, **kwargs):
        super(SingleViewDb,self).__init__(name,**kwargs)
        self.Databasetype = 1
        self.presciptionTypeName = "prescription_type"
        self.field_name = {}
        self.registeredSources = 0

    @classmethod
    def register(cls, kafkaclient, mongodclient,zkclient, *args, **kwargs):
        s = cls(*args, **kwargs)
        s._set_kafka_client(kafkaclient)
        s._set_mongod_client(mongodclient)
        s.zkclient = zkclient
        s.db_repo = s.mongod_client.get_database()[s.name]
        s.init_searchingCache()
        s.prescriptionType = []
        s.topics = []
        s.sourcePresMap = {}
        #s.get_kafka_topic()
        #s.get_mongod()

        return s


    def create_consumer_manager(self):
        self.consume_manager = Consumer_Thread_Manager.create_all(singleviewDb = self,singleviewClient = self.get_mongod(),topics = self.topics,kafkaclient = self.kafka_client,zk_connect = self.zkclient)

    def set_up_topics(self,topic):
        if topic not in self.topics:
            self.topics.append(topic)

    def set_up_prescription_type(self,prescriptionType):
        if prescriptionType not in self.prescriptionType:
            self.prescriptionType.append(prescriptionType)

    def set_up_field_name(self, fieldNames, sourcedb):

        if not self.field_name.has_key(sourcedb):
            self.field_name[sourcedb] = set(fieldNames)
        else:
            self.field_name[sourcedb].update(fieldNames)

    # set value as dict: self.levdistance[fieldname1] = set(fieldname2,fieldname3) if dist of 1-2 and 2-3 less than threshold
    def calculate_field_levdistance(self, thresholdDist=3):
        fieldLevDistance = {}
        keyMapping = {}
        for sourcedb, keys in self.field_name.items():

            #fieldLevDistance[sourcedb] = {}

            for key in list(keys):

                #fieldLevDistance[sourcedb][key] = []
                fieldLevDistance[key] = []
                for sourcedb2, key2 in self.field_name.items():
                    shortestDist = 10000
                    shortestKey = ""
                    if not sourcedb == sourcedb2:
                        #map the levdistance into the list map(lambda x:)
                        for i in key2:
                            dist = eval(key, i)
                            if dist < shortestDist and dist<=thresholdDist:
                                shortestDist = dist
                                shortestKey = i
                        if shortestKey != "":
                            #fieldLevDistance[sourcedb][key].append((sourcedb2,shortestKey))
                            fieldLevDistance[key].append(shortestKey)
                            if not keyMapping.has_key(key):
                                keyMapping[shortestKey] = key
        self.fieldLevDistance = fieldLevDistance
        self.keyMapping = keyMapping


    def insert_tag(self,presType,singleRecord):
        newRecord = deepcopy(singleRecord)
        newRecord[self.presciptionTypeName] = presType
        return newRecord

    def pre_process_for_load(self,singleRecord,prestype):
        return self.remove_id(self.insert_tag(prestype,singleRecord))

    def initial_load_all(self):
        allRecords = []
        sourcedbNames = self.topics
        for sourcedbName in sourcedbNames:
            sourceRecords = self.mongod_client.get_database()[sourcedbName].find()

            processedSourceRecords = [self.pre_process_for_load(r,self.sourcePresMap[sourcedbName]) for r in sourceRecords]
            if processedSourceRecords:
                self.set_up_field_name(processedSourceRecords[0].keys(),self.sourcePresMap[sourcedbName])
            allRecords.extend(processedSourceRecords)

        self.calculate_field_levdistance()
        self.get_mongod().insert_many(allRecords)


    def init_searchingCache(self):
        if not hasattr(self, 'similarityCache'):
            self.similarityCache = SimilarityCache.initSearchCache()


    def set_up_source_prescription_mapping(self,source,presType):
        if not self.sourcePresMap.has_key(source):
            self.sourcePresMap[source] = presType

    def register_source(self,sourceName, presptionType):
        self.set_up_topics(sourceName)
        self.set_up_prescription_type(presptionType)
        self.set_up_source_prescription_mapping(sourceName,presptionType)
        self.init_searchingCache()
        self.registeredSources+=1

    def get_many_with_prescription(self):
        recordPointer = self.db_repo.find()
        returnDict = []
        for record in recordPointer:
            presType = ""
            recordid = ""
            if record.has_key(self.presciptionTypeName) and record.has_key('_id'):
                presType = record[self.presciptionTypeName]
                recordid = record['_id']
                del record[self.presciptionTypeName]
                del record['_id']
            else:
                print "Corrupted Data"
            returnDict.append((presType,record,recordid))

        return returnDict

    def separate_prescription(self,rawrecordIter):
        returnDict = []
        for record in rawrecordIter:
            presType = ""
            if record.has_key(self.presciptionTypeName):
                presType = record[self.presciptionTypeName]
                del record[self.presciptionTypeName]
            else:
                print "Corrupted Data"
            returnDict.append((presType,record))

        return returnDict

    #todo: only support first query key for now
    def expandSearch(self,querycommand,fuzzyquery = False,presType = None):
        querycommanddict = json.loads(querycommand)
        if fuzzyquery:
            if len(querycommanddict) > 1:
                print "Does not support fuzzy query for more than one keys"
                return [self.remove_id(i) for i in self.get_mongod().find(querycommanddict)]
            elif not querycommanddict:
                return [self.remove_id(i) for i in self.get_mongod().find()]
            basicResult = [self.remove_id(i) for i in self.get_mongod().find(querycommanddict)]

            #print "lolololo"
            #print basicResult
            k,v = querycommanddict.items()[0][0],querycommanddict.items()[0][1]
            if self.fieldLevDistance.has_key(k):
                for key in self.fieldLevDistance[k]:
                    #make sure mapping is  not duplicate
                    if not key == k:
                        querycommanddictCopy = querycommanddict.copy()
                        newName = key
                        del querycommanddictCopy[k]
                        querycommanddictCopy[newName] = v
                        basicResult.extend([self.remove_id(i) for i in self.get_mongod().find(querycommanddictCopy)])


            return basicResult


        else:
            return [self.remove_id(i) for i in self.get_mongod().find(querycommanddict)]


    def set_searchingcache(self):
        self.init_searchingCache()
        self.similarityCache.loadData(self.get_many_with_prescription())



    def send_back_queryresult(self,topic,val,uuidval):

        if self.kafka_client != None:

            sendingTopic = self.get_kafka_topic(str(topic))

            resultJson = json.dumps(val)
            sendingobject = sendingMessage('queryresult', resultJson).withUUID(uuidval)
            try:
                with sendingTopic.get_sync_producer() as producer:
                    producer.produce(json.dumps(sendingobject.__dict__))
            except Exception as e:
                print 'got exception in sending back query'
                print e



    #This function supposed to return all the releative Infos about the Single View
    def return_Info(self):
        returnDict = {}
        if self.name:
            returnDict["name"] = self.name
        if self.topics:
            returnDict["source"] = self.topics
        if self.prescriptionType:
            returnDict["presType"] = self.prescriptionType
            returnDict["fieldName"] = [self.field_name[i] for i in self.prescriptionType]

        return returnDict


class SourceDb(ApplicationWarehouseABC):
    def __init__(self, name=None,tagName = 'prescription_type', **kwargs):
        super(SourceDb,self).__init__(name,**kwargs)
        self.Databasetype = 0
        self.TagName = tagName

    @classmethod
    def register(cls, kafkaclient, mongodclient,zkclient, *args, **kwargs):
        s = cls(*args, **kwargs)
        s._set_kafka_client(kafkaclient)
        s._set_mongod_client(mongodclient)
        s.zkclient = zkclient
        s.db_repo = s.mongod_client.get_database()[s.name]
        #s.get_kafka_topic()
        #s.get_mongod()

        return s

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
        newRecord = deepcopy(singleRecord)
        newRecord[self.TagName] = self.presType
        return newRecord

    def pre_process_for_load(self,singleRecord):
        return self.remove_id(self.insert_tag(singleRecord))


    def get_keys(self):
        returnKeys = []
        for k,_ in self.get_one().items():
            if not k == '_id':
                returnKeys.append(k)

        returnKeys.append(self.TagName)

        return returnKeys


    def set_prescription_type(self,presType):
        self.presType = presType


    #This function supposed to return all the releative Infos about the Source System
    def return_Info(self):
        returnDict = {}
        if self.name:
            returnDict["name"] = self.name

        if self.presType:
            returnDict["presType"] = self.presType

        recordIte = self.db_repo.find()

        for record in recordIte:
            if returnDict.has_key("data"):
                returnDict["data"].append(record)
            else:
                returnDict["data"] = list()
                returnDict["data"].append(record)

        return returnDict

    def initial_load(self):

        print "Time To Start Initial Load:{0}".format(str(time.time()))
        records = self.get_many()
        #print records
        records = [self.pre_process_for_load(r) for r in records]

        recordsJson = json.dumps(records)

        sendingobject = sendingMessage('insert',recordsJson).withSource(self.presType)

        if self.kafka_client != None:
            try:
                sendingTopic = self.get_kafka_topic(self.name)
                with sendingTopic.get_sync_producer() as producer:
                    producer.produce(json.dumps(sendingobject.__dict__))
            except Exception as e:
                print 'got exception'
                print e

    def delta_load(self,type,record,query,update):

        sendingTopic = self.get_kafka_topic(self.name)


        if type == 'insert':

            print "Time To Start Delta Load Insert:{0}".format(str(time.time()))
            recordSend = self.pre_process_for_load(record)

            recordSendJson = json.dumps([recordSend])

            sendingobject = sendingMessage('insert', recordSendJson).withSource(self.presType)

            if self.kafka_client != None:

                try:
                    with sendingTopic.get_sync_producer() as producer:
                        producer.produce(json.dumps(sendingobject.__dict__))
                except Exception as e:
                    print 'got exception'
                    print e

            self.db_repo.insert_one(record)

        elif type == 'delete':

            print "Time To Start Delta Load Delete:{0}".format(str(time.time()))

            queryWithTag = self.insert_tag(query)

            queryJson = json.dumps(queryWithTag)

            sendingobject = sendingMessage('delete',queryJson).withSource(self.presType)

            if self.kafka_client != None:

                try:
                    with sendingTopic.get_sync_producer() as producer:
                        producer.produce(json.dumps(sendingobject.__dict__))
                except Exception as e:
                    print 'got exception'
                    print e
            self.db_repo.remove(query)



        elif type == 'update':

            print "Time To Start Delta Load update:{0}".format(str(time.time()))

            queryWithTag = self.insert_tag(query)

            queryJson = json.dumps(queryWithTag)

            updateJson = json.dumps(update)

            sendingobject = sendingMessage('update', {'query':queryJson,'update':updateJson}).withSource(self.presType)

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

    def local_query_wrapper(self,query):
        print "Time To Start Local Query:{0}".format(str(time.time()))
        records =  [i for i in self.db_repo.find(query)]
        print "Time To Finish Local Query:{0}".format(str(time.time()))
        return records

    def singleview_query(self,type,query,timeout,simLevel):

        print "Time To Start Singleview Query:{0} Type {1}".format(str(time.time()),type)

        sendingTopic = self.get_kafka_topic(self.name)

        querySendJson = json.dumps(query)

        sendingobject = None

        uuidval = str(uuid.uuid4())

        if type == 'query':
            #calculate the similarities of the field levenstein distance or word2vec
            sendingobject = sendingMessage('query', querySendJson).withSource(self.presType).withReturnTopic(self.name+'query').withUUID(uuidval)

        elif type == 'similarityquery':
            localQueryResult = [self.remove_id(r) for r in self.local_query(query)]
            #calculate the similarities of the field levenstein distance or word2vec
            sendingobject = sendingMessage('similarityquery', querySendJson).withSource(self.presType).withLocalQueryResults(localQueryResult).withReturnTopic(self.name+'query').withUUID(uuidval).withSimilarity(simLevel)


        if self.kafka_client != None:

            try:
                with sendingTopic.get_sync_producer() as producer:
                    producer.produce(json.dumps(sendingobject.__dict__))
            except Exception as e:
                print 'got exception'
                print e

        returntopickafka = self.get_kafka_topic(self.name+"query")
        balanced_consumer = returntopickafka.get_simple_consumer(
            #publish/subscribe mode
            consumer_group=uuidval,
            auto_commit_enable=True,
            auto_commit_interval_ms=10,
            consumer_timeout_ms = timeout,
            # auto_offset_reset=OffsetType.LATEST,
            # consumer_id='test',
            # reset_offset_on_start=True,
            # zookeeper_connect=self.zkconnect
        )

        #block for results until timeout
        returnval = None
        for message in balanced_consumer:

            if message is not None:
                # print message.offset, message.value
                # print json.loads(message.value)
                try:
                    #print '+++++++++++++'
                    #print message.offset
                    #print message.value
                    #print '+++++++++++++'
                    receivedMessage = json.loads(message.value)
                    #print uuidval
                    if receivedMessage.has_key("uuid") and receivedMessage["uuid"] == uuidval:
                        returnval = json.loads(receivedMessage["value"])
                        print "Time To Finish Singleview Query:{0} Type {1}".format(str(time.time()), type)
                        balanced_consumer.stop()
                        return returnval
                except:
                    print "Not valid json record"
                    print message.value
                    print message.offset

        print "timeout ********"
        balanced_consumer.stop()
        return returnval




