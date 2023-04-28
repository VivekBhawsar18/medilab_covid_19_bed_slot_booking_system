import json
import requests
from Flaskapp import cache
from Flaskapp.utils.otp import *
from Flaskapp.extensions import db
from Flaskapp.models.admin import *
from Flaskapp.models.users import *
from Flaskapp.models.hospital import *
from Flaskapp.utils.authentication import *
from oauthlib.oauth2 import WebApplicationClient
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import  current_user, login_required, login_user, logout_user
from Flaskapp.utils.email import send_user_creation_confirmation_email as send_email
from Flaskapp.utils.email import send_google_user_creation_confirmation_email as send_google_email
from flask import Blueprint, current_app, flash, redirect, render_template,  request, session, url_for

bp = Blueprint('authentication' , __name__)


#  ************************************************ Google Sign-In ************************************************ 


# we are fetching it from the .env file 
GOOGLE_CLIENT_ID=os.getenv('GOOGLE_CLIENT_ID' , None)
GOOGLE_CLIENT_SECRET=os.getenv('GOOGLE_CLIENT_SECRET' , None)

client = WebApplicationClient(GOOGLE_CLIENT_ID)

GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)


def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

@bp.route('/google/login')
@authentication.handle_auth_errors
def google_sign_in():

        google_provider_cfg = get_google_provider_cfg()
        authorization_endpoint = google_provider_cfg['authorization_endpoint']
        request_uri = client.prepare_request_uri(
            authorization_endpoint,
            redirect_uri= "http://localhost:5000/login/callback",
            # redirect_uri= request.base_url + "/callback",
            scope= ['openid' ,'email' , 'profile']
        )
        return redirect(request_uri)


@bp.route('/login/callback')
@authentication.handle_auth_errors
def google_callback():
        code = request.args.get('code')

        google_provider_cfg = get_google_provider_cfg()

        token_endpoint = google_provider_cfg['token_endpoint']

        token_url , headers, body = client.prepare_token_request(
            token_endpoint,
            authorization_response=request.url,
            redirect_url= request.base_url,
            code=code
        )

        token_response = requests.post(
            token_url,
            headers=headers,
            data=body,
            auth=(GOOGLE_CLIENT_ID,GOOGLE_CLIENT_SECRET)
        )

        client.parse_request_body_response(json.dumps(token_response.json()))
        userinfo_endpoint = google_provider_cfg['userinfo_endpoint']
        uri , headers ,body = client.add_token(userinfo_endpoint)
        userinfo_responce = requests.get(uri,headers=headers , data=body)


        if userinfo_responce.json().get('email_verified'):
            # unique_id = userinfo_responce.json()['sub']
            user_name = userinfo_responce.json()['name']
            users_email = userinfo_responce.json()['email']
        else:
            return 'user email not available or not verified by google' , 400
        
        user = User.query.filter_by(EMAIL=users_email).first()
        hospital_user = HospitalUser.query.filter_by(EMAIL=users_email).first()

        if user and not hospital_user:  

            if user.LOGIN_METHOD == 'google':
                login_user(user)
                return redirect(url_for('user.home'))
            flash("User Exists!!.","warning")
            return redirect(url_for('authentication.user_sign_in'))
        

        if hospital_user :
            flash("User Exists!!.","warning")
            return redirect(url_for('authentication.user_sign_in'))
        
        new_user = User( EMAIL=users_email , LOGIN_METHOD='google') 
        db.session.add(new_user)
        db.session.commit()

        user = User.query.filter_by(EMAIL=users_email).first()                  # Query the User object with the email
        new_user_data = Userdata(user_data=user , USER_NAME=user_name)
        db.session.add(new_user_data)
        db.session.commit()

        send_google_email(user_name , users_email)        # Send a confirmation email to the user

        login_user(user)
        return redirect(url_for('user.home'))


# [ Admin login functionality ]
@bp.route('/admin/login' , methods=['POST' , 'GET'])
@authentication.handle_auth_errors
def admin_login():
    if request.method == 'POST':
        # Get the username and password from the form
        email = request.form.get('email') 
        password = request.form.get('password')

        user = Admin.query.filter_by(EMAIL=email).first()

        # Check if the entered username and password match the expected values
        if user:
            if password == user.PASSWORD:
                login_user(user)
                # flash("login success","success")
                return redirect(url_for('admin.home'))
            flash("Invalid Credentials","danger")
            return redirect(url_for('authentication.admin_login'))
        
        flash("User not found","danger")
        return redirect(url_for('authentication.admin_login'))


    # Return the login template for GET requests
    return render_template('authentication/admin-login.html')


