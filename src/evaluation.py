import matplotlib.pyplot as plt
import math
import sklearn
import gensim
from src.similarities import *
from stopwords import get_stopwords
from gensim.models.callbacks import CoherenceMetric, DiffMetric, PerplexityMetric, ConvergenceMetric

def mapLabel(label):
    '''

    :param label: label for string 'Positive' or 'Negative'
    :return: 1 for input 'Positive' and -1 for 'Negative'
    '''
    print label
    if label == 'Positive':
        return 1
    elif label == 'Negative':
        return -1
    else:
        raise ValueError("Wrong label type!")

def recoverLabel(num):
    '''

    :param num: input 1 or -1 for positive and negative set
    :return: label for 'Positive' and 'Negative'
    '''
    if num > 0:
        return 'Positive'
    else:
        return 'Negative'

def gaussian(dist, a=1, b=0, c=0.3):
    '''

    :param dist: distance
    :param a: scaling parameter
    :param b: mean
    :param c: variance
    :return: value after gaussian flat
    '''
    return a * math.e ** (-(dist - b) ** 2 / (2 * c ** 2))

def weightedKNN(similarities,numNeighbors = 5):
    '''

    :param similarities: document similarity list
    :param numNeighbors: neighbors for count
    :return: the predicted label of this document
    '''

    labelWeight = 0
    totalWeight = 0

    if len(similarities) > numNeighbors:
        for value in similarities[1:numNeighbors+1]:
            #get the value of the tuple
            label = value[0].split('+', 1)[0]

            totalWeight = totalWeight + gaussian(1-value[1])
            labelWeight = labelWeight+ mapLabel(label)*gaussian(1-value[1])


    elif len(similarities) > 1:
        for value in similarities[1:]:
            # get the value of the tuple
            label = value[0].split('+', 1)[0]
            totalWeight = totalWeight + gaussian(1-value[1])
            labelWeight = labelWeight+ mapLabel(label)*gaussian(1-value[1])

    else:
        raise ValueError("Too little data to compute!")

    return recoverLabel(labelWeight/(totalWeight))

def splitTrainTestSet(data,testingSetPercentage = 0.2):

    '''

    :param data: dataset
    :param testingSetPercentage: the percentage of test set
    :return: splitted set of train and test
    '''
    lenData = len(data)
    trainingSetIndex = range(lenData)
    testingSetIndex = []
    numTesting = int(lenData*testingSetPercentage)
    for i in range(1,numTesting):
        randIndex = int(np.random.uniform(0, len(trainingSetIndex)))
        testingSetIndex.append(trainingSetIndex[randIndex])
        del trainingSetIndex[randIndex]

    trainingSet,testingSet = [],[]

    for i in trainingSetIndex:
        trainingSet.append(data[i])
    for i in testingSetIndex:
        testingSet.append(data[i])

    return trainingSet,testingSet



