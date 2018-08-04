# this python file is for parsing the data from two directories positive and negetive
import os

#Load the file from path with two different subdirectories, positive and negative for evaluation
def ParseDirectory(path):
    '''

    :param path: the path of the evaluation files
    :return: dictionary with positive and negative as the key for positive and negative records
    '''
    TotalData = {}
    Positive = {}
    Negative = {}

    print "-------------------POSITIVE----------------------"
    # path for negative samples
    pathNegative = os.path.join(path, "negative")
    for filename in os.listdir(pathNegative):
        print filename
        filePath = os.path.join(pathNegative, filename)
        f = open(filePath, 'r')
        Negative[filename] = f.read()
        f.close()

    print "-------------------NEGATIVE----------------------"
    pathPositive = os.path.join(path, "positive")
    # path for positive samples
    for filename in os.listdir(pathPositive):
        print filename
        filePath = os.path.join(pathPositive, filename)
        f = open(filePath, 'r')
        Positive[filename] = f.read()
        f.close()

    TotalData['Positive'] = Positive
    TotalData['Negative'] = Negative
    return TotalData