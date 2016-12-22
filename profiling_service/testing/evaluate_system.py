import requests
from requests import ConnectionError
import time

# from profilingService import User
timestarted = time.time()
first = 'user'
last = 'doe'
user_mail = ' '
time_stamp = 0
for i in range(1000):
    time_stamp = time.time()
    user_mail = first + str(i).zfill(2) + last + str(i).zfill(2) + '@gmail.com'
    print user_mail
    body = '''
    {
    "time_stamp":%s,
    "user": "%s",
    "RSSI":-96,
    "cellular": {
    "cellTowers": [
    {
    "cellId": 64023,
    "locationAreaCode": 2316,
    "mobileCountryCode": 202,
    "mobileNetworkCode": 1,
    "signalStrength": -95
    },
    {
    "cellId": 61355,
    "locationAreaCode": 2317,
    "mobileCountryCode": 202,
    "mobileNetworkCode": 1,
    "signalStrength": -70
    },
    {
    "cellId": 61342,
    "locationAreaCode": 2316,
    "mobileCountryCode": 202,
    "mobileNetworkCode": 1,
    "signalStrength": -850
    }
    ]
    }
    }
    ''' % (time_stamp, user_mail)
    try:
        requests.post('http://localhost:8081/positioning/service/positioning_app', data=body)
    except ConnectionError as e:
        print(e)
    time.sleep(1)
    # print body
print ('execution time: ' + str(timestarted - time.time()))
