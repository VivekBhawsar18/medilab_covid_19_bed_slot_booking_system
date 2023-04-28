from sqlalchemy import CheckConstraint
from Flaskapp.extensions import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# create a timezone object for IST
import pytz
ist = pytz.timezone('Asia/Kolkata')



class HospitalUser(db.Model , UserMixin):
    __tablename__ = 'hospital_user'
    HCODE           = db.Column(db.String(20),primary_key=True )
    EMAIL           = db.Column(db.String(50),unique=True , nullable=False)
    PASSWORD_HASH   = db.Column(db.String(1000) , nullable=False)
    IS_ACTIVE       = db.Column(db.Boolean, default=True)
    CREATED_AT      = db.Column(db.DateTime, default=datetime.now(ist))
    ROLE            = db.Column(db.String(20), default="hospital")
    HOS_DATA        = db.relationship('Hospital' , backref='huser')

    def set_password(self, password):
        self.PASSWORD_HASH = generate_password_hash(password , method='sha256')

    def check_password(self, password):
        return check_password_hash(self.PASSWORD_HASH, password)
    
    def get_id(self):
        return str(self.HCODE)


class Hospital(db.Model):
    ID                  = db.Column(db.Integer,primary_key=True)
    HCODE               = db.Column(db.String(20) , db.ForeignKey('hospital_user.HCODE') , nullable=False)
    HOSPITAL_NAME       = db.Column(db.String(100))
    ICU_BEDS            = db.Column(db.Integer , nullable=False ,default=0 )
    NORMAL_BEDS         = db.Column(db.Integer , nullable=False ,default=0 )
    VENTILATOR_BEDS     = db.Column(db.Integer , nullable=False ,default=0 )
    HIGH_CARE_UNIT_BEDS = db.Column(db.Integer , nullable=False ,default=0 )

    __table_args__ = (
        CheckConstraint('normal_beds >= 0', name='normal_beds_positive'),
        CheckConstraint('icu_beds >= 0', name='icu_beds_positive'),
        CheckConstraint('ventilator_beds >= 0', name='ventilator_beds_positive'),
        CheckConstraint('high_care_unit_beds >= 0', name='high_care_unit_beds_positive'),
    )
