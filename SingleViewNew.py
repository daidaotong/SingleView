import matplotlib.pyplot as plt
#import six.moves
from six.moves import urllib_parse
#print six.__file__
from pykafka import KafkaClient
from flask import Flask, render_template, session, redirect, url_for
from src.warehouse import *
from src.ehrParser import *
from src.similarities import *
from src.evaluation import *
import pymongo
import time
from datetime import datetime



app = Flask(__name__)

mongodbURI = 'mongodb://localhost/local'
mongoClient = pymongo.MongoClient(mongodbURI)

kafkaClient = KafkaClient(hosts="127.0.0.1:9092")

zkclientAdr = '127.0.0.1:2181'



sourceDB1 = SourceDb.register(name='sourcedb1',kafkaclient=kafkaClient,mongodclient=mongoClient,zkclient=zkclientAdr)
sourceDB1.set_prescription_type("dental_pain")
sourceDB2 = SourceDb.register(name='sourcedb2',kafkaclient=kafkaClient,mongodclient=mongoClient,zkclient=zkclientAdr)
sourceDB2.set_prescription_type("dental_illness")
singleViewDB = SingleViewDb.register(name='singleviewDb',kafkaclient=kafkaClient,mongodclient=mongoClient,zkclient=zkclientAdr)
#singleViewDB.set_up_topics(topics=['sourcedb1', 'sourcedb2'])
singleViewDB.register_source("sourcedb1","dental_pain")
singleViewDB.set_up_field_name(["user","account","name"],"dental_pain")
singleViewDB.register_source("sourcedb2","dental_illness")
singleViewDB.set_up_field_name(["user1","accountId","usname"],"dental_illness")
singleViewDB.create_consumer_manager()
#must be called after the set_field_name function
singleViewDB.calculate_field_levdistance()
#print singleViewDB.keyMapping
#print singleViewDB.fieldLevDistance
#singleViewDB.set_searchingcache()
#searchCache =


'''
@app.route('/test')
def test():
    sourceDB1.initial_load()
    singleViewDB.set_up_topics(topics = ['sourcedb1','sourcedb2'])
    return 'Hello World!'




@app.route('/')
def index():
    return 'Hello World!'

'''

if __name__ == '__main__':
    #app.run(debug=True)
    #sourceDB1.initial_load()
    sourceDB2.initial_load()
    singleViewDB.set_searchingcache()

    #totalData = ParseDirectory("/Users/danieldai/Desktop/med")
    #print totalData
    #simvalue = SimilaritiesCauculation(dataDict=totalData)

    #print "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
    #print simvalue
    #print "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"

    #simvalue = SimilaritiesCauculation(dataDict=totalData,useCustomTfidfModel=True,calcuMethod = "lsi",numTopics=50)
    #print "^^^^^^^^^^^^^^^^^*********^^^^^^^^^^^^^^^^"
    #print simvalue
    #print "^^^^^^^^^^^^^^^**********^^^^^^^^^^^^^^^^^^"
    #calculateErrorRate(simvalue)

    #tuneNumTopics(totalData)

    #plt.show()

    #sourceDB1.delta_load('delete', record='', query={"aaa":"111"}, update='')

    print "(((((()))))))))))))"
    #print singleViewDB.calculate_field_levdistance()
    print ":::::::::::::::::::::::"
    #print sourceDB1.local_query_wrapper({"aaa":"111"})
    print ":::::::::::::::::::::::"
    #sourceDB1.singleview_query("query",{"aaa":"111"},10000)
    print ":::::::::::::::::::::::"
    #sourceDB1.singleview_query("similarityquery", {"aaa":"111"}, 10000)



    #print '*****************'
    #time.sleep(5)
    #sourceDB1.initial_load()
    #a = sourceDB1.local_query({"bb":33})
    
    
    
    '''
    #recordPointer = mongoClient.get_database()["singleview"].find()
    #print [record for record in recordPointer]
    #totalData = ParseDirectory("/Users/danieldai/Desktop/med")
    #print len(totalData)
    #print totalData

    #simvalue = SimilaritiesCauculation(dataDict=totalData, calcuMethod=newTFIDF)
    #simvalue = SimilaritiesCauculation(dataDict=totalData, calcuMethod=traditionalTFIDF)
    #print simvalue
    #calculateErrorRate(simvalue)
    #SimilaritiesCauculation(dataDict=totalData, calcuMethod=traditionalTFIDF)

    #print "ggggggggggggggggggg"
    #time.sleep(5)
    #sourceDB1.delta_load('update',record = '',query={'aa':33},update = {'aa':44})
    #time.sleep(5)
    #sourceDB1.delta_load('delete', record='', query={'bb': 33}, update='')
    #sourceDB2.initial_load()
    #time.sleep(5)
    #sourceDB1.delta_load('insert', record={'bb': 22}, query='', update='')
    time.sleep(100)

    '''