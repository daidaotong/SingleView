from flask import Flask, render_template, session, redirect, url_for
from src.warehouse import *
from pykafka import KafkaClient
import pymongo

app = Flask(__name__)

mongodbURI = 'mongodb://localhost/local'
mongoClient = pymongo.MongoClient(mongodbURI)

kafkaClient = KafkaClient(hosts="127.0.0.1:9092")



sourceDB1 = SourceDb.register(name='sourcedb1',kafkaclient=kafkaClient,mongodclient=mongoClient)
sourceDB2 = SourceDb(name='sourcedb2',kafkaclient=kafkaClient,mongodclient=mongoClient)
singleViewDB = SingleViewDb(name='singleviewDb',kafkaclient=kafkaClient,mongodclient=mongoClient)
#searchCache =

@app.route('/test')
def test():
    sourceDB1.initial_load()
    return 'Hello World!'




@app.route('/')
def index():
    return 'Hello World!'


if __name__ == '__main__':
    app.run(debug=True)