def tuneNumTopics(dataDict=dict(),numTopicsLower = 10,numTopicsUpper = 49,size = 5):
    '''

    :param dataDict: the dataset
    :param numTopicsLower: lower bound of num topics
    :param numTopicsUpper: upper bound of num topics
    :param size: jump size
    :return: u_mass and c_v topic coherence test saved as image
    '''

    if not dataDict:
        raise ValueError("Data dict must not be empty")

    _, _, _, totalDocs = getSenKeyNamelist(dataDict)

    #return a list of tuple with first key= numTopics second key = perplexity
    perplexTuple = []

    corpus = [(document[0], [word for word in gensim.utils.simple_preprocess(str(document[1]), deacc=True) if
                             word not in get_stopwords('en')])
              for document in totalDocs]

    # texts = [[word for word in document.lower().split() if word not in en_stop]
    # for document in sentencelist]

    dictionary = gensim.corpora.Dictionary([i[1] for i in corpus])
    #print(dictionary.token2id)

    # print(dictionary.token2id)
    bow_corpus = [(text[0], dictionary.doc2bow(text[1])) for text in corpus]

    trainingSet, testSet = splitTrainTestSet(bow_corpus)

    # print bow_corpus
    # TODO:calculate ans save the tfidf model
    newtfidf_model = newTfidfModel(bow_corpus, usingcustom=True)
    tradtfidf_model = newTfidfModel(bow_corpus, usingcustom=False)

    cv_coherencevalue = []
    cv_coherencevalue_new = []
    umass_coherencevalue = []
    umass_coherencevalue_new = []
    for i in range(numTopicsLower,numTopicsUpper+1,size):
        newldaModel = gensim.models.LdaModel(newtfidf_model[bow_corpus], id2word=dictionary, num_topics=i)
        tradldaModel = gensim.models.LdaModel(tradtfidf_model[bow_corpus], id2word=dictionary, num_topics=i)
        cmc_v_new = gensim.models.CoherenceModel(model=newldaModel, texts=[i[1] for i in corpus], dictionary=dictionary, coherence='c_v')
        val1 = cmc_v_new.get_coherence()
        print val1
        cv_coherencevalue_new.append(val1)

        cmc_v_trad = gensim.models.CoherenceModel(model=tradldaModel, texts=[i[1] for i in corpus], dictionary=dictionary,
                                             coherence='c_v')
        val2 = cmc_v_trad.get_coherence()
        print val2
        cv_coherencevalue.append(val2)


        cmu_mass_new = gensim.models.CoherenceModel(model=newldaModel, texts=[i[1] for i in corpus], dictionary=dictionary, coherence='u_mass')
        val3 = cmu_mass_new.get_coherence()
        print val3
        umass_coherencevalue_new.append(val3)

        cmu_mass = gensim.models.CoherenceModel(model=tradldaModel, texts=[i[1] for i in corpus], dictionary=dictionary, coherence='u_mass')
        val4 = cmu_mass.get_coherence()
        print val4
        umass_coherencevalue.append(val4)
        



    x = range(numTopicsLower, numTopicsUpper+1, size)
    f1 = plt.figure()
    plt.plot(x,cv_coherencevalue_new)
    plt.plot(x, cv_coherencevalue)
    plt.xlabel("Num Topics")
    plt.ylabel("C_V coherence score")
    plt.legend(["LDA with new TF-IDF Model","LDA with traditional TF-IDF Model"], loc='best')
    f1.savefig('fig1.png')  # save the figure to file

    f2 = plt.figure()
    plt.plot(x,umass_coherencevalue_new)
    plt.plot(x, umass_coherencevalue)
    plt.xlabel("Num Topics")
    plt.ylabel("U_Mass coherence score")
    plt.legend(["LDA with new TF-IDF Model","LDA with traditional TF-IDF Model"],loc='best')
    f2.savefig('fig2.png')  # save the figure to file




#this function comes from https://blog.csdn.net/qq_23926575/article/details/79472742
def perplexity(ldamodel, testset, dictionary, size_dictionary, num_topics):
    """calculate the perplexity of a lda-model"""
    # dictionary : {7822:'deferment', 1841:'circuitry',19202:'fabianism'...]
    print ('the info of this ldamodel: \n')
    print ('num of testset: %s; size_dictionary: %s; num of topics: %s' % (
    len(testset), size_dictionary, num_topics))
    prep = 0.0
    prob_doc_sum = 0.0
    topic_word_list = []  # store the probablity of topic-word:[(u'business', 0.010020942661849608),(u'family', 0.0088027946271537413)...]
    for topic_id in range(num_topics):
        topic_word = ldamodel.show_topic(topic_id, size_dictionary)
        dic = {}
        for word, probability in topic_word:
            dic[word] = probability
        topic_word_list.append(dic)
    doc_topics_ist = []  # store the doc-topic tuples:[(0, 0.0006211180124223594),(1, 0.0006211180124223594),...]
    for doc in testset:
        doc_topics_ist.append(ldamodel.get_document_topics(doc, minimum_probability=0))
    testset_word_num = 0
    for i in range(len(testset)):
        prob_doc = 0.0  # the probablity of the doc
        doc = testset[i]
        doc_word_num = 0  # the num of words in the doc
        for word_id, num in doc:
            prob_word = 0.0  # the probablity of the word
            doc_word_num += num
            word = dictionary[word_id]
            for topic_id in range(num_topics):
                # cal p(w) : p(w) = sumz(p(z)*p(w|z))
                prob_topic = doc_topics_ist[i][topic_id][1]
                prob_topic_word = topic_word_list[topic_id][word]
                prob_word += prob_topic * prob_topic_word
            prob_doc += math.log(prob_word)  # p(d) = sum(log(p(w)))
        prob_doc_sum += prob_doc
        testset_word_num += doc_word_num
    prep = math.exp(-prob_doc_sum / testset_word_num)  # perplexity = exp(-sum(p(d)/sum(Nd))
    print ("the perplexity of this ldamodel is : %s" % prep)
    return prep


