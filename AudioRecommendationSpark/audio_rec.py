import os
import os.path

from pyspark import SparkContext
from pyspark import SparkConf

#Set up spark
conf = SparkConf().setMaster("local").setAppName("AdvancedAnalytics_Ch3")
sc = SparkContext(conf=conf)


#Load Dataset
datasetPath = 's3://aws-logs-640840892516-us-east-1/audio_data/user_artist_data.txt'
artistDataPath = 's3://aws-logs-640840892516-us-east-1/audio_data/artist_data.txt'
artistAliasPath = 's3://aws-logs-640840892516-us-east-1/audio_data/artist_alias.txt'
numPartitions = 2
rawDataRDD = sc.textFile(datasetPath, numPartitions)
rawDataRDD.cache()
print "Loaded AudioScrobbler dataset with {0} points".format(rawDataRDD.count())

print rawDataRDD.map(lambda x: float(x.split()[0])).stats()
print rawDataRDD.map(lambda x: float(x.split()[1])).stats()

rawArtistRDD = sc.textFile(artistDataPath)

print '\n Data Loaded \n'

# Parse dataset and extract info
def parseId(singlePair):
    splitPair = singlePair.rsplit('\t')
    # we should have two items in the list - id and name of the artist.
    if len(splitPair) != 2:
        #print singlePair
        return []
    else:
        try:
            return [(int(splitPair[0]), splitPair[1])]
        except:
            return []

artistByID = dict(rawArtistRDD.flatMap(lambda x: parseId(x)).collect())

def parseArtistAlias(alias):
    splitPair = alias.rsplit('\t')
    # we should have two items in the list - id and name of the artist.
    if len(splitPair) != 2:
        #print singlePair
        return []
    else:
        try:
            return [(int(splitPair[0]), int(splitPair[1]))]
        except:
            return []

rawAliasRDD = sc.textFile(artistAliasPath)
artistAlias = rawAliasRDD.flatMap(lambda x: parseArtistAlias(x)).collectAsMap()
print '\n artistAlias done \n'

from pyspark.mllib import recommendation
from pyspark.mllib.recommendation import *
print '\n import done \n'

artistAliasBroadcast = sc.broadcast(artistAlias)
print '\n broadcast artistAlias done \n'

def parseArtist(x):
    userID, artistID, count = map(lambda lineItem: int(lineItem), x.split())
    finalArtistID = artistAliasBroadcast.value.get(artistID)
    if finalArtistID is None:
        finalArtistID = artistID
    return Rating(userID, finalArtistID, count)

print ' \n trainmapping start \n'
trainData = rawDataRDD.map(lambda x: parseArtist(x))
trainData.cache()
print ' \n trainmapping done \n'

# Train model
print 'Training start'
model = ALS.trainImplicit(trainData, 10, 5, 0.01)
print 'Training done'

# Example user
target = 2093760

artistByIDBroadcast = sc.broadcast(artistByID)

artistsForUser = (trainData
                  .filter(lambda observation: observation.user == target)
                  .map(lambda observation: artistByIDBroadcast.value.get(observation.product))
                  .collect())
print artistsForUser

# Example recommendadtion
recommendations = \
    map(lambda observation: artistByID.get(observation.product), model.call("recommendProducts", target, 10))

print recommendations