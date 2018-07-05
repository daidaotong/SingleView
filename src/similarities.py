from interfaces import *
import numpy as np
from gensim import corpora,models, similarities,matutils,utils
from six import iteritems
from stopwords import get_stopwords
from editdistance import *
import re


def precompute_custom_idfs(wglobal, dfs, total_docs):
        return {termid: wglobal(df, total_docs) for termid, df in iteritems(dfs)}

def calculateCustomidf():
        pass

# rewrite the tfidf function,return exactly same format as the gensim package
def df2idf(docfreq, totaldocs, log_base=2.0, add=0.0):
        return add + np.log(float(totaldocs) / docfreq) / np.log(log_base)


# supposed to pass in unique prescription Types
def calculatePresTypeDistanceMatrix(presList):

        nameListLength = len(presList)
        nameDistanceList = [[0 for _ in range(nameListLength)] for _ in range(nameListLength)]
        print nameDistanceList
        for i in range(nameListLength):
                firstPrescription = presList[i]
                for j in range(i + 1, nameListLength):
                        secondPrescription = presList[j]
                        levensteinValue = eval(firstPrescription, secondPrescription)

                        nameDistanceList[i][j] = levensteinValue
                        nameDistanceList[j][i] = levensteinValue

        return nameDistanceList




class newTfidfModel(models.TfidfModel):
        def __init__(self,corpus=None,id2word=None, dictionary=None, wlocal=utils.identity,
                 wglobal=models.tfidfmodel.df2idf, normalize=True, smartirs=None,usingcustom = False):

                self.usingCustom = usingcustom
                self.presTypes = []
                self.textCorpus = []
                self.wholeCorpus = corpus
                for i in corpus:
                        if i[0] not in self.presTypes:
                                self.presTypes.append(i[0])
                        self.textCorpus.append(i[1])

                self.presType2Id = {}
                self.id2PresType = {}
                self.setPresTypeIdAndRev()
                self.presTypeMat = calculatePresTypeDistanceMatrix(self.presTypes)

                super(newTfidfModel,self).__init__(self.textCorpus,id2word,dictionary, wlocal,wglobal, normalize, smartirs)
                #self.customDfs =
                #self.customIdfs = precompute_custom_idfs(wglobal,self.customDfs,self.num_docs)
                self.idfMat = self.setCustomIdfMat()

        def setPresTypeIdAndRev(self):
                for index, presType in enumerate(self.presTypes):
                        self.presType2Id[presType] = index
                        self.id2PresType[index] = presType

        def setCustomIdfMatOld(self):
                idfDict = {}
                for tup in self.wholeCorpus:
                        presType = tup[0]
                        if not idfDict.has_key(presType):
                                idfDict[presType] = {}
                        for temid, _ in tup[1]:
                                if not idfDict[presType].has_key(temid):
                                        dfval = 0
                                        maxDist = max(self.presTypeMat[self.presType2Id[presType]])
                                        for tup2 in self.wholeCorpus:
                                                for temid2,_ in tup2[1]:
                                                        if temid2 == temid:
                                                                '''
                                                                print "match"
                                                                print temid2
                                                                print self.presTypeMat[self.presType2Id[presType]][self.presType2Id[tup2[0]]]
                                                                print maxDist
                                                                print float(self.presTypeMat[self.presType2Id[presType]][self.presType2Id[tup2[0]]])/float(maxDist)
                                                                print "77777"
                                                                '''
                                                                dfval+=float(self.presTypeMat[self.presType2Id[presType]][self.presType2Id[tup2[0]]])/float(maxDist)
                                                                break
                                        idfs = df2idf(dfval + 1, len(self.wholeCorpus) + 1)
                                        idfDict[presType][temid] = idfs

                return idfDict

        def setCustomIdfMat(self):
                newIdfDict = {}
                for tup in self.wholeCorpus:
                        presType = tup[0]
                        if not newIdfDict.has_key(presType):
                                newIdfDict[presType] = {}
                        for temid, _ in tup[1]:
                                newIdfDict[presType][temid] = newIdfDict[presType].get(temid,0)+1

                weightedIdfDict={}
                for k1,v1 in newIdfDict.items():
                        presType1 = k1
                        maxDist = max(self.presTypeMat[self.presType2Id[presType1]])
                        weightedIdfDict[presType1] = {}
                        for temid,_ in v1.items():
                                dfval = 0
                                for k2,v2 in newIdfDict.items():
                                        presType2 = k2
                                        if not presType1 == presType2 and v2.has_key(temid):
                                                dfval += float(self.presTypeMat[self.presType2Id[presType1]][self.presType2Id[presType2]])*v2[temid] / float(maxDist)
                                idfs = df2idf(dfval + 1, len(self.wholeCorpus) + 1)
                                if presType1 == 'dental_painful' and temid == 10:
                                        print ">>>>>>>>>>>>>>"
                                        print idfs
                                        print dfval
                                        print ">>>>>>>>>>>>>>"
                                weightedIdfDict[presType1][temid] = idfs


                return weightedIdfDict




        def __getitem__(self, presTypeWithbow, eps=1e-12):

                if not presTypeWithbow:
                    return None
                if self.usingCustom:
                        if not isinstance(presTypeWithbow[1], list):
                                return self._apply(presTypeWithbow)
                        presType = presTypeWithbow[0]
                        bow = presTypeWithbow[1]
                        self.eps = eps
                        # if the input vector is in fact a corpus, return a transformed corpus as a result
                        #not support corpus for now
                        '''
                        is_corpus, bow = gensim.utils.is_corpus(bow)
                        if is_corpus:
                                return self._apply(bow)

                        '''
                        # unknown (new) terms will be given zero weight (NOT infinity/huge weight,
                        # as strict application of the IDF formula would dictate)


                        termid_array, tf_array = [], []
                        for termid, tf in bow:
                                termid_array.append(termid)
                                tf_array.append(tf)

                        tf_array = self.wlocal(np.array(tf_array))

                        print presType
                        print self.idfMat.get(presType).get(termid,0.0)
                        vector = [
                                (termid, tf * self.idfMat.get(presType).get(termid))
                                for termid, tf in zip(termid_array, tf_array) if
                                abs(self.idfMat.get(presType,{}).get(termid,0.0)) > self.eps
                        ]

                        if self.normalize is True:
                                self.normalize = matutils.unitvec
                        elif self.normalize is False:
                                self.normalize = utils.identity

                        vector = self.normalize(vector)
                        vector = [(termid, weight) for termid, weight in vector if abs(weight) > eps]
                        return vector

                else:
                        '''
                        is_corpus, bow = utils.is_corpus(bow)
                        if is_corpus:
                                return self._apply(bow)
                        '''
                        if isinstance(presTypeWithbow[1],list):
                                return super(newTfidfModel, self).__getitem__(presTypeWithbow[1], eps=1e-12)
                        else:
                                return self._apply(presTypeWithbow)





