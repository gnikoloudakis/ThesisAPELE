# -*- coding: utf-8 -*-
import warnings
from apscheduler.schedulers.background import BackgroundScheduler

from flask import Flask, render_template, request, redirect, session, json, flash, app
from flask.exthook import ExtDeprecationWarning

warnings.simplefilter("ignore", category=ExtDeprecationWarning)
from flask_mongoengine import MongoEngine
from flask_security import Security, MongoEngineUserDatastore, UserMixin, RoleMixin, login_required, roles_required
from flask_gravatar import Gravatar
from werkzeug.utils import secure_filename
# from flask_mail import Mail
# from .models import User, Role, db
from datetime import datetime, timedelta
import os, psutil

scheduler = BackgroundScheduler()

# Create the APP
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = os.urandom(16)
app.config['SECURITY_TRACKABLE'] = True
app.config['SECURITY_CONFIRMABLE'] = False
app.config['SECURITY_REGISTERABLE'] = True
app.config['SECURITY_SEND_REGISTER_EMAIL'] = False
app.config['SECURITY_POST_LOGIN_VIEW'] = '/users'
app.config['SECURITY_POST_REGISTER_VIEW'] = '/users/welcome'
app.config['SECURITY_RECOVERABLE'] = True
app.config['SECURITY_CHANGEABLE'] = True
# app.config['SECURITY_PASSWORDLESS'] = True
app.config['SECURITY_PASSWORD_HASH'] = 'sha512_crypt'
app.config['SECURITY_PASSWORD_SALT'] = "dkljsarlh5oqy89n8y78cuiyweort/3.64,'32cq[ pltwp4[5tq,uwc p349cq nw78qqoq2y345qb5v"

# MongoDB config
app.config['MONGODB_DB'] = 'apele_thesis'
app.config['MONGODB_HOST'] = 'ds011495.mlab.com'
app.config['MONGODB_PORT'] = 11495
app.config['MONGODB_USERNAME'] = 'yannis'
app.config['MONGODB_PASSWORD'] = 'spacegr'

# Create database connection object
db = MongoEngine(app)

# Mail configuration
# After 'Create app'
# app.config['MAIL_SERVER'] = 'smtp.example.com'
# app.config['MAIL_PORT'] = 465
# app.config['MAIL_USE_SSL'] = True
# app.config['MAIL_USERNAME'] = 'username'
# app.config['MAIL_PASSWORD'] = 'password'
# mail = Mail(app)

# Gravatar setup
gravatar = Gravatar(app,
                    size=100,
                    rating='g',
                    default='retro',
                    force_default=False,
                    use_ssl=False,
                    base_url=None)

# FILEPICKER
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])


########################################################################################################################
class History(db.EmbeddedDocument):
    # history_id = db.StringField()
    date = db.DateTimeField(default=datetime.now)
    hospital = db.StringField()
    doctor = db.StringField()
    reason = db.StringField()
    outcome = db.StringField()


class Settings(db.Document):
    volunteer_radius = db.StringField(default='5000')

    def __str__(self):
        return self.volunteer_radius


class Role(db.Document, RoleMixin):
    name = db.StringField(max_length=80, unique=True)
    description = db.StringField(max_length=255)


class User(db.Document, UserMixin):
    photo = db.FileField()
    first_name = db.StringField(max_length=60, default='')
    last_name = db.StringField(max_length=60, default='')
    # username = db.StringField(max_length=60)
    password = db.StringField(max_length=512)
    email = db.StringField(max_length=255, unique=True)
    user_ip = db.StringField(max_length=20, default='0.0.0.0')
    user_type = db.StringField(max_length=60, default='user')
    active = db.BooleanField(default=True)
    birth_date = db.DateTimeField(default=datetime.now(), format='%d-%m-%Y')
    age = db.IntField()
    medical_situation = db.StringField(max_length=512, default='safe')
    full_url = db.StringField(default='/users/full')
    limited_url = db.StringField(default='/users/limited')
    medical_history = db.ListField(db.EmbeddedDocumentField(History))
    first_response_info = db.StringField(max_length=512)
    position = db.PointField(defeult=[25.00, 35.00])
    accuracy = db.FloatField()
    user_state = db.StringField(default='IN')
    date_created = db.DateTimeField(default=datetime.now(), format='%d-%m-%Y')
    confirmed_at = db.DateTimeField(format='%d-%m-%Y')
    last_login_at = db.DateTimeField(format='%d-%m-%Y')
    current_login_at = db.DateTimeField(format='%d-%m-%Y')
    last_login_ip = db.StringField(max_length=45)
    current_login_ip = db.StringField(max_length=45)
    login_count = db.IntField()
    roles = db.ListField(db.ReferenceField(Role))


