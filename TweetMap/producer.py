from kafka import KafkaProducer
from kafka.errors import KafkaError
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import time
import sys, json
reload(sys)
sys.setdefaultencoding('UTF8')

# Twitter Information
API_KEY = "1DkaP9rLh5FKWF4qYLlo6oUGh"
API_SECRET = "NwJIT3QfLerHGIaW9Xvgs5YQuicEuBOgspybvTJZhlX1zOL1hS"
ACCESS_TOKEN = "3431454303-nQTAecbq8UbEyE8CyNLLLWy4W3EWjWF0XQpiVWx"
ACCESS_TOKEN_SECRET = "Lt7r3rpxEMeWkGRxpcNXHMbD4XLit5MLCxBkZB4z7SZ6W"

#This is a basic listener that just prints received tweets to stdout.
class StdOutListener(StreamListener):     
    
    def on_status(self, status):
    #print status._json
        if status.coordinates != None:
            print status._json
            tweet = status.text.encode('utf-8')
            coord = status.coordinates

            body = { 'tweet': tweet,
                   'location': str(coord['coordinates'][1])+","+str(coord['coordinates'][0])
                   }
            # queue.send_message(MessageBody=json.dumps(body))
            producer = KafkaProducer(bootstrap_servers=['localhost:9092'])
            
            producer.send('tweets', value=json.dumps(body))
            producer.flush()

        return True   

    def on_error(self, status):
        # print status, type(status)
        if status == 420:
            time.sleep(10)
        return True
            

def startStream():
    try:
        #This handles Twitter authetification and the connection to Twitter Streaming API
        listener = StdOutListener()
        auth = OAuthHandler(API_KEY, API_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
        stream = Stream(auth, listener)

	    #This line filter Twitter Streams to capture data by the keywords: 'python', 'javascript', 'ruby'
        filterlist = ['Trump', 'election', 'love', 'debate', 'Hillary', 'game', 'apple', 'fun', 'hashtag', 'music', 'sports', 'food']
        stream.filter(track = filterlist, languages=['en'])
        # time.sleep(10)
    except:
    	startStream()

if __name__ == '__main__':
    startStream()