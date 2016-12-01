# -*- coding: utf-8 -*-

from flask.exthook import ExtDeprecationWarning
import warnings
warnings.simplefilter("ignore", category=ExtDeprecationWarning)
from flask import Flask, request, json, render_template, redirect
import requests
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

g_url = 'https://www.googleapis.com/geolocation/v1/geolocate?key=AIzaSyAAyeOvQsvoNanKXf2MS8PmiHKDK-xOdVg'
times = 0
state = 'IN'
LogFile = []


class positioning_settings(db.Document):
    profiling_service_ip = db.StringField(default='127.0.0.1', max_length=100)
    profiling_service_port = db.StringField(default='8080', max_length=10)
    service_logic_ip = db.StringField(default='127.0.0.1', max_length=100)
    service_logic_port = db.StringField(default='5000', max_length=10)

    def __str__(self):
        return self.profiling_service_ip

# pp = positioning_settings(profiling_service_ip='127.0.0.1')
# pp.save()
pr_srvc_ip = positioning_settings.objects.first().profiling_service_ip
pr_srvc_port = positioning_settings.objects.first().profiling_service_port
sl_ip = positioning_settings.objects.first().service_logic_ip
sl_port = positioning_settings.objects.first().service_logic_port


def define_position(rssi, cell, user, ip):
    global times, state
    if rssi < -95:
        times += 1
        if times > 3:
            print(rssi, 'User is outside the House')  # user is unsafe after 3 times
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
    requests.post('http://' + sl_ip + ':' + sl_port + '/service/service_logic',
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
    settings = positioning_settings.objects.first()
    settings.update(set__profiling_service_ip=pr_srvc_ip,
                    set__profiling_service_port=pr_srvc_port,
                    set__service_logic_ip=sl_ip,
                    set__service_logic_port=sl_port)

    return redirect('/positioning')


@app.route('/positioning/service/positioning_app', methods=['POST'])
def positioning():
    LogFile = ' '
    data = request.data
    dataDict = json.loads(data)
    user = dataDict['user']
    ip = request.remote_addr
    # print(user)
    rssipower = dataDict['RSSI']
    # print(rssipower)
    celldata = dataDict['cellular']
    # print(json.dumps(celldata))
    define_position(rssipower, json.dumps(celldata), user, ip)
    return ip


@app.route('/positioning/service/get_log', methods=['GET'])
def get_log():
    return json.dumps(LogFile)

if __name__ == '__main__':
    # app.run(port=4000)
    app.run(host='0.0.0.0', port=8081)
