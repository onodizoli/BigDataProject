import json
import pandas as pd
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
from key import access_key, secret_key

import sys
reload(sys)
sys.setdefaultencoding('UTF8')

# AWS host
host = "search-twittmap-etr35ieexhu5irovghg3pz4fwy.us-east-1.es.amazonaws.com"

# Connect to AWS
awsauth = AWS4Auth(access_key, secret_key, 'us-east-1', 'es')

# Elasticsearch client setup
es = Elasticsearch(
    hosts=[{'host': host, 'port': 443}],
    http_auth=awsauth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection
)



mappings = {"mappings":{
                "twitter": {
                    "properties": {
                         "tweet":  {
                            "type": "string"
                         },
                         "sentiment": {
                            "type": "string"
                         },
                         "location": {
                             "type": "geo_point"
                         }}
                }
            }}
es.indices.create(index='snsindex', body=mappings)

