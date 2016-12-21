from flask import request, json
import requests, os
import requests, xml.etree.ElementTree as ET
from requests import ConnectionError



# lat = str(dataDict['location']['lat'])
# long = str(dataDict['location']['lng'])
long = str(25.0916924)
lat = str(35.311212)
lost_request = """<?xml version="1.0" encoding="UTF-8"?>
<findService
 xmlns="urn:ietf:params:xml:ns:lost1"
 xmlns:p2="http://www.opengis.net/gml"
 serviceBoundary="value"
 recursive="true">
 <location id="manousos" profile="geodetic-2d">
   <p2:Point id="point1" srsName="urn:ogc:def:crs:EPSG::4326">
      <p2:pos>%s %s</p2:pos>
   </p2:Point>
 </location>
 <service>urn:service:sos</service>
</findService>""" % (long, lat)

headers = {'Content-Type': 'text/plain'}
try:
    lost_responce = requests.post('http://lost.owncloud.gr/lost/lost', data=lost_request, headers=headers)
    # print(lost_request)
except ConnectionError as e:
    print(e)
data = lost_responce.text
lost_data = ET.fromstring(data)
# print(lost_data[0][3].text)
# print(lost_data)
print('posted to lost server' + os.linesep)
print('PSAP: ', lost_data[0][3].text)
print('Emergency Number:', lost_data[0][4].text, os.linesep)