# [ Hospital login functionality ]
@bp.route('/hospital/login' , methods=[ 'GET','POST'])
@authentication.handle_auth_errors
def hospital_login():
        # If the request method is POST, extract the email and password from the request form
        if request.method=='POST': 
        
            email=request.form.get('email')
            password=request.form.get('password')

            # Query the database for a user with the given email
            user=HospitalUser.query.filter_by(EMAIL=email).first()

            # If a user is found, verify the password
            if user:
                # If the password is correct, log the user in and redirect to the dashboard
                if user.check_password(password):
                    login_user(user)
                    # flash('Login Successfull.' , 'success')
                    return redirect(url_for('hospital.hospital_dashboard'))
                flash('Please check your login details and try again.' ,'warning')
                return redirect(url_for('authentication.hospital_login')) 
            # If no user is found, show a warning message
            flash('User not registerd' , 'warning')
            return redirect(url_for('authentication.hospital_login'))

        # If the request method is GET, render the login template
        return render_template('authentication/hospital-login.html')



#  ************************************************ One-Time-Password ************************************************ 

@bp.route('/One-Time Password')
@authentication.handle_auth_errors
@authentication.check_session_timeout               # check whether the session has exceeded the maximum time limit
def one_time_password():
    with current_app.app_context():
        otp_instance = OTP(session['auth_type'] , session['email'] , session.sid)   # Create an instance of the OTP class 

        otp = otp_instance.generate_and_store_otp() # Generate and store OTP using the instance, and get the OTP value
        otp_instance.send_otp(otp)                  # Send OTP using the instance and the OTP value

        flash('OTP sent succesfully ! Check Your Email .' , 'success')
        return redirect(url_for('authentication.sign_in_verification'))


# [ User sign-in functionality ]
@bp.route('/user/sign-in', methods=['GET' , 'POST'])
@authentication.handle_auth_errors
def user_sign_in():
        # If the request method is POST, retrieve the email and password from the form data
    if request.method=='POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # query both User and Credentials tables
        user = User.query.filter_by(EMAIL=email).first()
        hospital_user = HospitalUser.query.filter_by(EMAIL=email).first()

        # If a user with the given email belongs to hospital
        if hospital_user :
            
            flash("Email cannot be used.!! Try another email","warning")
            return redirect(url_for('authentication.user_sign_up'))           
        
        # If a user with the given email exists
        if user and user.LOGIN_METHOD =='manual':

            # Check if the provided password matches the hashed password in the database
            user_credentials = Credentials.query.filter_by(UID=user.UID).first()
            password = check_password_hash(user_credentials.PASSWORD , password)

            # If the password matches, generate a new OTP and send it to the user's email
            if password :

                    session['email']     = email
                    session['auth_type'] = 'sign-in'
                    return redirect(url_for("authentication.one_time_password"))
            
            # If the password doesn't match, show an error message
            flash("Incorrect Password" ,"danger")
            return redirect(url_for('user.user_login'))
        
        if user and user.LOGIN_METHOD =='google':

            flash("User Exists!! . Kindly login through google ","warning")
            return redirect(url_for('authentication.user_sign_up'))
        
        
        # If no user with the given email exists, show an error message
        flash('Email not registered . SignUp First.', "danger")
        return redirect(url_for('authentication.user_sign_in'))

    # If the request method is GET, return the login template
    session.pop('start_time', None)
    return render_template('authentication/user-login.html')



