#import six.moves
from six.moves import urllib_parse
#print six.__file__
#from src.evaluation import *
from pykafka import KafkaClient
from flask import Flask, render_template, session, redirect, url_for,request,abort
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

    deltaType = SelectField("Delta Type :", choices=[("0", "Insert"),("1", "Delete"),("2", "Update")], coerce=int)

    submit = SubmitField('Delta Change')

class Query(FlaskForm):

    queryField = StringField("Query Field:", [validators.required(), validators.length(max=10)])
    similarityLevel = StringField("Similarity Level:", [validators.length(max=10)])
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
            session['sourcename'] = str(request.form["sourceName"])
        return redirect(url_for('table'))
    return render_template('CoolAdmin/clientlogin.html',addrSourceForm=addrSourceForm)

@app.route('/delta',methods=['POST', 'GET'])
def delta():
    if not session.get('sourcename',None):
        abort(404)
    deltaForm = Deltaload()

    sourcedbName = session["sourcename"]

    if SourceDBs.has_key(sourcedbName):

        if deltaForm.submit.data:

            if str(request.form["deltaType"]) == "0":

                try:

                    insertFields = json.loads(str(request.form["insertField"]))

                    SourceDBs[sourcedbName].delta_load('insert', record=insertFields, query='',
                                                                          update='')

                except Exception as e:
                    print 'Invalid Input for delta insert'
                    print e


            elif str(request.form["deltaType"]) == "1":

                try:

                    queryFields = json.loads(str(request.form["queryField"]))

                    SourceDBs[sourcedbName].delta_load('delete', record='', query=queryFields,
                                                                          update='')

                except Exception as e:
                    print 'Invalid Input for delta delete'
                    print e



            elif str(request.form["deltaType"]) == "2":

                try:

                    queryFields = json.loads(str(request.form["queryField"]))
                    updateFields = json.loads(str(request.form["updateField"]))

                    SourceDBs[sourcedbName].delta_load('update', record='', query=queryFields,
                                                                          update=updateFields)

                except Exception as e:
                    print 'Invalid Input for delta insert'
                    print e


            else:
                print "query type not recognized"

    return render_template('CoolAdmin/clientDelta.html',deltaForm = deltaForm)


@app.route('/table',methods=['POST', 'GET'])
def table():
    queryResults = []
    if not session.get('sourcename',None):
        abort(404)

    query = Query()

    sourcedbName = session["sourcename"]

    if SourceDBs.has_key(sourcedbName):

        if query.submit.data:

            if str(request.form["queryType"]) == "1":

                try:

                    queryFields = json.loads(str(request.form["queryField"]))

                    queryResults.extend(
                        SourceDBs[sourcedbName].singleview_query("query", queryFields, 10000,0.0))

                except Exception as e:
                    print 'Invalid Input for query'
                    print e


            elif str(request.form["queryType"]) == "2":

                try:

                    simLevel = float(str(request.form["similarityLevel"]))
                    queryFields = json.loads(str(request.form["queryField"]))

                    queryResults.extend(
                        SourceDBs[sourcedbName].singleview_query("similarityquery", queryFields, 10000,simLevel))

                except Exception as e:
                    print 'Invalid Input for similarity query'
                    print e


            elif str(request.form["queryType"]) == "0":
                print "hhhshdhdd"

                try:

                    queryFields = json.loads(str(request.form["queryField"]))

                    queryResults.extend(SourceDBs[sourcedbName].local_query_wrapper(queryFields))

                except Exception as e:
                    print 'Invalid Input for local query'
                    print e

            else:
                print "query type not recognized"

    print queryResults
    print SourceDBs[sourcedbName]
    prescriptionTypes = {}
    if queryResults:
        for record in queryResults:
            if prescriptionTypes.has_key(record.get(SourceDBs[sourcedbName].TagName)):
                prescriptionTypes[record.get(SourceDBs[sourcedbName].TagName)].append(record)
            else:
                prescriptionTypes[record.get(SourceDBs[sourcedbName].TagName)] = list()
                prescriptionTypes[record.get(SourceDBs[sourcedbName].TagName)].append(record)


    return render_template('CoolAdmin/tableclient.html', queryform=query,queryresults = queryResults,prescriptionTypes = prescriptionTypes)



    '''
    #recordsInfo = get_Info()
    print request.form
    #return render_template('sourcePage.html',addrSourceForm = addrSourceForm,initialLoad = initialLoad,deltaLoad = deltaLoad,query = query,refreash = refreash,queryresults = queryResults,info = recordsInfo)
    return render_template('CoolAdmin/clientDelta.html', addrSourceForm=addrSourceForm, initialLoad=initialLoad,deltaLoad=deltaLoad, query=query, refreash=refreash, queryresults=queryResults,info=recordsInfo)
    '''


if __name__ == '__main__':
    app.run(debug=True,port=5002)
    #sourceDB1.initial_load()


    #singleViewDB.set_searchingcache()

