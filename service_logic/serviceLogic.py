# -*- coding: utf-8 -*-
import os, time, datetime
import requests, xml.etree.ElementTree as ET
import warnings
from flask.exthook import ExtDeprecationWarning
from requests import ConnectionError
from apscheduler.schedulers.background import BackgroundScheduler
# from Backgroundsceduler import scheduler
from flask import Flask, request, json, render_template, redirect
from flask_mongoengine import MongoEngine
from tofile import write_file
from base64 import b16encode
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor

warnings.simplefilter("ignore", category=ExtDeprecationWarning)

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = os.urandom(16)

# MongoDB config
app.config['MONGODB_DB'] = 'apele_thesis'
app.config['MONGODB_HOST'] = 'ds011495.mlab.com'
app.config['MONGODB_PORT'] = 11495
app.config['MONGODB_USERNAME'] = 'yannis'
app.config['MONGODB_PASSWORD'] = 'spacegr'

scheduler = BackgroundScheduler(executors={
    'default': ThreadPoolExecutor(15),
    'processpool': ProcessPoolExecutor(13)
}, job_defaults={
    'coalesce': True,
    'max_instances': 10
})

wf = write_file(app.root_path)
wf.startFile()

# Create database connection object
db = MongoEngine(app)

time_started = 0
time_for_volunteers = 0
time_for_psap = 0

LogFile = []
nearby_volunteers = []


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
    global time_started
    global nearby_volunteers
    nearby_users = requests.post('http://' + pr_srvc_ip + ':' + pr_srvc_port + '/service/profiling/get_nearby_volunteers', data)
    nearby_volunteers = nearby_users.json()
    # print ('1111111111111111111', nearby_users.json(), '222222', nearby_volunteers)
    scheduler.add_job(wf.outputFile, 'date', next_run_time=datetime.datetime.now(), args=[json.loads(data)['user'] + ',' + 'Time for Volunteers', str(time.time() - time_started)],
                      id=b16encode(os.urandom(16)).decode('utf-8'), replace_existing=False)
    # wf.outputFile(json.loads(data)['user'] + ',' + 'Time for Volunteers ', str(time.time() - time_started) + 'seconds')
    print ('Volunteers:' + os.linesep)
    for i in nearby_volunteers:
        print ('Last Name: ', i['last_name'])
    return nearby_volunteers


def create_lost_request(data):
    global time_started
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
   </findService>""" % (long, lat)

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
    print('posted to lost server' + os.linesep)
    print('PSAP: ', lost_data[0][3].text)
    print('Emergency Number:', lost_data[0][4].text, os.linesep)

    scheduler.add_job(wf.outputFile, 'date', next_run_time=datetime.datetime.now(), args=[dataDict['user'] + ',' + 'Time for LoST', str(time.time() - time_started)],
                      id=b16encode(os.urandom(16)).decode('utf-8'), replace_existing=False)
    # wf.outputFile(dataDict['user'] + ',' + 'Time for LoST ', str(time.time() - time_started) + 'seconds')

    LogFile.append('posted to lost server')
    LogFile.append('PSAP: ' + lost_data[0][3].text)
    LogFile.append('Emergency Number:' + lost_data[0][4].text)


@app.route('/logic')
def service_logic_index():
    settings = service_logic_settings.objects.first()
    return render_template('index.html', settings=settings)


@app.route('/logic/save_all', methods=['POST'])
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

    return redirect('/logic')


@app.route('/logic/service/service_logic', methods=['POST'])
def service_logic():
    global time_started
    data = request.data
    time_started = json.loads(data)['time_stamp']
    print (time_started)
    # fp = get_full_profile(data)
    # lp = get_limited_profile(data)
    # nu = get_nearby_users(data)   # Getting nearby volunteers
    scheduler.add_job(get_nearby_users, 'date', next_run_time=datetime.datetime.now(), args=[data], id=b16encode(os.urandom(16)).decode('utf-8'), replace_existing=False)
    scheduler.add_job(create_lost_request, 'date', next_run_time=datetime.datetime.now(), args=[data], id=b16encode(os.urandom(16)).decode('utf-8'), replace_existing=False)
    # create_lost_request(data)
    # print(fp)
    # print(lp)
    return 'ok'


@app.route('/logic/init_log', methods=['GET'])
def init_log():
    with open(app.root_path + '/logs/log.txt', 'a') as logfile:
        logfile.write('---------------------------------' + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + '---------------------------' + os.linesep)
        return 'initialized log file'


@app.route('/logic/get_log', methods=['GET'])
def get_logs():
    with open(app.root_path + '/logs/log.txt', 'r') as logfile:
        a = logfile.read()
        return json.dumps(a)


@app.route('/logic/clear_log', methods=['GET'])
def get_logs():
    with open(app.root_path + '/logs/log.txt', 'w') as logfile:
        logfile.write('')
        return 'Cleared Log File....'


@app.route('/logic/service/get_log', methods=['GET'])
def get_log():
    return json.dumps(LogFile)


if __name__ == '__main__':
    # app.secret_key = 'super secret key'
    # app.run(debug=True, port=5000)
    scheduler.start()
    app.run(host='0.0.0.0', port=8082)
