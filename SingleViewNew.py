from flask import Flask, render_template, session, redirect, url_for
from src.warehouse import *
from src.ehrParser import *
from src.similarities import *
from src.evaluation import *
from pykafka import KafkaClient
import pymongo
import time
from datetime import datetime

'''

app = Flask(__name__)

mongodbURI = 'mongodb://localhost/local'
mongoClient = pymongo.MongoClient(mongodbURI)

kafkaClient = KafkaClient(hosts="127.0.0.1:9092")

zkclientAdr = '127.0.0.1:2181'



sourceDB1 = SourceDb.register(name='sourcedb1',kafkaclient=kafkaClient,mongodclient=mongoClient,zkclient=zkclientAdr)
sourceDB2 = SourceDb.register(name='sourcedb2',kafkaclient=kafkaClient,mongodclient=mongoClient,zkclient=zkclientAdr)
singleViewDB = SingleViewDb.register(name='singleviewDb',kafkaclient=kafkaClient,mongodclient=mongoClient,zkclient=zkclientAdr)
#searchCache =

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
    #sourceDB2.initial_load()

    #singleViewDB.set_up_topics(topics=['sourcedb1', 'sourcedb2'])
    #singleViewDB.create_consumer_manager()
    #print '*****************'
    #time.sleep(5)
    #sourceDB1.initial_load()
    #a = sourceDB1.local_query({"bb":33})
    '''
    for i in a:
        print "7777777777777"
        print i
        
    '''

    totalData = ParseDirectory("/Users/danieldai/Desktop/med")
    print len(totalData)

    simvalue = SimilaritiesCauculation(dataDict=totalData, calcuMethod=newTFIDF)
    #simvalue = SimilaritiesCauculation(dataDict=totalData, calcuMethod=traditionalTFIDF)
    print simvalue
    calculateErrorRate(simvalue)
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

