from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_login import LoginManager
from flask_session import Session
# from flask_pymongo import PyMongo
import redis
import os

redis_obj = redis_store = redis.Redis.from_url(os.getenv('REDIS_URL'))
# mongo = PyMongo()
db = SQLAlchemy()
mail = Mail()
login_manager = LoginManager()
session = Session()

