import requests
from requests import ConnectionError
import time

# from profilingService import User

first = 'user'
last = 'doe'
user_mail = ' '

for i in range(10):
    user_mail = first + str(i).zfill(2) + last + str(i).zfill(2) + '@gmail.com'
    print user_mail
    body = '''
    {
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
    ''' % (user_mail)
    try:
        requests.post('http://localhost:8081/positioning/service/positioning_app', data=body)
    except ConnectionError as e:
        print(e)
    time.sleep(0.5)
    # print body
