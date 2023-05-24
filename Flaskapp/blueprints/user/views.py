from Flaskapp import cache
from Flaskapp.models.users import *
from Flaskapp.models.hospital import *
from Flaskapp.extensions import db 
from flask_login import  login_required, current_user
from Flaskapp.utils.email import send_booking_confirmation_email as booking_email
from flask import Blueprint, flash , render_template , request , redirect, session , url_for 


# Creating a blueprint object 'bp' to store the user related functionality
bp = Blueprint('user' , __name__ )


@bp.before_request
def load_user_data():
    try:
        if current_user.is_authenticated:
            user_data = cache.get(f'user_data_{current_user.UID}')
            if not user_data:
                user_data = Userdata.query.filter_by(UID=current_user.UID).first()
                cache.set(f'user_data_{current_user.UID}', user_data)
            current_user.user_data = user_data
    except Exception as e:
        return render_template('error/error-404.html' , error=e)

# [ User dashboard route ]
@bp.route('/home')
@login_required
def home():
    try:
        return render_template('user/dashboard.html')
    except Exception as e:
        return render_template('error/error-404.html' , error=e)


def update_user_details(data, user_name, gender, contact, address):
    try:
        """
        Updates the user details in the database
        """
        data.USER_NAME = user_name
        data.GENDER = gender
        data.CONTACT = contact
        data.ADDRESS = address

        db.session.commit()

        cache.delete(f'user_data_{current_user.UID}')

        flash('Account details updated successfully.' , 'primary')
        # return render_template("user/services/account.html")
        return redirect(url_for('user.user_account'))
    
    except Exception as e:
        db.session.rollback()
        return render_template('error/error-404.html' , error=e)


# [ User account page ]
@bp.route("/account")
@login_required
def user_account():
    try:
        return render_template("user/services/account.html")
    except Exception as e:
        return render_template('error/error-404.html' , error=e)



# [ User update account page ]
@bp.route("/account/update",methods=['GET' , 'POST'])
@login_required
def user_account_update():
    try:
        if request.method == 'POST':

            # Get the form data
            form_name  = request.form.get('name')
            form_gender  = request.form.get('gender')
            form_contact  = request.form.get('contact')
            form_address  = request.form.get('address')

            # Convert name to uppercase
            form_name = form_name.upper()

            # Check if the contact already exists
            existing_contact = Userdata.query.filter_by(CONTACT=form_contact).first()

            # data = Userdata.query.join(User).filter_by(EMAIL=current_user.EMAIL).first()
            data = Userdata.query.filter_by(UID=current_user.UID).first()

            # Check if the contact belongs to the current user
            if not existing_contact or existing_contact and existing_contact.CONTACT == current_user.user_data.CONTACT : 
                
                # Update the user details if the contact does not already exists
                update_user_details(data, form_name, form_gender, form_contact, form_address)
                # flash('Account details updated successfully.' , 'primary')
                return redirect(url_for('user.user_account'))

            flash('Contact No. is already registered' , 'warning')
              return redirect(url_for('user.user_account_update'))

        return render_template("user/services/update-account.html")
    except Exception as e:
        db.session.rollback()
        return render_template('error/error-404.html' , error=e)



# This line defines a route for the URL '/slotbooking' and specifies that it can handle both GET and POST requests.
@bp.route('/bedslot/booking', methods=['GET' , 'POST'])
# This line specifies that the user must be logged in to access this route.
@login_required
def bed_slot_booking():
    try:
        # This line fetches all records from the 'hospitaldata' table and stores it in the 'query' variable.
        query = Hospital.query.all()

        # If the request method is POST, the form data is processed.
        if request.method=="POST":
            
            # The form data is retrieved and stored in variables.
            email=request.form.get('email')
            hcode=request.form.get('hcode')
            bedtype=request.form.get('bedtype')
            spo2=request.form.get('spo2')
            pname=request.form.get('pname')
            pphone=request.form.get('pphone')

            pname = pname.upper()
            
            # These lines check if the email or phone number has already been used to book a slot
            checkbooking = Userbookings.query.join(User).filter_by(EMAIL=email).first()
            checkContact = Userbookings.query.filter_by(PATIENT_CONTACT=pphone).first()

            # If the email has already been used, a warning message is displayed and the user is redirected to the bed slot booking page.
            if checkbooking:
                flash(" Booking exists ","warning")
                return redirect(url_for('user.bed_slot_booking'))
            
            # If the phone number has already been used, a warning message is displayed and the user is redirected to the bed slot booking page.
            if checkContact:
                flash(" Contact No. exists ","warning")
                return redirect(url_for('user.bed_slot_booking'))           
            
            # The hospital code is stored in the 'code' variable.
            code=hcode

            # The data for the hospital with the specified code is fetched from the 'hospitaldata' table.
            dbb=db.engine.execute(f"SELECT * FROM `Hospital` WHERE `Hospital`.`HCODE`='{code}' ")         
            bedtype=bedtype

            # The bed type and the number of available beds (seat) are stored in variables.
            seat = 0

            # Decrement the number of available beds of the selected type in the hospital with the given code
            if bedtype=="NormalBed":
                for d in dbb:
                    seat=d.NORMAL_BEDS
                    ar=Hospital.query.filter_by(HCODE=code).first()
                    ar.NORMAL_BEDS=seat-1

                    
            elif bedtype=="HICUBed":      
                for d in dbb:
                    seat=d.HIGH_CARE_UNIT_BEDS
                    ar=Hospital.query.filter_by(HCODE=code).first()
                    ar.HIGH_CARE_UNIT_BEDS=seat-1


            elif bedtype=="ICUBed":     
                for d in dbb:
                    seat=d.ICU_BEDS
                    ar=Hospital.query.filter_by(HCODE=code).first()
                    ar.ICU_BEDS=seat-1

            elif bedtype=="VENTILATORBed": 
                for d in dbb:
                    seat=d.VENTILATOR_BEDS
                    ar=Hospital.query.filter_by(HCODE=code).first()
                    ar.VENTILATOR_BEDS=seat-1

            else:
                pass
            
            # If there is at least one bed of the selected type available in the hospital, book the slot
            if seat>=1:

                # Check if there is a hospital with the given hcode
                check=Hospital.query.filter_by(HCODE=hcode).first()

                # If there is a hospital with the given hcode
                if check!=None:

                        # Create a new entry in the Userbookings table with the given data
                        user = User.query.filter_by(EMAIL=email).first()
                        res=Userbookings(user_booking=user,BED_TYPE=bedtype,HCODE=hcode , HOSPITAL_NAME=check.HOSPITAL_NAME,OXYGEN_LEVEL=spo2,PATIENT_NAME=pname,PATIENT_CONTACT=pphone)
                        db.session.add(res)

                        # Commit the changes to the database
                        db.session.commit()

                        booking_email(pname , email , check.HOSPITAL_NAME , bedtype , hcode) # Create a message object and send an email to the user
                        
                        # Display a success message
                        flash("Slot is Booked kindly Visit Hospital for Further Procedure","success")
                        # Redirect to the bed_slot page
                        return redirect(url_for('user.bed_slot_booking'))
                else:
                        # Display an error message if the hcode is not valid
                        flash("Give the proper hospital Code","info")
                        # Redirect to the bed_slot page
                        return redirect(url_for('user.bed_slot_booking'))
                
            # Display a warning message if the bedtype is not available in the given hospital
            flash(f'{bedtype} is not available in {d.HOSPITAL_NAME}' , 'warning')
            # Redirect to the bed_slot page
            return redirect(url_for('user.bed_slot_booking'))
        
        # Render the services/bedSlotbooking.html template with the list of hospitals
        return render_template('user/services/bed-slot-booking.html', query=list(query))
    except Exception as e:
        db.session.rollback()
        return render_template('error/error-404.html' , error=e)



