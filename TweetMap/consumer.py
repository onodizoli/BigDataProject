from kafka import KafkaConsumer
import json
import boto
from alchemyapi import AlchemyAPI

sns = boto.connect_sns()
topics = sns.get_all_topics()
mytopics = topics["ListTopicsResponse"]["ListTopicsResult"]["Topics"]
mytopic_arn = mytopics[0]["TopicArn"]
# To consume latest messages and auto-commit offsets
consumer = KafkaConsumer('tweets',
                         group_id='my-group',
                         bootstrap_servers=['localhost:9092'])
for message in consumer:
    # message value and key are raw bytes -- decode if necessary!
    # e.g., for unicode: `message.value.decode('utf-8')`

    try:

    	tweet = json.loads(message.value.decode('utf-8'))
    	print tweet
    	tweet['sentiment'] = AlchemyAPI().sentiment('text', tweet['tweet'])['docSentiment']['type']
    	print tweet['sentiment']
    	sns.publish(mytopic_arn, message=json.dumps(tweet), subject="Tweets")
    except:
    	pass