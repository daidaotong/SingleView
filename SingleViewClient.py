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
#SingleviewDB = None

SourceDBs = {}

#prescriptionTypes = {}
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

class AddSourceForm(FlaskForm):
    sourceName = StringField("Source Name:",[validators.required(), validators.length(max=20)])
    presType = StringField("PresType Name:",[validators.required()])

    submit = SubmitField('SubmitCreateSource')

class InitialLoad(FlaskForm):


    sourceName = StringField("Source Name:",[validators.required(), validators.length(max=10)])
    presType = StringField("PresType Name:",[validators.required(), validators.length(max=10)])


    submit = SubmitField('InitialLoad')


class Deltaload(FlaskForm):


    insertField = StringField("Insert Field:")
    queryField = StringField("Query Field:")
    updateField = StringField("Update Field:")

    deltaType = SelectField("Delta Type :", choices=[("0", "Insert"),("1", "Delete"),("2", "Query")], coerce=int)

    submit = SubmitField('Delta Change')

class Query(FlaskForm):

    queryField = StringField("Query Field:", [validators.required(), validators.length(max=10)])
    queryType = SelectField("Query Type :", choices=[("0", "Local Query"), ("1", "Singleview Query"), ("2", "Singleview Similarity Query")], coerce=int)
    submit = SubmitField('Query')


class Refreash(FlaskForm):

    submit = SubmitField('Refreash')


def get_Info():
    global SourceDBs
    InfoList = []
    for sourceDB in SourceDBs.values():
        InfoList.append(sourceDB.return_Info())

    return InfoList

@app.route('/',methods=['POST', 'GET'])
def login():
    global SourceDBs
    addrSourceForm = AddSourceForm()
    if addrSourceForm.validate_on_submit() and addrSourceForm.submit.data:
        if not SourceDBs.has_key(str(request.form["sourceName"])):
            newSource = SourceDb.register(name=str(request.form["sourceName"]), kafkaclient=kafkaClient,
                                          mongodclient=mongoClient, zkclient=zkclientAdr)
            newSource.set_prescription_type(str(request.form["presType"]))

            SourceDBs[str(request.form["sourceName"])] = newSource

            return redirect(url_for('index'))
    return render_template('CoolAdmin/clientlogin.html',addrSourceForm=addrSourceForm)

@app.route('/delta',methods=['POST', 'GET'])
def delta():
    deltaForm = Deltaload()
    return render_template('CoolAdmin/clientDelta.html',deltaForm = deltaForm)


@app.route('/table',methods=['POST', 'GET'])
def table():
    query = Query()
    return render_template('CoolAdmin/tableclient.html', queryform=query)


@app.route('/main',methods=['POST', 'GET'])
def index():
    global SourceDBs
    #global prescriptionTypes
    queryResults = []
    addrSourceForm = AddSourceForm()
    initialLoad = InitialLoad()
    deltaLoad = Deltaload()
    query = Query()
    refreash = Refreash()
    if request.method == 'POST':
        print request.form

        if request.form["submit"] == "InitialLoad":

            if SourceDBs.has_key(str(request.form["sourceName"])):
                SourceDBs[str(request.form["sourceName"])].initial_load()

            else:
                print "Source not recognized"



        elif str(request.form["submit"]) == "Deltaload":

            if SourceDBs.has_key(str(request.form["sourceName"])):

                if str(request.form["deltaType"]) == "delete":

                    try:

                        queryFields = json.loads(str(request.form["queryField"]))

                        SourceDBs[str(request.form["sourceName"])].delta_load('delete', record='', query=queryFields,
                                                                              update='')

                    except Exception as e:
                        print 'Invalid Input for delta delete'
                        print e


                elif str(request.form["deltaType"]) == "insert":

                    try:

                        insertFields = json.loads(str(request.form["insertField"]))

                        SourceDBs[str(request.form["sourceName"])].delta_load('insert', record=insertFields, query='',
                                                                              update='')

                    except Exception as e:
                        print 'Invalid Input for delta insert'
                        print e

                elif str(request.form["deltaType"]) == "update":

                    try:

                        queryFields = json.loads(str(request.form["queryField"]))
                        updateFields = json.loads(str(request.form["updateField"]))

                        SourceDBs[str(request.form["sourceName"])].delta_load('update', record='', query=queryFields,
                                                                              update=updateFields)

                    except Exception as e:
                        print 'Invalid Input for delta insert'
                        print e

                else:
                    print "delta type not recognized"

            else:
                print "Source not recognized"


        elif request.form["submit"] == "Query":

            if SourceDBs.has_key(str(request.form["sourceName"])):

                if str(request.form["queryType"]) == "query":

                    try:

                        queryFields = json.loads(str(request.form["queryField"]))

                        queryResults.extend(SourceDBs[str(request.form["sourceName"])].singleview_query("query",queryFields,10000))

                    except Exception as e:
                        print 'Invalid Input for query'
                        print e


                elif str(request.form["queryType"]) == "similarityquery":

                    try:

                        queryFields = json.loads(str(request.form["queryField"]))

                        queryResults.extend(SourceDBs[str(request.form["sourceName"])].singleview_query("similarityquery", queryFields, 10000))

                    except Exception as e:
                        print 'Invalid Input for similarity query'
                        print e


                elif str(request.form["queryType"]) == "localquery":

                    try:

                        queryFields = json.loads(str(request.form["queryField"]))

                        queryResults.extend(SourceDBs[str(request.form["sourceName"])].local_query_wrapper(queryFields))

                    except Exception as e:
                        print 'Invalid Input for local query'
                        print e

                else:
                    print "query type not recognized"

            else:
                print "Source not recognized"


    recordsInfo = get_Info()
    print request.form
    #return render_template('sourcePage.html',addrSourceForm = addrSourceForm,initialLoad = initialLoad,deltaLoad = deltaLoad,query = query,refreash = refreash,queryresults = queryResults,info = recordsInfo)
    return render_template('CoolAdmin/clientDelta.html', addrSourceForm=addrSourceForm, initialLoad=initialLoad,deltaLoad=deltaLoad, query=query, refreash=refreash, queryresults=queryResults,info=recordsInfo)


if __name__ == '__main__':
    app.run(debug=True,port=5002)
    #sourceDB1.initial_load()


    #singleViewDB.set_searchingcache()

