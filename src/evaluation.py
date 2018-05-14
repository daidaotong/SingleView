import math

def mapLabel(label):
    print label
    if label == 'Positive':
        return 1
    elif label == 'Negative':
        return -1
    else:
        raise ValueError("Wrong label type!")

def recoverLabel(num):
    print "Uuuuuuuuuuuuuuuuuuuuu"
    print num
    print "Uuuuuuuuuuuuuuuuuuuuu"
    if num > 0:
        return 'Positive'
    else:
        return 'Negative'

def gaussian(dist, a=1, b=0, c=0.3):
    return a * math.e ** (-(dist - b) ** 2 / (2 * c ** 2))

def weightedKNN(similarities,numNeighbors = 5):

    labelWeight = 0
    numRecords = 0
    totalWeight = 0

    if len(similarities) > numNeighbors:
        numRecords = numNeighbors
        for value in similarities[1:numNeighbors+1]:
            #get the value of the tuple
            label = value[0].split('+', 1)[0]
            #totalWeight = totalWeight + 1/(value[1]+1)
            #labelWeight = labelWeight+ mapLabel(label)/(value[1]+1)

            totalWeight = totalWeight + gaussian(1-value[1])
            labelWeight = labelWeight+ mapLabel(label)*gaussian(1-value[1])


    elif len(similarities) > 1:
        numRecords = len(similarities)
        for value in similarities[1:]:
            # get the value of the tuple
            label = value[0].split('+', 1)[0]
            #totalWeight = totalWeight + 1 / (value[1] + 1)
            #labelWeight = labelWeight + mapLabel(label)/(value[1]+1)
            totalWeight = totalWeight + gaussian(1-value[1])
            labelWeight = labelWeight+ mapLabel(label)*gaussian(1-value[1])

    else:
        raise ValueError("Too little data to compute!")

    return recoverLabel(labelWeight/(totalWeight))





def calculateErrorRate(docuSimilarities,method = weightedKNN):
    correctNum = 0
    totalNum = len(docuSimilarities)
    labelList = list()
    predictList = list()
    for key, values in docuSimilarities.items():
        label = key.split('+', 1)[0]
        print 'wwwwwwwww'
        print key
        print label
        labelList.append(label)
        predict = weightedKNN(values,5)
        predictList.append(predict)
        if label == predict:
            correctNum = correctNum + 1


    print '**********************result*************************'
    print correctNum
    print totalNum
    print '****The accuracy is: '+str(correctNum/totalNum) + ' ******'
    print '**********************result*************************'









