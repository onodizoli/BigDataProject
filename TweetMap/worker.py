
import json
import boto3
import boto

from alchemyapi import AlchemyAPI
from multiprocessing import Pool


# Initiate SQS
sqs = boto3.resource('sqs')
queue = sqs.get_queue_by_name(QueueName='tweets')
# Setup for SNS
sns = boto.connect_sns()
topics = sns.get_all_topics()
mytopics = topics["ListTopicsResponse"]["ListTopicsResult"]["Topics"]
mytopic_arn = mytopics[0]["TopicArn"]
# sns = boto3.resource('sns')
# topic = sns.create_topic(Name='twitter')
# topic.subscribe(Protocol='http', Endpoint=endpoint)

# Worker nonde for sentiment analysis
def worker(_):
    while True:
        for message in queue.receive_messages(MaxNumberOfMessages=5, WaitTimeSeconds=10):
        	try:
        		tweet = json.loads(message.body)
        		tweet['sentiment'] = AlchemyAPI().sentiment('text', tweet['tweet'])['docSentiment']['type']
        		print tweet
        		print tweet['sentiment']
        		#Send by sns
        		sns.publish(mytopic_arn, message=json.dumps(tweet), subject="Tweets")
        		message.delete()
        		print 'Message processed and deleted'
        	except:
	            # print 'Error happened, message deleted.'
        	        pass
        	# message.delete()


if __name__ == '__main__':
    pool = Pool(3)
    pool.map(worker, range(3))

