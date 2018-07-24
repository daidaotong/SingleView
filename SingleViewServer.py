#import six.moves
from six.moves import urllib_parse
#print six.__file__
#from src.evaluation import *
from pykafka import KafkaClient
from flask import Flask, render_template, session, redirect, url_for,request
from src.warehouse import *
from src.ehrParser import *
from src.similarities import *
import pymongo
import time
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,PasswordField,validators




app = Flask(__name__)
app.config['SECRET_KEY'] = 'Iwasbornfortheparty'


mongodbURI = 'mongodb://localhost/local'
mongoClient = pymongo.MongoClient(mongodbURI)

kafkaClient = KafkaClient(hosts="127.0.0.1:9092")

zkclientAdr = '127.0.0.1:2181'

#TODO:Lock
SingleviewDB = None

#SingleviewDB = SingleViewDb.register(name='singleviewDb',kafkaclient=kafkaClient,mongodclient=mongoClient,zkclient=zkclientAdr)
#singleViewDB.set_up_topics(topics=['sourcedb1', 'sourcedb2'])
#SingleviewDB.register_source("sourcedb1","dental_pain")
#SingleviewDB.set_up_field_name(["user","account","name"],"dental_pain")


prescriptionTypes = {}
'''
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
    #singleViewDB.set_up_topics(topics = ['sourcedb1','sourcedb2'])
    return 'Hello World!'


class SetSingleViewForm(FlaskForm):
    singleViewName = StringField("Single View Name:",[validators.required(), validators.length(max=10)])
    #similarityLevel = StringField("Similarity Level:",[validators.required()])
    databaseName = StringField("Database Name:",[validators.required(), validators.length(max=10)])

    submit = SubmitField('SubmitSingleView')

class RegisterSourceForm(FlaskForm):
    sourceName = StringField("Source Name:",[validators.required(), validators.length(max=10)])
    fieldName = StringField("Field Name:",[validators.required()])
    presType = StringField("PresType Name:",[validators.required(), validators.length(max=10)])

    submit = SubmitField('SubmitRegisterSource')

class Initialize(FlaskForm):

    submit = SubmitField('Initialize')

class Refreash(FlaskForm):

    submit = SubmitField('Refreash')

class SetSimilarityCache(FlaskForm):

    submit = SubmitField('SetSimilarityCache')


@app.route('/',methods=['POST', 'GET'])
def index():
    global SingleviewDB
    global prescriptionTypes
    returnInfo = dict()
    singleViewForm = SetSingleViewForm()
    registerSourceForm = RegisterSourceForm()
    initialize = Initialize()
    refreash = Refreash()
    setSimilarityCache = SetSimilarityCache()
    if request.method == 'POST':
        print request.form
        if request.form["submit"] == "SubmitSingleView":


            SingleviewDB = SingleViewDb.register(name=request.form['singleViewName'], kafkaclient=kafkaClient, mongodclient=mongoClient,
                                                 zkclient=zkclientAdr)


        elif request.form["submit"] == "SubmitRegisterSource":

            fieldNames = map(str,request.form["fieldName"].split(":"))
            print fieldNames
            SingleviewDB.register_source(str(request.form["sourceName"]), str(request.form["presType"]))
            SingleviewDB.set_up_field_name(fieldNames, str(request.form["presType"]))

        elif request.form["submit"] == "Initialize":

            SingleviewDB.create_consumer_manager()
            SingleviewDB.calculate_field_levdistance()

        elif request.form["submit"] == "Refreash":
            recordIte  = SingleviewDB.db_repo.find()
            prescriptionTypes = {}
            for record in recordIte:
                if prescriptionTypes.has_key(record[SingleviewDB.presciptionTypeName]):
                    prescriptionTypes[record[SingleviewDB.presciptionTypeName]].append(record)
                else:
                    prescriptionTypes[record[SingleviewDB.presciptionTypeName]] = list()
                    prescriptionTypes[record[SingleviewDB.presciptionTypeName]].append(record)

        elif request.form["submit"] == "SetSimilarityCache":

            SingleviewDB.set_searchingcache()




    else:

        if not SingleviewDB:
            print "1111"
        else:
            print "2222"


    if SingleviewDB:
        returnInfo = SingleviewDB.return_Info()
    #return render_template('singleviewLDA.html', singleviewform=singleViewForm, registersourceForm=registerSourceForm, initialize = initialize,refreash = refreash,setSimilarityCache = setSimilarityCache,prescriptionTypes = prescriptionTypes,infoDict=returnInfo)
    return render_template('CoolAdmin/table.html', singleviewform=singleViewForm, registersourceForm=registerSourceForm,
                           initialize=initialize, refreash=refreash, setSimilarityCache=setSimilarityCache,
                           prescriptionTypes=prescriptionTypes, infoDict=returnInfo)


if __name__ == '__main__':
    app.run(debug=True,port=5001)
    #sourceDB1.initial_load()


    #singleViewDB.set_searchingcache()

