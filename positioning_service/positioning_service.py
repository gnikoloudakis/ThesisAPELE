# -*- coding: utf-8 -*-

from flask.exthook import ExtDeprecationWarning
import warnings
from tofile import write_file
from base64 import b16encode
from flask import Flask, request, json, render_template, redirect
import requests, logging
from flask_mongoengine import MongoEngine
import os, sys
from datetime import datetime, timedelta

warnings.simplefilter("ignore", category=ExtDeprecationWarning)

from apscheduler.schedulers.background import BackgroundScheduler

logging.basicConfig()

scheduler = BackgroundScheduler()

app = Flask(__name__)
wf = write_file(app.root_path)
wf.startFile()

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


class positioning_settings(db.Document):
    profiling_service_ip = db.StringField(default='127.0.0.1', max_length=100)
    profiling_service_port = db.StringField(default='8080', max_length=10)
    service_logic_ip = db.StringField(default='127.0.0.1', max_length=100)
    service_logic_port = db.StringField(default='5000', max_length=10)
    google_api_key = db.StringField()

    def __str__(self):
        return self.profiling_service_ip


# pp = positioning_settings(profiling_service_ip='127.0.0.1')
# pp.save()
pr_srvc_ip = positioning_settings.objects.first().profiling_service_ip
pr_srvc_port = positioning_settings.objects.first().profiling_service_port
sl_ip = positioning_settings.objects.first().service_logic_ip
sl_port = positioning_settings.objects.first().service_logic_port
gkey = positioning_settings.objects.first().google_api_key

g_url = 'https://www.googleapis.com/geolocation/v1/geolocate?key=' + gkey
times = 0
state = 'IN'
LogFile = []
time_stamp = 0


def init_schedulers():
    url = sys.argv[1] if len(sys.argv) > 1 else 'sqlite:///' + app.root_path + '\example.sqlite'
    scheduler.add_jobstore('sqlalchemy', url=url)
    print('To clear the alarms, delete the example.sqlite file.')
    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass


def define_position(rssi, cell, user, ip):
    global times, state
    if rssi < -95:
        times += 1
        if times > 3:
            print(user, rssi, 'User is outside the House')  # user is unsafe after 3 times
            wf.outputFile(user + ' ', str(datetime.now()))
            LogFile.append(str(rssi) + 'User is outside the House  ')
            state = 'OUT'
            location = acquire_position(cell)  # get location from Google
            inform_profile(location, state, user, ip)  # inform profiling service
            inform_logic(location, state, user, ip)  # inform service logic
        else:
            print(times)
    elif rssi > -95:
        times = 0
        print(rssi, 'User is inside the house')
        LogFile.append(str(rssi) + 'User is inside the house  ')
        state = 'IN'
        inform_profile(None, state, user, ip)  # inform profiling service
    else:
        print(rssi, 'prama')
        print('den ksero ti na kano')


# GET LOCATION FROM GOOGLE API USING CELLULAR DATA
def acquire_position(data):
    # print('google')
    r = requests.post(g_url, data=data)  # get location from Google
    # p = json.loads(r.content)
    p = r.json()
    print("GOT POSITION FROM GOOGLE", p)
    LogFile.append('GOT POSITION FROM GOOGLE ' + str(p))
    return p


def inform_profile(user_location, user_state, user, ip):  # port 8080
    # print('lat:', user_location['location']['lat'])
    # print('long:', user_location['location']['lng'])
    # print('accuracy:', user_location['accuracy'])
    data = {
        "user": user,
        "user-ip": ip,
        "state": user_state,
        "location":
            {
                "lat": user_location['location']['lat'],
                "lng": user_location['location']['lng'],
                "accuracy": user_location['accuracy']
            }
    }

    requests.post('http://' + pr_srvc_ip + ':' + pr_srvc_port + '/service/profiling', data=json.dumps(data))  # localhost:8080/service/profiling
    print("INFORMED PROFILING SERVICE", pr_srvc_ip, pr_srvc_port)
    LogFile.append('INFORMED PROFILING SERVICE  ')
    return json.dumps(data)


def inform_logic(user_location, user_state, user, ip):  # port 6000
    # print('lat:', user_location['location']['lat'])
    # print('long:', user_location['location']['lng'])
    # print('accuracy:', user_location['accuracy'])
    global time_stamp
    data = {
        "time_stamp": time_stamp,
        "user": user,
        "user-ip": ip,
        "state": user_state,
        "location":
            {
                "lat": user_location['location']['lat'],
                "lng": user_location['location']['lng'],
                "accuracy": user_location['accuracy']
            }
    }
    requests.post('http://' + sl_ip + ':' + sl_port + '/logic/service/service_logic',
                  data=json.dumps(data))  # localhost:8080/service/service_logic
    print("INFORMED SERVICE LOGIC")
    LogFile.append('INFORMED SERVICE LOGIC  ' + sl_ip + sl_port)
    return json.dumps(data)


@app.route('/positioning')
def positioning_service_index():
    settings = positioning_settings.objects.first()
    return render_template('index.html', settings=settings)


@app.route('/positioning/save_all', methods=['POST'])
def save_all():
    # global pos_srvc_port
    # pos_srvc_port = request.form['positioning_port']
    global pr_srvc_ip
    pr_srvc_ip = request.form['profiling_ip']
    global pr_srvc_port
    pr_srvc_port = request.form['profiling_port']
    global sl_ip
    sl_ip = request.form['logic_ip']
    global sl_port
    sl_port = request.form['logic_port']
    global gkey
    gkey = request.form['gkey']

    settings = positioning_settings.objects.first()
    settings.update(set__profiling_service_ip=pr_srvc_ip,
                    set__profiling_service_port=pr_srvc_port,
                    set__service_logic_ip=sl_ip,
                    set__service_logic_port=sl_port,
                    set__google_api_key=gkey)

    return redirect('/positioning')


@app.route('/positioning/service/positioning_app', methods=['POST'])
def positioning():
    global time_stamp
    LogFile = ' '
    data = request.data
    print(type(data))
    dataDict = json.loads(data)
    time_stamp = dataDict['time_stamp']
    user = dataDict['user']
    ip = request.remote_addr
    # print(user)
    rssipower = dataDict['RSSI']
    # print(rssipower)
    celldata = dataDict['cellular']
    # print(json.dumps(celldata))
    # define_position(rssipower, json.dumps(celldata), user, ip)
    scheduler.add_job(define_position, 'date', run_date=datetime.now(), args=[rssipower, json.dumps(celldata), user, ip])
    # define_position(rssipower, json.dumps(celldata), user, ip)
    return ip


@app.route('/positioning/service/get_log', methods=['GET'])
def get_log():
    return json.dumps(LogFile)


if __name__ == '__main__':
    # app.run(port=4000)
    init_schedulers()
    app.run(host='0.0.0.0', port=8081)
