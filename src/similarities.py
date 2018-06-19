from interfaces import *
import numpy as np
from gensim import corpora,models, similarities,matutils,utils
from six import iteritems
from stopwords import get_stopwords
from editdistance import *
import re


class SimilarityCache(SearchCacheABC):
    def __init__(self, name=None, **kwargs):
        super(self).__init__(name,**kwargs)
        self.Databasetype = 1
        self.docuCommonWords = ['principal','discharge', 'diagnosis', 'responsible', 'after', 'study', 'causing', 'admission','same','other','record','orders','end','conditions',
                   'infections','complications','diet','service','admission','date','limited','need','felt','month','day','years','service','full','code','status',
                   'medications','entered','order','summary','will','none','summary:','home','year','~','liter','status:','know','?']

        self.stop_words = get_stopwords('en')
    @classmethod
    def initSearchCache(cls,confdLevel,fieldNameSimilarity,hybridSimilarity, *args, **kwargs):
        return super(cls).initSearchCache(confdLevel,fieldNameSimilarity,hybridSimilarity, *args, **kwargs)

    def hasNumbers(self,inputString):
        return any(char.isdigit() for char in inputString)

    # regex
    def hasSpecialCharacters(self,inputString):
        return bool(re.search(".*[*:;.@].*", inputString))

    def hasCommonWords(self,inputString):
        return inputString not in self.stop_words or inputString not in self.docuCommonWords

    def filterPattern(self,inputString):
        return self.hasNumbers(inputString) or self.hasSpecialCharacters(inputString)

    # rewrite the tfidf function,return exactly same format as the gensim package
    def df2idf(self,docfreq, totaldocs, log_base=2.0, add=0.0):
        return add + np.log(float(totaldocs) / docfreq) / np.log(log_base)

    #nameDict supposed to save the key in dict as prescriptionType:name
    def setNameFieldDistance(self,nameList):

        nameListLength = len(nameList)
        nameDistanceDict = {}
        for i in range(nameListLength):
            firstPrescription, firstName = nameList[i].split(":")[0],nameList[i].split(":")[1]
            for j in range(i+1,nameListLength):
                secondPrescription, secondName = nameList[j].split(":")[0], nameList[j].split(":")[1]
                if firstPrescription == secondPrescription:
                    continue

                levensteinValue = eval(firstName, secondName)

                if not nameDistanceDict.has_key(i):
                    nameDistanceDict[i] = list()
                    nameDistanceDict[i].append((j,levensteinValue))
                else:
                    nameDistanceDict[i].append((j, levensteinValue))


                if not nameDistanceDict.has_key(j):
                    nameDistanceDict[j] = list()
                    nameDistanceDict[j].append((i,levensteinValue))
                else:
                    nameDistanceDict[j].append((i, levensteinValue))


        self.nameDistanceDict = nameDistanceDict


        return


    def TfidfCustom(self,corpus, query, queryFieldNo, normalize=matutils.unitvec, weightMatrix=np.mat([])):
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
        idfs = {termid: self.df2idf(df + 1, docno + 1) for termid, df in iteritems(dfs)}

        vector = [
            (termid, tf * idfs.get(termid))
            for termid, tf in zip(termid_array, tf_array) if abs(idfs.get(termid, 0.0)) > 1e-12
        ]

        vector = normalize(vector)
        vector = [(termid, weight) for termid, weight in vector if abs(weight) > 1e-12]

        return vector

    def CalLevensteinDistanceMatrix(self,nameList):

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

    def traditionalTFIDF(self,tfidf_model, bow_corpus, namelist):
        return tfidf_model[bow_corpus]

    def newTFIDF(self,tfidf_model, bow_corpus, namelist):

        # calculate the levenstein distance of the names:
        weightForEach = self.CalLevensteinDistanceMatrix(namelist)

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
            corpuslist.append(self.TfidfCustom(bow_corpus, j, i, weightMatrix=weightForEach))
        return corpuslist

    def getSenKeyNamelist(self,dataDict=dict()):
        sentencelist = []
        keylist = []
        namelist = []

        for key, value in dataDict.items():

            for fieldkey, fieldvalue in value.items():
                sentencelist.append(fieldvalue)

                keylist.append(key + "+" + fieldkey)

                namelist.append(fieldkey)

        return sentencelist, keylist, namelist

    def SimilaritiesCauculation(self, dataDict=dict(), calcuMethod=traditionalTFIDF,
                                numLoops=100):

        if not dataDict:
            raise ValueError("Data dict must not be empty")

        sentencelist, keylist, namelist = self.getSenKeyNamelist(dataDict)

        print '1111111111111'
        print sentencelist[0]
        print '1111111111111'

        texts = [[word for word in document.lower().split() if
                   not self.hasCommonWords(word) and not self.filterPattern(word)]
                 for document in sentencelist]

        # texts = [[word for word in document.lower().split() if word not in en_stop]
        # for document in sentencelist]

        dictionary = corpora.Dictionary(texts)
        print(dictionary.token2id)
        bow_corpus = [dictionary.doc2bow(text) for text in texts]

        # print TfidfCustom(bow_corpus,bow_corpus[0],0)
        tfidf_model = models.TfidfModel(bow_corpus)

        corpusList = calcuMethod(tfidf_model, bow_corpus, namelist)

        resultMap = {}

        for i in range(numLoops):

            lda = models.LdaModel(corpusList, id2word=dictionary, num_topics=5)
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
        # print resultMap
        return resultMap

