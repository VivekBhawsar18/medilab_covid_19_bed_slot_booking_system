import os


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    REDIS_URL = os.getenv('REDIS_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    # SQLALCHEMY_BINDS = os.getenv('SQLALCHEMY_BINDS')
    # MONGO_URI = os.getenv('MONGO_URI')



class MailConfig:
    MAIL_SERVER='smtp.gmail.com'
    MAIL_PORT='465'
    MAIL_USE_SSL=True
    MAIL_USERNAME=os.getenv('GMAIL_ACCOUNT')
    MAIL_PASSWORD=os.getenv('GAMIL_ACC_PASS')


class AdminCred:
    ADMIN_NAME = os.getenv('ADMIN_NAME')
    ADMIN_PWD  = os.getenv('ADMIN_PASS')
    MAIL_SENDER = os.getenv('GMAIL_ACCOUNT')

class SessionConfig:
    SESSION_TYPE            = 'filesystem'
    SESSION_PERMANENT       = False
    SESSION_USE_SIGNER      = True
    SESSION_FILE_DIR        = '/tmp/flask_session'
    SESSION_FILE_THRESHOLD  = 100