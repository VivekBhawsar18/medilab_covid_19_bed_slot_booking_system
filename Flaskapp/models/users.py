from Flaskapp.extensions import db
from flask_login import UserMixin
from datetime import datetime

# create a timezone object for IST
import pytz
ist = pytz.timezone('Asia/Kolkata')

class User(UserMixin,db.Model):
    UID    = db.Column(db.Integer , primary_key = True)
    EMAIL = db.Column(db.String(50) , unique=True)
    IS_ACTIVE = db.Column(db.Boolean, default=True)
    CREATED_AT = db.Column(db.DateTime, default=datetime.now(ist))
    LOGIN_METHOD = db.Column(db.String(20), nullable=False)
    ROLE = db.Column(db.String(20), default="user")
    USER = db.relationship('Userdata' , backref='user_data')
    CREDENTIALS = db.relationship('Credentials' , backref='user_credentials')
    BOOKINGS = db.relationship('Userbookings' , backref='user_booking')

    
    def get_id(self):
        return str(self.UID)

    def __str__(self) -> str:
        return f"{self.id}-{self.email}-{self.firstname}-{self.lastname}-{self.password}"
    

class Credentials(db.Model):
    __tablename__ = 'credentials'
    CID = db.Column(db.Integer , primary_key = True)
    UID   = db.Column(db.Integer , db.ForeignKey('user.UID'))
    PASSWORD = db.Column(db.String(1000) , nullable=False)

    def get_id(self):
        return str(self.UID)
    


class Userdata(db.Model):
    ID    = db.Column(db.Integer , primary_key = True)
    UID = db.Column(db.Integer , db.ForeignKey('user.UID'))
    USER_NAME = db.Column(db.String(100), nullable=False)
    CONTACT = db.Column(db.String(20), unique=True)
    GENDER = db.Column(db.String(20))
    ADDRESS = db.Column(db.String(100))
    

class Userbookings(db.Model):

    BID = db.Column(db.Integer,primary_key=True)
    UID = db.Column(db.Integer , db.ForeignKey('user.UID'))
    HCODE = db.Column(db.String(20), nullable=False)
    HOSPITAL_NAME = db.Column(db.String(100), nullable=False)
    BED_TYPE = db.Column(db.String(100), nullable=False)
    OXYGEN_LEVEL = db.Column(db.Integer)
    PATIENT_NAME = db.Column(db.String(100), nullable=False)
    PATIENT_CONTACT = db.Column(db.String(100),unique=True)
    