class Alert(db.Document):
    unsafe_user = db.ReferenceField(User)


class Address(db.Document):
    # address_id = db.StringField(primary_key=True)
    country = db.StringField()
    city = db.StringField()
    street = db.StringField()
    number = db.IntField()
    postal_code = db.IntField()


########################################################################################################################

# Setup Flask-Security
user_datastore = MongoEngineUserDatastore(db, User, Role)
security = Security(app, user_datastore)


@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=5)


@app.route('/')
def index():
    login = 'Log In'
    alert = Alert.objects
    # print(len(alert))
    return render_template('index.html', login=login, alert=alert)


@app.route('/init_db')
def init_db():
    # user_datastore.create_role(name='admin')
    # user_datastore.create_role(name='user')
    # user_datastore.create_user(first_name='Yannis', last_name='Nikoloudakis', email='giannis.nikoloudakis@gmail.com',
    #                            password='spacegr', position=[35, 25])
    # user_datastore.create_user(first_name='George', last_name='Nikoloudakis', email='george.nikoloudakis@gmail.com',
    #                            password='spacegr', position=[35.5, 25.5])
    # user_datastore.create_user(first_name='Aggeliki', last_name='Kokona', email='a.kokona@gmail.com',
    #                            password='spacegr', position=[35.2, 25.2])
    # user_datastore.create_user(first_name='Antiopi', last_name='Nikoloudaki', email='antiopi.nikoloudaki@gmail.com',
    #                            password='spacegr', position=[35.1, 25.1])
    # user_datastore.create_user(first_name='Evangelos', last_name='Markakis', email='markakis@gmail.com',
    #                            password='spacegr', position=[35.12, 25.12])
    # user_datastore.create_user(first_name='Anargyros', last_name='Sideris', email='sideris@gmail.com',
    #                            password='spacegr', position=[35.21, 25.21])
    # user_datastore.create_user(first_name='George', last_name='Alexiou', email='alexiou@gmail.com', password='spacegr',
    #                            position=[35.32, 25.32])
    # user1 = User.objects.get_or_404(email='giannis.nikoloudakis@gmail.com')
    # user_datastore.add_role_to_user(user1, user_datastore.find_role('admin'))
    #
    # user2 = User.objects.get_or_404(email='george.nikoloudakis@gmail.com')
    # user_datastore.add_role_to_user(user2, user_datastore.find_role('user'))
    #
    # user3 = User.objects.get_or_404(email='a.kokona@gmail.com')
    # user_datastore.add_role_to_user(user3, user_datastore.find_role('user'))
    #
    # user4 = User.objects.get_or_404(email='antiopi.nikoloudaki@gmail.com')
    # user_datastore.add_role_to_user(user4, user_datastore.find_role('user'))
    #
    # user5 = User.objects.get_or_404(email='markakis@gmail.com')
    # user_datastore.add_role_to_user(user5, user_datastore.find_role('user'))
    #
    # user6 = User.objects.get_or_404(email='sideris@gmail.com')
    # user_datastore.add_role_to_user(user6, user_datastore.find_role('user'))
    #
    # user7 = User.objects.get_or_404(email='alexiou@gmail.com')
    # user_datastore.add_role_to_user(user7, user_datastore.find_role('user'))
    #
    # alert1 = Alert(User.objects.get_or_404(email='i.louloudis@gmail.com'))
    # alert1.save()
    # settings = Settings(volunteer_radius='5000')
    # settings.save()

    return 'Data Base Initialized'


# @app.route('/users/change')
# def change():
#     return render_template('/templates/security/login_user.html')


@app.route('/users/welcome')
def welcome():
    login = 'Log Out'
    alert = Alert.objects
    users = User.objects.get_or_404(id=session['user_id'])
    result = user_datastore.add_role_to_user(users, user_datastore.find_role('user'))
    return render_template('welcome.html', login=login, users=users, alert=alert)


@app.route('/settings')
@login_required
@roles_required('admin')
def system_settings():
    login = 'Log Out'
    alert = Alert.objects
    users = User.objects.get_or_404(id=session['user_id'])
    settings = Settings.objects.first()
    return render_template('settings.html', login=login, users=users, settings=settings, alert=alert)


