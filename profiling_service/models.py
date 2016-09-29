from flask.ext.mongoengine import MongoEngine
from flask.ext.security import RoleMixin, UserMixin
from old_profilingService import app
from datetime import datetime
db = MongoEngine(app)


class Role(db.Document, RoleMixin):
    name = db.StringField(max_length=80, unique=True)
    description = db.StringField(max_length=255)


class Address(db.Document):
    # address_id = db.StringField(primary_key=True)
    country = db.StringField()
    city = db.StringField()
    street = db.StringField()
    number = db.IntField()
    postal_code = db.IntField()


class History(db.EmbeddedDocument):
    # history_id = db.StringField()
    date = db.DateTimeField(default=datetime.now)
    hospital = db.StringField()
    doctor = db.StringField()
    reason = db.StringField()
    outcome = db.StringField()


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
    position = db.PointField()
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