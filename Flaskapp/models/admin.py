from Flaskapp.extensions import db
from flask_login import UserMixin
from datetime import datetime

# create a timezone object for IST
import pytz
ist = pytz.timezone('Asia/Kolkata')

class Admin(UserMixin,db.Model):
    UID    = db.Column(db.Integer , primary_key = True)
    EMAIL = db.Column(db.String(50) , unique=True)
    PASSWORD=db.Column(db.String(1000) , nullable=False)
    IS_ACTIVE = db.Column(db.Boolean, default=True)
    CREATED_AT = db.Column(db.DateTime, default=datetime.now(ist))
    ROLE = db.Column(db.String(20), default="admin")

    def get_id(self):
        return str(self.UID)