@app.route('/settings/save_all', methods=['POST'])
@login_required
@roles_required('admin')
def save_settings():
    login = 'Log Out'
    settings = Settings.objects.first()
    alert = Alert.objects
    users = User.objects.get_or_404(id=session['user_id'])
    radius = request.form['radius']
    settings.update(set__volunteer_radius=radius)
    settings.save()
    settings2 = Settings.objects.first()
    return render_template('settings.html', login=login, users=users, settings=settings2, alert=alert)


@app.route('/users/alerts')
@login_required
def alerts():
    alert = Alert.objects
    return render_template('alerts.html', alert=alert)


@app.route('/users')
@app.route('/users/full')
# @roles_required('admin')
@login_required
def users_full():
    login = 'Log Out'
    alert = Alert.objects
    # user=current_user
    # print(session['user_id'])
    users = User.objects.get_or_404(id=session['user_id'])
    return render_template('user_full.html', login=login, users=users, alert=alert)


@app.route('/users/limited')
@login_required
def users_limited():
    login = 'Log Out'
    alert = Alert.objects
    # user=current_user
    # print(session['user_id'])
    users = User.objects.get_or_404(id=session['user_id'])
    return render_template('user_limited.html', login=login, users=users, alert=alert)


@app.route('/users/edit_profile')
@login_required
def edit_profile():
    login = 'Log Out'
    alert = Alert.objects
    users = User.objects.get_or_404(id=session['user_id'])
    return render_template('edit_profile.html', login=login, users=users, alert=alert)


# FIND - EDIT USERS BUTTON
@app.route('/users/find_change')
@login_required
@roles_required('admin')
def find_change():
    login = 'Log Out'
    alert = Alert.objects
    users = User.objects.get_or_404(id=session['user_id'])
    user_object = User
    return render_template('find_change_user.html', login=login, users=users, user_object=user_object, alert=alert)


# CALLED BY THE SEARCH BUTTON
@app.route('/search_user', methods=['POST'])
@login_required
@roles_required('admin')
def search_user():
    search_text = request.form['search_text']
    users = User.objects(email__contains=search_text)
    return json.dumps(users)


@app.route('/amberalert/<user_email>')
@login_required
def amberalert(user_email):
    alert = Alert.objects
    radius = Settings.objects.first().volunteer_radius
    unsafe_user_email = user_email
    unsafe_user_lng = User.objects(email=unsafe_user_email).first().position['coordinates'][0]
    unsafe_user_lat = User.objects(email=unsafe_user_email).first().position['coordinates'][1]
    # print(user_email)
    user = User.objects(email=user_email).first()
    volunteers = User.objects(user_type='volunteer',
                              position__near=[unsafe_user_lng, unsafe_user_lat],
                              position__max_distance=int(radius))
    return render_template('amberalert.html', user=user, alert=alert, volunteers=volunteers)


@app.route('/change_user/<user_email>')
@login_required
@roles_required('admin')
def change_user_profile(user_email):
    login = 'Log Out'
    alert = Alert.objects
    # print(user_email)
    user = User.objects(email=user_email).first()
    if user.roles == user_datastore.find_role('admin'):
        return render_template('admin_edit_user.html', users=user, login=login, alert=alert)
    else:
        return render_template('edit_profile.html', users=user, login=login, alert=alert)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/change_user/upload_avatar', methods=['GET', 'POST'])
@login_required
def upload_avatar():
    if request.method == 'POST':
        email = request.form['email']
        user = User.objects(email=email).first()
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # return redirect(url_for('uploaded_file', filename=filename))
            user.photo.put(filename)
            user.save()
    return redirect('/users/edit_profile')


