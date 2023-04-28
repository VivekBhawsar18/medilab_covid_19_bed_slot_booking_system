from config import AdminCred
from flask_mail import  Message
from Flaskapp.extensions import mail 
from Flaskapp.models.test import Test
from flask import Blueprint, render_template, request
from sqlalchemy.exc import OperationalError, ProgrammingError

bp = Blueprint('test' , __name__ , template_folder='templates')

var = AdminCred()

@bp.route('/')
def index():
    return render_template('test/index.html')

@bp.route('/dbcon')
def db_con():
    try:
        data = Test.query.all()
        # return render_template('dbcon.html',names = data)
        return '<h1>Database connection succesfull!!!</h1>'

    except OperationalError:
        return '<h1>Cannot connect to database.</h1>'
    except ProgrammingError:
        return '<h1>Error executing database query.</h1>'

@bp.route('/email' , methods = ['GET' , 'POST'])
def send_email():
    if request.method == 'POST':
        email = request.form.get('email')
        try:
            msg = Message(
                            'TEST EMAIL',
                            sender = var.MAIL_SENDER,
                            recipients = [email]
                        )
            msg.body = 'Hello user message sent from Flask-Mail'
            mail.send(msg)
            return '<h1>Mail Sent Check Your Inbox !!!</h1>'

        except Exception as e:
            return str(e)
        
    return render_template('test/email-test.html')

@bp.route('/debug-sentry')
def trigger_error():
    division_by_zero = 1 / 0