def getSenKeyNamelist(dataDict=dict()):
         sentencelist = []
         keylist = []
         namelist = []
         totalList = []

         for key, value in dataDict.items():

             for fieldkey, fieldvalue in value.items():

                 totalList.append((fieldkey,fieldvalue))

                 sentencelist.append(fieldvalue)

                 keylist.append(key + "+" + fieldkey)

                 namelist.append(fieldkey)

         return sentencelist, keylist, namelist,totalList




#This function supposed to return the corpus with the most similar items
def SimilaritiesCauculation(dataDict=dict(), useCustomTfidfModel=False,calcuMethod = "lda", numLoops=100, numTopics=10):

    if not dataDict:
        raise ValueError("Data dict must not be empty")


    sentencelist, keylist, namelist,totalDocs = getSenKeyNamelist(dataDict)

    corpus = [(document[0],[word for word in gensim.utils.simple_preprocess(str(document[1]), deacc=True) if word not in get_stopwords('en')])
         for document in totalDocs]

    # texts = [[word for word in document.lower().split() if word not in en_stop]
    # for document in sentencelist]

    dictionary = gensim.corpora.Dictionary([i[1] for i in corpus])
    print(dictionary.token2id)

    # print(dictionary.token2id)
    bow_corpus = [(text[0], dictionary.doc2bow(text[1])) for text in corpus]

    #print bow_corpus
    # TODO:calculate ans save the tfidf model
    tfidf_model = newTfidfModel(bow_corpus,usingcustom = useCustomTfidfModel)

    print "**************"
    print tfidf_model[bow_corpus]
    print "**************"


    resultMap = {}

    for i in range(numLoops):

        topicModel = None
        if calcuMethod == "lda":
            topicModel = gensim.models.LdaModel(tfidf_model[bow_corpus], id2word=dictionary, num_topics=numTopics)

        if calcuMethod == "lsi":
            topicModel = gensim.models.LsiModel(tfidf_model[bow_corpus], id2word=dictionary, num_topics=numTopics)


        index = gensim.similarities.MatrixSimilarity(topicModel[tfidf_model[bow_corpus]])

        for idx in range(len(bow_corpus)):
            # print idx
            corpus1 = tfidf_model[bow_corpus[idx]]
            # print corpus1
            simmatrix = index[topicModel[corpus1]]
            # print list(enumerate(simmatrix))
            # sort_sims = sorted(enumerate(simmatrix), key=lambda item: item[1],reverse=True)
            result = [(keylist[tulple[0]], tulple[1]) for tulple in enumerate(simmatrix)]
            if i == 0:
                resultMap[keylist[idx]] = result
            else:
                resultMap[keylist[idx]] = map(lambda x, y: (x[0], x[1] + y[1]), resultMap[keylist[idx]], result)


    for key, value in resultMap.iteritems():
        # print key,value
        resultMap[key] = map(lambda x: (x[0], x[1] / numLoops), value)

    for key, value in resultMap.iteritems():
        resultMap[key] = sorted(value, key=lambda item: item[1], reverse=True)

    return resultMap



def calculateErrorRate(docuSimilarities,method = weightedKNN):
    correctNum = 0
    totalNum = len(docuSimilarities)
    labelList = list()
    predictList = list()
    for key, values in docuSimilarities.items():
        label = key.split('+', 1)[0]
        labelList.append(label)
        predict = method(values,5)
        predictList.append(predict)
        if label == predict:
            correctNum = correctNum + 1


    print '**********************result*************************'
    print correctNum
    print totalNum
    print '****The accuracy is: '+str(float(correctNum)/float(totalNum)) + ' ******'
    print '**********************result*************************'










