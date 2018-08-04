from gensim import corpora, models, similarities, matutils,utils
from gensim.models import KeyedVectors
import numpy as np

#Word2vec Experiment
testString = ['PAST_MEDICAL_HISTORY','PAST_SURGICAL_HISTORY','PHYSICAL_EXAMINATION']
'''
word_vectors = KeyedVectors.load_word2vec_format('~/Downloads/GoogleNews-vectors-negative300.bin', binary=True)
#model.save("file.txt")
print word_vectors.most_similar(positive=['woman', 'king'], negative=['man'])
print "******************************************************"
print word_vectors.similarity('woman', 'man')
#print  word_vectors.most_similar(positive=['san_francisco'])
print  word_vectors.most_similar(positive=['SURGICAL'])

#word_vectors.similarity(testString[0],testString[1])

'''
a=[1,4,3,6,3,6]
print a[:-1]
#print zip(a[:-1],a[1:])
print np.random.randn(3, 2)