class SimilarityCache(SearchCacheABC):
    def __init__(self, name=None, level=None, **kwargs):
        super(SimilarityCache,self).__init__(**kwargs)
        self.name = name
        self.confdLevel = level
        self.docuCommonWords = ['principal','discharge', 'diagnosis', 'responsible', 'after', 'study', 'causing', 'admission','same','other','record','orders','end','conditions',
                   'infections','complications','diet','service','admission','date','limited','need','felt','month','day','years','service','full','code','status',
                   'medications','entered','order','summary','will','none','summary:','home','year','~','liter','status:','know','?']

        self.stop_words = get_stopwords('en')
    @classmethod
    def initSearchCache(cls,confdLevel = 5, *args, **kwargs):

        s = cls(*args, **kwargs)
        #s._content = content
        s._confdLevel = confdLevel

        return s


    def hasNumbers(self,inputString):
        return any(char.isdigit() for char in inputString)

    # regex
    def hasSpecialCharacters(self,inputString):
        return bool(re.search(".*[*:;.@].*", inputString))

    def hasCommonWords(self,inputString):
        return True if inputString in self.stop_words or inputString in self.docuCommonWords else False

    def filterPattern(self,inputString):
        return self.hasNumbers(inputString) or self.hasSpecialCharacters(inputString)


    # rewrite the tfidf function,return exactly same format as the gensim package
    def df2idf(self,docfreq, totaldocs, log_base=2.0, add=0.0):
        return add + np.log(float(totaldocs) / docfreq) / np.log(log_base)


    def calTfIdf(self,corpus = None, traditional = True):
        if not corpus:
            raise AttributeError("corpus cannot be empty")
        if traditional:
            tfidf_model = models.TfidfModel([i[1] for i in corpus])
            return tfidf_model
        #TODO: calculate the custom tf-idf

    #input as tuple with 1.prestype, 2,document content 3. key Id
    def loadData(self,documents,numTopics = 5):
        print "hahahha"
        print documents
        corpus = [(document[0],[word for word in utils.simple_preprocess(str(document[1]), deacc=True) if
                   not self.hasCommonWords(word)])
                 for document in documents]

        print corpus
        self.documentIds = [document[2] for document in documents]

        self.dictionary = corpora.Dictionary([i[1] for i in corpus])

        #print(dictionary.token2id)
        bow_corpus = [(text[0],self.dictionary.doc2bow(text[1])) for text in corpus]

        #TODO:calculate ans save the tfidf model
        self.tfidf_model = newTfidfModel(bow_corpus)

        print self.tfidf_model

        #TODO: calculate and save the lda model
        self.lda = models.LdaModel(self.tfidf_model[bow_corpus], id2word=self.dictionary, num_topics=numTopics)

        #index = similarities.MatrixSimilarity(lda[tfidf_model[bow_corpus]])


    #return the
    def getSimilarRecordWithThreshold(self,threshold = 0.75,localQueries = None,rawResult = None,sourceType = None):


        print ")))))))))))))))))))"
        print localQueries
        print rawResult
        print sourceType
        print ")))))))))))))))))))"
        if not localQueries or not rawResult or not sourceType:
            print "requiredField is empty"
            return []

        filteredList = [False for _ in rawResult]

        processedResult = [(document[0],[word for word in utils.simple_preprocess(str(document[1]), deacc=True) if
                   not self.hasCommonWords(word)])
                 for document in rawResult]

        bowProcessedResult = [(text[0], self.dictionary.doc2bow(text[1])) for text in processedResult]

        index = similarities.MatrixSimilarity(self.lda[self.tfidf_model[bowProcessedResult]])

        for locquery in localQueries:
            processedLocalQuery = (sourceType, [word for word in utils.simple_preprocess(str(locquery), deacc=True) if
                                              not self.hasCommonWords(word)])

            bowProcessedLocalQuery = (sourceType,self.dictionary.doc2bow(processedLocalQuery[1]))

            for ind,j in enumerate(index[self.lda[self.tfidf_model[bowProcessedLocalQuery]]]):

                if j >=threshold:
                    filteredList[ind] = True

            print 'simmilarrrrrrrrr'
            print index[self.lda[self.tfidf_model[bowProcessedLocalQuery]]]
            print filteredList
            print 'simmilarrrrrrrrr'
        return filteredList
