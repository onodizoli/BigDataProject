from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit, disconnect
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
from key import access_key, secret_key
import requests
import json, sys, socket

reload(sys)
sys.setdefaultencoding("utf-8")

app = Flask(__name__)

async_mode = None

socketio = SocketIO(app)

host = "search-twittmap-etr35ieexhu5irovghg3pz4fwy.us-east-1.es.amazonaws.com"
awsauth = AWS4Auth(access_key, secret_key, 'us-east-1', 'es')
                   
es = Elasticsearch(
    hosts=[{'host': host, 'port': 443}],
    http_auth=awsauth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection
)
print(es.info())

def msg_process(msgRaw):
    msg = json.loads(msgRaw)
    print msg['tweet']
    print msg['location']

    tweets = {
        'tweet': msg['tweet'],
        'location': msg['location'],
        'sentiment': msg['sentiment']
    }
    # es_entries = { 'tweet': tweets['text'][i],
    #                'location': str(tweets['location'][i][1])+","+str(tweets['location'][i][0])
    # }
    res = es.index(index="snsindex", doc_type="twitter", body=tweets)
    # get_size = es.search(index = "cloud")['hits']['total']
    # res = es.index(index="cloud", doc_type="tweet", id=get_size+1, body=doc)
    print(res['created'])

    returned = ""+json.dumps(tweets)
    socketio.send(returned, namespace="/sns")
    # es.indices.refresh(index="cloud")
    # print msg

@app.route('/', methods=['GET', 'POST', 'PUT'])
def index():
    try:
        js = json.loads(request.data)
        print js
    except:
        pass

    hdr = request.headers.get('X-Amz-Sns-Message-Type')
    # subscribe to the SNS topic
    if hdr == 'SubscriptionConfirmation' and 'SubscribeURL' in js:
        r = requests.get(js['SubscribeURL'])
        print r

    if hdr == 'Notification':
        print js['Message']
        msg_process(js['Message'])

    # return render_template('googleMap.html', msg=r)
    return render_template('googleMap.html')

@app.route('/sns', methods=['GET', 'POST', 'PUT'])
def sns():
    return render_template('snsMap.html', async_mode=socketio.async_mode)

@app.route('/queryES/<key>', methods=['POST'])
def queryES(key):
    res = es.search(index='snsindex', doc_type='twitter', size=1000, from_=0, body={"query":{'match':{"tweet": key}}})
    print res
    return jsonify(res['hits']['hits'])

@app.route('/queryClick/<clickCoordinates>', methods=['POST'])
def queryClick(clickCoordinates):
    coordinates = clickCoordinates.split(',')
    lat = coordinates[0]
    lon = coordinates[1]
    float(lat.replace(u'\N{MINUS SIGN}', '-'))
    float(lon.replace(u'\N{MINUS SIGN}', '-'))
    circleBody =  {"filter": {
                    "geo_distance": {
                      "distance": "100km", 
                      "location": { 
                        "lat": lat,
                        "lon": lon
                      }
                    }
                  }
                } 
    res = es.search(index='snsindex', doc_type='twitter', size=1000, from_=0, body=circleBody)
    # res = es.search(index='twittmap', doc_type='twitter', size=1000, from_=0, body={"filter" : {"geo_distance" : {"distance" : "100km","location" : {"lat" : lat,"lon" : lon}}}})

    # print res
    return jsonify(res['hits']['hits'])
    # return clickCoordinates

# @app.route('/search', methods=['POST'])
# def search():
#     try:
#         userInput = str(request.form['userInput'])
#         print userInput

#         es = es.search(index='indexgeo4', doc_type='twitter', size=1000, from_=0, body={"query":{'match':{"tweet": userInput}}})
#         print res
#         return jsonify(res['hits']['hits'])
#     except Exception, e:
#         print traceback.print_exc()
#         return 'False'
# def server_run():
#     myIP = socket.gethostbyname(socket.gethostbyname())
#     socketio.run(app, host=myIP, port=5000)

if __name__ == '__main__':
    # app.run(
    #     host = "160.39.203.60",
    #     port = 5000
    # )
    myIP = socket.gethostbyname(socket.gethostname())
    socketio.run(app, host=myIP, port=5000)
