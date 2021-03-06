import sseclient
import urllib3
import json


def with_urllib3(url):
    """Get a streaming response for the given event feed using urllib3."""
    http = urllib3.PoolManager()
    headers = urllib3.util.make_headers(basic_auth='ttn:xxx')
    return http.request('POST', url, headers=headers, preload_content=False)


#url = 'http://127.0.0.1:5000/ttn/sub'
#url = 'https://alarm.deepcyber.de/calarm.fcgi/ttn/sub'
url = 'https://alarm.deepcyber.de/ttn/sub'

response = with_urllib3(url)
client = sseclient.SSEClient(response)
for event in client.events():
    #print("got:", event.data)
    #pprint.pprint(json.loads(event.data))
    data = json.loads(event.data)
    if data['event'] == "alarm":
        print("{} - CYBER ALARM level {} from {}!!!".format(data['timestamp'], data['level'], data['device']))
