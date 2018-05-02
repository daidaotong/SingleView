
import numpy as np
from gensim import corpora,models, similarities,matutils,utils
from six import iteritems
from stopwords import get_stopwords



# rewrite the tfidf function,return exactly same format as the gensim package
def df2idf(docfreq, totaldocs, log_base=2.0, add=0.0):
    return add + np.log(float(totaldocs) / docfreq) / np.log(log_base)


def TfidfCustom(corpus, query, queryFieldNo, normalize=matutils.unitvec,weightMatrix):
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


def SimilaritiesCauculation(en_stop = get_stopwords('en'), dataDict):
    
    sentencelist = []
    keylist = []
    namelist = []
