from flask import Flask, flash, redirect, url_for        # Importing required packages and modules from the Flask library
from flask_caching import Cache

from config import Config , MailConfig , SessionConfig   # Importing custom configuration classes for the application

# Importing extensions for the application
from Flaskapp.extensions import db , mail , login_manager , session 

# Importing models for the hospital and users
from Flaskapp.models.hospital import *
from Flaskapp.models.users import *
from Flaskapp.models.admin import *

# Loding Env variables from .flaskenv file
from dotenv import load_dotenv
load_dotenv()

#----------------------------------------------------------------------------#
#                                 Logging                                    #
#----------------------------------------------------------------------------#

import logging                                              # Import the logging module for logging

logging.basicConfig(filename='app.log', level=logging.DEBUG,
                        format='%(asctime)s:%(levelname)s:%(message)s')
logger = logging.getLogger(__name__)


#----------------------------------------------------------------------------#
#                                 Monitoring                                 #
#----------------------------------------------------------------------------#

import sentry_sdk                                           # Import the Sentry SDK for error tracking
from sentry_sdk.integrations.flask import FlaskIntegration  # Import the FlaskIntegration from the Sentry SDK for integrating with Flask

# Initialize the Sentry SDK with the FlaskIntegration
sentry_sdk.init(
    dsn="https://86bdac5970d94915bf25623282ca4592@o4504660581482496.ingest.sentry.io/4504660582924288",
    integrations=[
        FlaskIntegration(),
    ],

    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=1.0
)


# Creating a Flask application instance
app = Flask(__name__ , static_folder='static' , template_folder='templates')
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

# App configuration

app.config.from_object(Config)        # basic configuration details for the application
app.config.from_object(MailConfig)    # Configuration for Flask-Mail
app.config.from_object(SessionConfig) # Configuration for Flask-Session


# Initializing extensions for the Flask application

# The database extension is initialized
db.init_app(app)
# mongo.init_app(app)
# The email extension is initialized
mail.init_app(app)
# The login management extension is initialized
login_manager.init_app(app)
# The session management extension is initialized
session.init_app(app)
# Setting the login view for the application
login_manager.login_view = 'home.index'
# Setting the message category for the login messages in the application
login_manager.login_message_category = "info"

@login_manager.unauthorized_handler
def unauthorized():
        flash( 'User must be logged in to access this content','warning')
        return redirect(url_for('authentication.user_sign_in'))


# Defining a user_loader function for the login manager extension
# The function takes the user_id as an argument and returns the corresponding user object
@login_manager.user_loader
def user_load(user_id):
# Query for user by id from three different models
        try:
                user = Admin.query.get(user_id) or HospitalUser.query.get(user_id)

                if user:
                        return user

                user = User.query.get(user_id)

                if user:
                        return user

                raise ValueError('User not found')
        except Exception as e:
                logging.error(f'Error getting user by id {user_id}: {str(e)}')
                return None


# Registering blueprints for the application

# The home blueprint is registered with the application
from Flaskapp.blueprints.home.views import bp as Home_bp
app.register_blueprint(Home_bp)

# The test blueprint is registered with the application and is prefixed with '/test'
from Flaskapp.blueprints.test.views import bp as Test_bp
app.register_blueprint(Test_bp ,url_prefix ='/test')

from Flaskapp.blueprints.authentication.views import bp as Auth_bp
app.register_blueprint(Auth_bp)

# The admin blueprint is registered with the application and is prefixed with '/admin'
from Flaskapp.blueprints.admin.views import bp as Admin_bp
app.register_blueprint(Admin_bp , url_prefix = '/admin')

# The hospital blueprint is registered with the application and is prefixed with '/hospital'
from Flaskapp.blueprints.hospital.views import bp as Hospital_bp
app.register_blueprint(Hospital_bp , url_prefix = '/hospital')

# The user blueprint is registered with the application and is prefixed with '/user'
from Flaskapp.blueprints.user.views import bp as User_bp
app.register_blueprint(User_bp , url_prefix = '/user')