@bp.route('/sign-in/verification' , methods=['GET' , 'POST'])
@authentication.handle_auth_errors
@authentication.check_session_timeout 
def sign_in_verification():

        if request.method == 'POST':
            # Check if the OTP entered by the user matches the generated OTP
            otp = request.form.get('otp')
            email = session['email']

            otp_instance = OTP('sign-in' , email , session.sid)
            is_valid_otp = otp_instance.verify_otp(otp)

            if is_valid_otp:
            
                user = User.query.filter_by(EMAIL=session['email']).first()

                if user and user.LOGIN_METHOD =='manual':
                    for key in ['email', 'auth_type' , 'start_time']:
                        session.pop(key, None)

                    login_user(user)
                    user_data = current_user.USER
                    return redirect(url_for('user.home'))
                    # return redirect(url_for('welcome_page.index'))

            flash('Wrong otp' , 'warning')                                  # debuggig statement 
            return redirect(url_for('authentication.sign_in_verification'))

        # flash('OTP sent succesfully ! Check Your Email .' , 'success')
        return render_template('authentication/user-verification.html')



# [ User sign-up functionality ]
@bp.route('/user/sign-up', methods=['GET' , 'POST'])
@authentication.handle_auth_errors
def user_sign_up():
        
    if request.method=='POST':

        # Extract the user input data from the request form
        user_name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if the email is already registered in the database
        userEmail= User.query.filter_by(EMAIL=email).first()
        hospital_user = HospitalUser.query.filter_by(EMAIL=email).first()

        # If the email is already registered, send a flash message to the user
        if  userEmail and userEmail.LOGIN_METHOD=='google':

            flash("User Exists.!! Kindly login through google ","warning")
            return redirect(url_for('authentication.user_sign_up'))
        
        if  userEmail and userEmail.LOGIN_METHOD=='manual' or hospital_user:
            flash("User Exists.!!","warning")
            return redirect(url_for('authentication.user_sign_up'))

        session['user_name'] = user_name
        session['email']     = email
        session['password']  = password
        session['auth_type'] = 'sign-up'
    
        return redirect(url_for('authentication.one_time_password'))
    

    # If the request method is GET, return the userSignup.html template
    session.pop('start_time', None)
    return render_template('authentication/user-login.html')



# [ Email verification for new user sign up ]
@bp.route('/sign-up/verification' , methods=['GET' , 'POST'])
@authentication.handle_auth_errors
@authentication.check_session_timeout 
def sign_up_verification():
    
    if request.method=='POST':

        # Get the OTP and Password entered by the user
        otp = request.form.get('otp')
        password = session['password']


        # Hash the password entered by the user
        encpassword = generate_password_hash(password , method='sha256')

        # Retrieve the user data stored in session 
        email = session['email']

        # Check if the OTP entered by the user matches the generated OTP
        otp_instance = OTP('sign-up' , email , session.sid)
        is_valid_otp = otp_instance.verify_otp(otp)


        if is_valid_otp:
            
                new_user = User( EMAIL = session['email'], LOGIN_METHOD='manual')  # Create a new user object
                db.session.add(new_user)                                           # Add the user to the database
                db.session.commit()                                                # Commit the changes to the database

                user = User.query.filter_by(EMAIL=email).first()                   # Query the User object with the email
                user_credentials = Credentials(user_credentials=user , PASSWORD=encpassword)
                user_name = Userdata(user_data=user , USER_NAME=session['user_name'])
                db.session.add(user_credentials , user_name)
                db.session.commit()


                send_email(session['user_name'] , email , password)        # Send a confirmation email to the user

                for key in ['email', 'auth_type' , 'start_time' , 'password' , 'user_name']:
                    session.pop(key, None)
                # Log in the user
                login_user(user , remember=False)

                # Display a success message and redirect to the user dashboard
                flash('Congratulations, your account has been successfully created.' , "success")
                return redirect(url_for('user.home'))

        # Display an error message if the OTP entered by the user does not match the generated OTP
        flash("wrong OTP..!   try again." , "danger")
        return redirect(url_for('authentication.sign_up_verification'))
    
    return render_template('authentication/user-verification.html')


# [ Logout Route ]
@bp.route('/logout')
@authentication.handle_auth_errors
@login_required
def logout():

    # Check if cache data is present
    if hasattr(current_user, 'UID'):
        if cache.get(f'user_data_{current_user.UID}'):
            cache.delete(f'user_data_{current_user.UID}')

    # logout the user using the logout_user function from Flask-Login
    logout_user()

    # Remove the data stored in session variables
    session.clear()          # Clear expired session
    session.modified = True  # Notify Flask that session has been modified

    # Display a success message
    # flash('Logout Successfull' , 'success')
    # Redirect the user to the login page
    return redirect(url_for('home.index'))

