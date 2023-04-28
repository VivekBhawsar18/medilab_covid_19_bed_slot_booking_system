'''This code imports the necessary libraries and creates a blueprint for the user functionality.'''
from Flaskapp.extensions import db
from Flaskapp.models.users import *
from Flaskapp.models.hospital import *
from flask_login import  login_required
from Flaskapp.utils.authentication import authentication
from flask import Blueprint, flash , render_template , request , redirect , url_for
from Flaskapp.utils.email import send_hospital_user_creation_confirmation_email as send_email


# Creating a blueprint object 'bp' to store the user related functionality
bp = Blueprint('admin' , __name__ )


# [ Admin dashboard ]
@bp.route('/dashboard')
@login_required # Check if the user is logged in
def home():
    try:
        return render_template('admin/dashboard.html') # User is logged in, show the dashboard
    except Exception as e:
        return render_template('error/error-404.html' , error=e)


# Services 

# [ Adding new hospital user ]
@bp.route("/add/hospital", methods=['POST' , 'GET'])
@login_required                         
def add_new_hospital():
    try:
        # Check if the request method is POST and the user is logged in with the correct username
        if request.method=='POST':
            
            # Get the form data
            hcode = request.form.get('hcode')
            email = request.form.get('email')
            password = request.form.get('password')
            hcode = hcode.upper()   # Convert the hcode to uppercase

            # Check if the email is already registered in the database
            if authentication.is_email_registered(email):
                flash("Email is already registered","warning")
                return render_template('admin/services/add-hospital.html')
            
            hospital_code = HospitalUser.query.filter_by(HCODE=hcode).first() 

            # If hcode is already taken, show error message and return to the previous page
            if hospital_code :
                flash("Hospital code Exists","warning")
                return render_template('admin/services/add-hospital.html')       

            # Add the new hospital user to the database

            newuser = HospitalUser( HCODE=hcode, EMAIL=email , ROLE='hospital') 
            newuser.set_password(password)        # Hash the password
            db.session.add(newuser)
            db.session.commit()                   # Commit the database transaction

            send_email(hcode , email , password)  # Create and send an email to the new hospital user

            # Show success message and redirect to the previous page
            flash("Mail Sent and Data Inserted Successfully","success")
            return redirect(url_for('admin.hos_user'))

        # Check if the request method is GET
        return render_template('admin/services/add-hospital.html') 
    
    except Exception as e:
        db.session.rollback()
        return render_template('error/error-404.html' , error=e)


# [ This route will query and display Hospital users data  ]
@bp.route('/hospital/data')
@login_required
def hospital_data():
    try:
        # Execute SQL query to select all data from hospitaldata table
        # query = db.engine.execute('SELECT * FROM Hospital')
        query = Hospital.query.all()
        # Render the hospitalData.html template with the results of the query
        return render_template('admin/services/hospital-data.html' , query=list(query))
    except Exception as e:
        return render_template('error/error-404.html' , error=e)


# [ This route will query and display users booking data  ]
@bp.route('/user/bookings')
@login_required
def user_data():
    try:
        # Execute SQL query to select all data from userbookings table
        query = db.engine.execute('SELECT * FROM Userbookings')
        # Render the user-data.html template with the results of the query
        return render_template('admin/services/user-booking-detail.html' , query=list(query))
    except Exception as e:
        return render_template('error/error-404.html' , error=e)


