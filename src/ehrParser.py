# this python file is for parsing the data from two directories positive and negetive
import os

def ParseDirectory(path):
    #PositiveData = {}
    #NegativeData = {}
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