# [ This router will render user's bed-slot booking page ]
@bp.route("/bedslot-booking/details")
@login_required
def user_booking():
    try:
        # Get the user's booking information based on their email
        data = Userbookings.query.filter_by(UID=current_user.UID).first()

        # Show a success message that the user can now update their booking details
        # flash('You can now update your booking details.' , 'success')
        return render_template("user/services/booking.html",data=data)
    except Exception as e:
        db.session.rollback()
        return render_template('error/error-404.html' , error=e)



# [ Update user's bed-slot booking route ]
@bp.route("/bedslot-booking/update",methods=['GET' , 'POST'])
@login_required
def user_booking_update():
    try:
        # retrieve the user booking data based on the email
        data = Userbookings.query.filter_by(UID=current_user.UID).first()

        # if the request method is POST
        if request.method == 'POST':

            # get the form data
            name = request.form.get('name')
            contact =  request.form.get('contact')
            oxygen = request.form.get('oxygen')
            name = name.upper()

            # get the user booking data based on the email
            data = Userbookings.query.filter_by(UID=current_user.UID).first()
            # check if the contact number is already registered
            existing_contact = Userbookings.query.filter_by(PATIENT_CONTACT=contact).first()

            # if the contact number is already registered for the same user
            if not existing_contact or existing_contact and existing_contact.PATIENT_CONTACT == data.PATIENT_CONTACT:
                    
                    # update the user booking data
                    data.PATIENT_NAME = name
                    data.PATIENT_CONTACT = contact
                    data.OXYGEN_LEVEL = oxygen

                    db.session.commit()      # commit the changes to the database

                    flash('Booking details updated successfully.' , 'primary') # show a success message
                    
                    return redirect(url_for('user.user_booking'))   # redirect the user to the booking page
                
            
            flash('Contact No. is already registered' , 'warning')   # if the contact number is registered for a different user
            return render_template("user/services/update-booking.html",data=data)

        # render the booking template with the data and hospital name
        return render_template("user/services/update-booking.html",data=data)
    except Exception as e:
        db.session.rollback()
        return render_template('error/error-404.html' , error=e)



# [ Delete user's bed-slot booking route ]
@bp.route('/delete')
@login_required
def user_booking_delete():
    try:
        # Get the Userbookings data based on email
        data = Userbookings.query.filter_by(UID=current_user.UID).first()

        # Get the hcode and bedtype from the Userbookings data
        hcode = data.HCODE
        bedtype = data.BED_TYPE

        # Get the hospital data based on the hcode
        hospital = Hospital.query.filter_by(HCODE=hcode).first()
        seat = 0

        # Increment the number of available beds in the hospital based on the bedtype
        if bedtype=='NormalBed':
            seat = hospital.NORMAL_BEDS
            hospital.NORMAL_BEDS = seat+1

        if bedtype=='HICUBed':
            seat = hospital.HIGH_CARE_UNIT_BEDS
            hospital.HIGH_CARE_UNIT_BEDS = seat+1

        if bedtype=='ICUBed':
            seat = hospital.ICU_BEDS
            hospital.ICU_BEDS = seat+1

        if bedtype=='VENTILATORBed':
            seat = hospital.VENTILATOR_BEDS
            hospital.VENTILATOR_BEDS = seat+1
        else :
            pass
        
        Userbookings.query.filter_by(UID=current_user.UID).delete() # Delete the Userbookings data based on the email
        db.session.commit()                                         # Commit the changes to the database

        flash("Data Deleted Succesfully" , "danger")
        return redirect(url_for('user.user_booking'))
    
    except Exception as e:
        db.session.rollback()
        return render_template('error/error-404.html' , error=e)






