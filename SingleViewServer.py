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
from wtforms import StringField,SubmitField,SelectField,validators




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

@app.route('/test')
def test():
    #singleViewDB.set_up_topics(topics = ['sourcedb1','sourcedb2'])
    return 'Hello World!'


class SetSingleViewForm(FlaskForm):
    singleViewName = StringField("Single View Name:",[validators.required(), validators.length(max=20)])
    #similarityLevel = StringField("Similarity Level:",[validators.required()])
    databaseName = StringField("Database Name:",[validators.required(), validators.length(max=20)])

    submit = SubmitField('Submit Single View')

class RegisterSourceForm(FlaskForm):
    sourceName = StringField("Source Name:",[validators.required(), validators.length(max=20)])
    fieldName = StringField("Field Name:",[validators.required()])
    presType = StringField("PresType Name:",[validators.required(), validators.length(max=30)])
    submit = SubmitField('Submit Register Source')
    submitInit = SubmitField('Initialize')

class SelectSource(FlaskForm):

    selectLg = SelectField('Sources', choices=[("0","Please select")], coerce=int)
    submit = SubmitField('Submit')
    submitSetCache = SubmitField('SetSimilarityCache')

@app.route('/',methods=['POST', 'GET'])
def login():
    global SingleviewDB
    singleViewForm = SetSingleViewForm()
    if singleViewForm.validate_on_submit():
        print request.form
        SingleviewDB = SingleViewDb.register(name=str(request.form['singleViewName']), kafkaclient=kafkaClient,
                                             mongodclient=mongoClient,
                                             zkclient=zkclientAdr)
        return redirect(url_for('addSource'))
    print request.form
    return render_template('CoolAdmin/login.html',singleviewform=singleViewForm)


@app.route('/add',methods=['POST', 'GET'])
def addSource():
    global SingleviewDB
    registerSourceForm = RegisterSourceForm()
    if registerSourceForm.validate_on_submit():

        if registerSourceForm.submit.data:
            fieldNames = map(str, request.form["fieldName"].split(":"))
            #print fieldNames
            SingleviewDB.register_source(str(request.form["sourceName"]), str(request.form["presType"]))
            SingleviewDB.set_up_field_name(fieldNames, str(request.form["presType"]))

        elif registerSourceForm.submitInit.data:
            SingleviewDB.create_consumer_manager()
            SingleviewDB.calculate_field_levdistance()
            SingleviewDB.initial_load_all()
            return redirect(url_for('index'))

    return render_template('CoolAdmin/add.html',registersourceForm=registerSourceForm)




@app.route('/main',methods=['POST', 'GET'])
def index():
    global SingleviewDB
    global prescriptionTypes
    returnInfo = dict()
    selectPresType = ""
    selectSource = SelectSource()

    if SingleviewDB:
        returnInfo = SingleviewDB.return_Info()

    if returnInfo.has_key("presType"):
        for index,infoValue in enumerate(returnInfo.get("presType")):
            selectSource.selectLg.choices.append((str(index+1),infoValue))

    recordIte = SingleviewDB.db_repo.find()
    prescriptionTypes = {}
    for record in recordIte:
        if prescriptionTypes.has_key(record[SingleviewDB.presciptionTypeName]):
            prescriptionTypes[record[SingleviewDB.presciptionTypeName]].append(record)
        else:
            prescriptionTypes[record[SingleviewDB.presciptionTypeName]] = list()
            prescriptionTypes[record[SingleviewDB.presciptionTypeName]].append(record)

    if selectSource.submit:

        if selectSource.submit.data:
            if int(request.form["selectLg"]) >= 1:
                selectPresType = returnInfo.get("presType")[int(request.form["selectLg"])-1]

        elif selectSource.submitSetCache.data:
            SingleviewDB.set_searchingcache()


    print "***********"
    print selectPresType
    print prescriptionTypes
    print prescriptionTypes.get(selectPresType)
    print "***********"


    presData = dict()
    if prescriptionTypes.get(selectPresType):
        presData = prescriptionTypes.get(selectPresType)
    print "***************&"
    print prescriptionTypes
    print returnInfo
    print "***************&"
    return render_template('CoolAdmin/table.html',selectSource = selectSource,prescriptionTypes=presData, infoDict=returnInfo)


if __name__ == '__main__':
    app.run(debug=True,port=5001)
    #sourceDB1.initial_load()


    #singleViewDB.set_searchingcache()