@app.route('/change_user/save_all', methods=['POST'])
@login_required
# @roles_required('admin')
def save_all():
    first_name = request.form['first']
    last_name = request.form['last']
    email = request.form['email']
    birth = request.form['birth']
    birth_date = datetime.strptime(birth, '%d-%m-%Y').date()
    role = request.form['role']
    typeq = request.form['type']
    medical_situation = request.form['situation']
    history = request.form['history']
    user = User.objects(email=email).first()
    user.update(set__first_name=first_name,
                set__last_name=last_name,
                set__email=email,
                set__birth_date=birth_date,
                set__age=datetime.now().date().year - birth_date.year,
                set__medical_situation=medical_situation,
                set__user_type=typeq,
                set__position=[float(request.form['long']), float(request.form['lat'])])

    user.update(set__medical_history=[])

    if role == 'admin':
        rem = user_datastore.remove_role_from_user(user, user_datastore.find_role('user'))
        result = user_datastore.add_role_to_user(user, user_datastore.find_role(role))
        user_datastore.commit()
    else:
        rem = user_datastore.remove_role_from_user(user, user_datastore.find_role('admin'))
        result = user_datastore.add_role_to_user(user, user_datastore.find_role(role))
        user_datastore.commit()

    user.save()
    user2 = User.objects(email=email).first()
    # print(user.medical_history)
    for i in json.loads(history):
        data = History(date=datetime.strptime(i["date"], '%d-%m-%Y'),
                       hospital=i["hospital"],
                       doctor=i["doctor"],
                       reason=i["reason"],
                       outcome=i["outcome"])
        # print(i)
        user2.medical_history.append(data)
    user2.save()
    if medical_situation == 'unsafe':
        if not Alert.objects(unsafe_user=User.objects(email=email).first().id):
            alert2 = Alert(User.objects.get_or_404(email=email))
            alert2.save()
        else:
            pass
    else:
        if Alert.objects(unsafe_user=User.objects(email=email).first().id):
            Alert.objects(unsafe_user=User.objects(email=email).first().id).delete()
        else:
            pass
    return redirect('/change_user/' + email)


@app.route('/service/profiling', methods=['POST'])
def profiling_service():
    data = request.data
    dataDict = json.loads(data)
    print(dataDict)
    user = User.objects(email=dataDict['user']).first()
    user.update(set__user_state=dataDict['state'])
    user.update(set__position=[float(dataDict['location']['lng']), float(dataDict['location']['lat'])])
    # loc = {'type': 'Point', 'coordinates': [81.44, 23.61]}
    # user.update(set__position=[81.44, 23.61])
    # print(type(dataDict['location']['lat']))
    # print(dataDict['location']['lng'])
    user.update(set__accuracy=dataDict['location']['accuracy'])
    user.update(set__user_ip=dataDict['user-ip'])
    if dataDict['state'] == 'OUT':
        user.update(set__medical_situation='unsafe')
    elif dataDict['state'] == 'IN':
        user.update(set__medical_situation='safe')
    print("PROFILE RECEIVED USER LOCATION")
    return 'profiling service'


@app.route('/service/profiling/get_full_profile', methods=['POST'])
def get_full_profile():
    data = request.data
    dataDict = json.loads(data)
    user = User.objects(email=dataDict['user']).first()
    # print(user[0].full_url)
    full_profile = {
        "full_url": user.full_url
    }
    print("SENT FULL PROFILE")
    return json.dumps(user)


@app.route('/service/profiling/get_limited_profile', methods=['POST'])
def get_limited_profile():
    data = request.data
    dataDict = json.loads(data)
    user = User.objects(email=dataDict['user']).first()
    # print(user[0].limited_url)
    limited_profile = {
        "limited_url": user.limited_url
    }
    print("SENT LIMITED PROFILE")
    return json.dumps(limited_profile)


@app.route('/service/profiling/get_nearby_volunteers', methods=['POST'])
def get_nearby_volunteers():
    radius = Settings.objects.first().volunteer_radius
    data = request.data
    dataDict = json.loads(data)
    print(dataDict)
    volunteers = User.objects(user_type='volunteer',
                              position__near=[dataDict['location']['lng'], dataDict['location']['lat']],
                              position__max_distance=int(radius))
    found_volunteers = []
    for i in volunteers:
        print(i.email)
        found_volunteers.append({
            "first_name": i.first_name,
            "last_name": i.last_name,
            "email": i.email,
            "location":
                {
                    "lat": i.position['coordinates'][0],
                    "lng": i.position['coordinates'][1],
                    "accuracy": i.accuracy
                }
        })

    print("SENT NEARBY VOLUNTEERS", json.dumps(found_volunteers))
    return json.dumps(found_volunteers)


@app.route('/service/profiling/get_nearby_volunteers_simple', methods=['POST'])
def get_nearby_simple():
    radius = Settings.objects.first().volunteer_radius
    data = request.form
    unsafe_user_email = data['email']
    unsafe_user_lng = User.objects(email=unsafe_user_email).first().position['coordinates'][0]
    unsafe_user_lat = User.objects(email=unsafe_user_email).first().position['coordinates'][1]
    # print(User.objects(email=data['email']).first().position['coordinates'][0])
    volunteers = User.objects(user_type='volunteer',
                              position__near=[unsafe_user_lng, unsafe_user_lat],
                              position__max_distance=int(radius))
    return json.dumps(volunteers)


if __name__ == '__main__':
    # app.run(port=8080)
    scheduler.start()
    app.run(host='0.0.0.0', port=8080)
