
import numpy as np
from gensim import corpora,models, similarities,matutils,utils
from six import iteritems
from stopwords import get_stopwords
from editdistance import *



# rewrite the tfidf function,return exactly same format as the gensim package
def df2idf(docfreq, totaldocs, log_base=2.0, add=0.0):
    return add + np.log(float(totaldocs) / docfreq) / np.log(log_base)


def TfidfCustom(corpus, query, queryFieldNo, normalize=matutils.unitvec,weightMatrix=np.mat([])):
    termid_array, tf_array = [], []
    for termid, tf in query:
        termid_array.append(termid)
        tf_array.append(tf)

    dfs = {}
    docno = -1

    for docno, bow in enumerate(corpus):

        for termid, _ in bow:
            if termid in termid_array:
                levdistanceweight = weightMatrix[queryFieldNo, docno]
                dfs[termid] = dfs.get(termid, 0) + levdistanceweight

    # avoid devide 0
    idfs = {termid: df2idf(df + 1, docno + 1) for termid, df in iteritems(dfs)}

    vector = [
        (termid, tf * idfs.get(termid))
        for termid, tf in zip(termid_array, tf_array) if abs(idfs.get(termid, 0.0)) > 1e-12
    ]

    vector = normalize(vector)
    vector = [(termid, weight) for termid, weight in vector if abs(weight) > 1e-12]

    return vector


def CalLevensteinDistanceMatrix(nameList):

    nameListLength = len(nameList)
    levdistanceList = []
    for i in range(nameListLength):
        levdistanceListInner = []
        for j in range(nameListLength):
            levensteinValue = eval(nameList[i], nameList[j])
            levdistanceListInner.append(levensteinValue)
            levdistanceListInner = map(float, levdistanceListInner)
        levdistanceList.append(levdistanceListInner)

    levdistanceMat = np.mat(levdistanceList)

    weightForEach = levdistanceMat / np.amax(levdistanceMat, axis=0)[0]

    return weightForEach

def traditionalTFIDF(tfidf_model,bow_corpus,namelist):
    return tfidf_model[bow_corpus]



def newTFIDF(tfidf_model,bow_corpus,namelist):

    # calculate the levenstein distance of the names:
    weightForEach = CalLevensteinDistanceMatrix(namelist)

    # calculate the levenstein distance of the names:
    nameListLength = len(namelist)
    levdistanceList = []
    for i in range(nameListLength):
        levdistanceListInner = []
        for j in range(nameListLength):
            levensteinValue = eval(namelist[i], namelist[j])
            levdistanceListInner.append(levensteinValue)
            levdistanceListInner = map(float, levdistanceListInner)
        levdistanceList.append(levdistanceListInner)



    corpuslist = []
    for i, j in enumerate(bow_corpus):
        corpuslist.append(TfidfCustom(bow_corpus, j, i,weightMatrix = weightForEach))
    return corpuslist

def getSenKeyNamelist(dataDict = dict()):
    sentencelist = []
    keylist = []
    namelist = []

    for key, value in dataDict.items():

        for fieldkey, fieldvalue in value.items():
            sentencelist.append(fieldvalue)

            keylist.append(key + "+" + fieldkey)

            namelist.append(fieldkey)


    return sentencelist, keylist, namelist


def SimilaritiesCauculation(en_stop = get_stopwords('en'), dataDict = dict(),calcuMethod = traditionalTFIDF,numLoops = 100):

    if not dataDict:
        raise ValueError("Data dict must not be empty")


    sentencelist,keylist,namelist = getSenKeyNamelist(dataDict)


    texts = [[word for word in document.lower().split() if word not in en_stop]
             for document in sentencelist]

    dictionary = corpora.Dictionary(texts)
    print(dictionary.token2id)
    bow_corpus = [dictionary.doc2bow(text) for text in texts]

    # print TfidfCustom(bow_corpus,bow_corpus[0],0)
    tfidf_model = models.TfidfModel(bow_corpus)


    corpusList = calcuMethod(tfidf_model,bow_corpus,namelist)


    resultMap = {}

    for i in range(numLoops):

        lda = models.LdaModel(corpusList, id2word=dictionary, num_topics=2)
        # corpus_lda = lda[corpus_tfidf]
        index = similarities.MatrixSimilarity(lda[bow_corpus])
        # for idx,corpus1 in enumerate(bow_corpus):
        for idx in range(len(bow_corpus)):
            # print idx
            corpus1 = bow_corpus[idx]
            # print corpus1
            simmatrix = index[lda[corpus1]]
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
    # print sort_sims
    #print resultMap
    return resultMap









