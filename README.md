# Single View for EHR

A Simulated Program for Solving EHR System Interoperability Issue by Using MongoDB Single View and LDA Modelling

## Getting Started
### Prerequisites

1. Install Python2.7
2. Install MongoDB
3. Install Kafka-Zookeeper
4. Create topics for source table
```
explanation for step 4:

if you have sourcedb1 and sourcedb2 are used as your source EHR system table name, and singleview as single view table name,
then you need to create sourcedb1,sorucedb2,sourcedb1query,sourcedb2,sourcedb2query these four topics.
 you can simply do creating topic by using the shell command:
bin/kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 1 --partitions 1 --topic topicname by using the pre-written kafka script
```
5. preparing the source data and save it in the source tables in local database(The python script InitData.py in src folder will work as an example)
### Installing

install third-party packages of python 2.7: pykafka,pymongo,gensim,flask,flask_wtf,wtforms,numpy,editdistance and stopwords
install google chrome if needed

## Running
### Server Start:
Start the Single View Server by using 'python SingleViewServer.py' command, then open a browser for address http://127.0.0.1:5001
In the Web UI page type name for single view table,then register the source for single view for pulling the data from the sources(The source name
must be exactly the same as the sourcedb table,then you also need to input the source prescription type).
After the above steps,you can get into the main page and look at the single view with different prescription schemas.

### Client Start:
Start the Single View Client by using 'python SingleViewClient.py' command, then open a browser for address http://127.0.0.1:5002
In the Web UI page type name for source table,(The source name must be exactly the same as the sourcedb table,then you also need to input the source perscription type).

### Single View and Source Interaction:
The Source and Single View are interacted by using Apache Kafka Event Queues for source querying and changes in sources floated into the Single View.
1. Delta Load:
We can update the source table in http://127.0.0.1:5002/delta page, at the same time the changes will be loaded into the single view table, the following process is delta load.
We can verify the changes loaded into the Single View Table by using the server web page http://127.0.0.1:5001/table or mongoDB Command Line. But make sure the server has already been started.

2. Single View Querying
the following steps illustrates how to do the Single View Querying:
1. go to the main page of client after login: http://127.0.0.1:5002/table
2. Select Query type:
(1) Local Query: The query will be performed locally in source table.
(2) Single View Query: The query will be floated into Single View table but no similarity calculation will be performed
(3) Single View Similarity Query: The query will be floated into Single View table and similarity filtering will be made to filter the records, the similarity level can be set through the UI


## Versioning

1.0.1

## Authors

* **Daotong Dai**

## License

This project is licensed under the MIT License

## Acknowledgments

* Hat tip to anyone whose code was used
* Inspiration
* etc

