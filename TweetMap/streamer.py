#Import the necessary methods from tweepy library
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream 
import json
import time
import boto3 
import sys
reload(sys)
sys.setdefaultencoding('UTF8')

#Variables that contains the user credentials to access Twitter API 
access_token = '700387106133319682-8QjWgmhcaS8f9lf1qDYCEHlIcqMoYul'
access_token_secret = 'KySf3eVBj78rcdeGCd5u8uP3jeECwpSiXWSyMzH3PQehk'
consumer_key = 'woKaXnZooAkQeDQ7oU2QZ6yLz'
consumer_secret = 'KbGHTktGz0C19R2KiAVU5mXT0EaHtHmYrTeDT70PKrcJtrTy0N'

# Set up queue
queueName = 'tweets'
sqs = boto3.resource('sqs')
try:
    queue = sqs.get_queue_by_name(QueueName=queueName)
except:
    queue = sqs.create_queue(QueueName=queueName, Attributes={'DelaySeconds': '0'})

#This is a basic listener that just prints received tweets to stdout.
class StdOutListener(StreamListener):

    def on_status(self, status):
	#print status._json
        if status.coordinates != None:
            print status._json
            coord = status.coordinates

            body = { 'tweet': status.text,
                   'location': str(coord['coordinates'][1])+","+str(coord['coordinates'][0])
                   }
            queue.send_message(MessageBody=json.dumps(body))
            # write it out to file
            with open("tweet_data.txt", "a") as text_file:
    	    	    text_file.write(json.dumps(status._json))
    	    	    text_file.write('\n')            
        return True        

    
    def on_error(self, status):
        print status, type(status)
        if status == 420:
            time.sleep(10)
        return True
            


def startStream():
    try:
	#This handles Twitter authetification and the connection to Twitter Streaming API
	l = StdOutListener()
	auth = OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_token, access_token_secret)
	stream = Stream(auth, l)

	#This line filter Twitter Streams to capture data by the keywords: 'python', 'javascript', 'ruby'
	filterlist = ['Trump', 'election', 'love', 'debate', 'Hillary', 'game', 'apple', 'fun', 'hashtag', 'music', 'sports', 'food']
	stream.filter(track=filterlist, languages=['en'])
    except:
	startStream()


if __name__ == '__main__':
	startStream()
