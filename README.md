# Project Title

A Simulated Program for Solving EHR System Interoperability Issue by Using MongoDB Single View and LDA Modelling

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

1. Install Python2.7
2. Install MongoDB
3. Install Kafka-Zookeeper
4. create topics for single view table and source table
```
explanation for step 4:

if you have sourcedb1 and sourcedb2 as your source EHR system table, and singleview as single view table, then you need to create sourcedb1,sorucedb2,sourcedb1query,sourcedb2,sourcedb2query these four topics. you can simply do creqating topic by using the shell command:
bin/kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 1 --partitions 1 --topic topicname by using the pre-written kafka script
```
5. preparing the source data ang save it in the source database
### Installing

install third-party packages of python 2.7: pykafka,pymongo,gensim,flask,flask_wtf,wtforms,numpy,editdistance and stopwords
install google chrome if needed

## Running
Server Starts:
Start the Single View Server by using 'python SingleViewServer.py' command



Client Starts:
Start the Single View Client by using 'python SingleViewClient.py' command
### Break down into end to end tests

Explain what these tests test and why

```
Give an example
```

### And coding style tests

Explain what these tests test and why

```
Give an example
```

## Deployment

Add additional notes about how to deploy this on a live system

## Built With

* [Dropwizard](http://www.dropwizard.io/1.0.2/docs/) - The web framework used
* [Maven](https://maven.apache.org/) - Dependency Management
* [ROME](https://rometools.github.io/rome/) - Used to generate RSS Feeds

## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your/project/tags). 

## Authors

* **Billie Thompson** - *Initial work* - [PurpleBooth](https://github.com/PurpleBooth)

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Hat tip to anyone whose code was used
* Inspiration
* etc

