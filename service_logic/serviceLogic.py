# -*- coding: utf-8 -*-

from flask.exthook import ExtDeprecationWarning
import warnings
warnings.simplefilter("ignore", category=ExtDeprecationWarning)
from flask import Flask, request, json, render_template, redirect
import requests, xml.etree.ElementTree as ET
from flask_mongoengine import MongoEngine
import os

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = os.urandom(16)


# MongoDB config
app.config['MONGODB_DB'] = 'apele_thesis'
app.config['MONGODB_HOST'] = 'ds011495.mlab.com'
app.config['MONGODB_PORT'] = 11495
app.config['MONGODB_USERNAME'] = 'yannis'
app.config['MONGODB_PASSWORD'] = 'spacegr'

# Create database connection object
db = MongoEngine(app)


LogFile = []


class service_logic_settings(db.Document):
    profiling_service_ip = db.StringField(default='127.0.0.1', max_length=100)
    profiling_service_port = db.StringField(default='8080', max_length=10)
    lost_server_ip = db.StringField(default='10.0.3.86', max_length=100)
    lost_server_port = db.StringField(default='8080', max_length=10)

    def __str__(self):
        return self.profiling_service_ip

# pp = service_logic_settings(profiling_service_ip='127.0.0.1')
# pp.save()
pr_srvc_ip = service_logic_settings.objects.first().profiling_service_ip
pr_srvc_port = service_logic_settings.objects.first().profiling_service_port
lost_ip = service_logic_settings.objects.first().lost_server_ip
lost_port = service_logic_settings.objects.first().lost_server_port


def get_full_profile(data):
    full_url = requests.post('http://' + pr_srvc_ip + ':' + pr_srvc_port + '/service/profiling/get_full_profile', data)
    fu = full_url.json()
    return fu


def get_limited_profile(data):
    limited_url = requests.post('http://' + pr_srvc_ip + ':' + pr_srvc_port + '/service/profiling/get_limited_profile', data)
    lu = limited_url.json()
    return lu


def get_nearby_users(data):
    nearby_users = requests.post('http://' + pr_srvc_ip + ':' + pr_srvc_port + '/service/profiling/get_nearby_volunteers', data)
    nu = nearby_users.json()
    return nu


def create_lost_request(data):
    dataDict = json.loads(data)
    lat = str(dataDict['location']['lat'])
    long = str(dataDict['location']['lng'])
    # long = str(13.4634816)
    # lat = str(52.5499857)
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
   </findService>"""%(long, lat)

    headers = {'Content-Type': 'text/plain'}
    try:
        lost_responce = requests.post('http://' + lost_ip + ':' + lost_port + '/lost/lost', data=lost_request, headers=headers)
        # print(lost_request)
    except ConnectionError as e:
        print(e)
    data = lost_responce.text
    lost_data = ET.fromstring(data)
    # print(lost_data[0][3].text)
    # print(lost_data)
    print('posted to lost server\n')
    print('PSAP: ', lost_data[0][3].text)
    print('Emergency Number:', lost_data[0][4].text, '\n')
    LogFile.append('posted to lost server')
    LogFile.append('PSAP: ' + lost_data[0][3].text)
    LogFile.append('Emergency Number:' + lost_data[0][4].text)


@app.route('/service_logic_index')
def service_logic_index():
    settings = service_logic_settings.objects.first()
    return render_template('index.html', settings=settings)


@app.route('/save_all', methods=['POST'])
def save_all():
    global pr_srvc_ip
    pr_srvc_ip = request.form['profiling_ip']
    global pr_srvc_port
    pr_srvc_port = request.form['profiling_port']
    global lost_ip
    lost_ip = request.form['lost_ip']
    global lost_port
    lost_port = request.form['lost_port']

    settings = service_logic_settings.objects.first()
    settings.update(set__profiling_service_ip=pr_srvc_ip,
                    set__profiling_service_port=pr_srvc_port,
                    set__lost_server_ip=lost_ip,
                    set__lost_server_port=lost_port)

    return redirect('/service_logic_index')


@app.route('/service/service_logic', methods=['POST'])
def service_logic():
    data = request.data
    fp = get_full_profile(data)
    lp = get_limited_profile(data)
    nu = get_nearby_users(data)
    create_lost_request(data)
    # print(fp)
    # print(lp)
    for i in nu:
        print('Last Name: ', i['last_name'])
        LogFile.append(i['last_name'])
    return 'ok'


@app.route('/service/get_log', methods=['GET'])
def get_log():
    return json.dumps(LogFile)


if __name__ == '__main__':
    # app.secret_key = 'super secret key'
    # app.run(debug=True, port=5000)
    app.run(host='0.0.0.0', port=8082)
