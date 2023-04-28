'''This code imports the necessary libraries and creates a blueprint for the user functionality.'''
from Flaskapp.extensions import db
from Flaskapp.models.hospital import *
from flask_login import login_required , current_user
from flask import Blueprint, flash , render_template , request , redirect , url_for


# Creating a blueprint object 'bp' to store the user related functionality
bp = Blueprint('hospital' , __name__ )


#Hospital dashboard Page
@bp.route('/dashboard' , methods=['GET' , 'POST'])
@login_required # This decorator ensures that the user must be logged in to access this route. 
def hospital_dashboard():
    try:

        # Retrieve the first record of Hospital model from database matching current user's HCODE.
        hospital_data = Hospital.query.filter_by(HCODE=current_user.HCODE).first()

        # check if the request method is 'POST'
        if request.method=='POST':              
                # get the values of hcode, hname, nbed, hbed, ibed, and vbed from the form
                hcode=request.form.get('hcode')
                hname=request.form.get('hname')
                nbed=request.form.get('normalbed')
                hbed=request.form.get('hicubeds')
                ibed=request.form.get('icubeds')
                vbed=request.form.get('ventbeds')


                # if the hospital data is already present
                if hospital_data:
                    flash("Data is already Present you can update it..","primary")
                    return render_template("hospital/dashboard.html" , hospital_data=hospital_data)


                # get the first instance of the hospital user with the given hospital code
                hospital_user = HospitalUser.query.filter_by( HCODE = hcode ).first()

                # if the hospital user is present
                if hospital_user:
                    # create a new instance of the Hospitaldata model with the given parameters
                    new_user = Hospital( huser=hospital_user , HOSPITAL_NAME=hname, NORMAL_BEDS=nbed , HIGH_CARE_UNIT_BEDS=hbed , ICU_BEDS=ibed , VENTILATOR_BEDS=vbed )

                    db.session.add(new_user)      # add the new data to the database 
                    db.session.commit()           # commit the changes to the database

                    flash("Data Is Added","success")
                    return redirect(url_for('hospital.hospital_dashboard'))  # redirect the user to the hospital dashboard
                
        
        return render_template('hospital/dashboard.html' , hospital_data=hospital_data ) # render the dashboard template and pass in the hospital_data
    
    except Exception as e:
        db.session.rollback()
        return render_template('error/error-404.html' , error=e)


# Hospital data update
@bp.route('/update/<string:id>' , methods=['GET' ,'POST']) # Flask route at '/update/<string:id>' where id is a string parameter. 
@login_required
def hospital_data_update(id):
    try:

        # Retrieve the data of the hospital with the given id
        hospital_data=Hospital.query.filter_by(ID=id).first() 

        # Check if the request method is POST
        if request.method=="POST":

            # Get the updated data from the form
            hname=request.form.get('hname')
            nbed=request.form.get('normalbed')
            hbed=request.form.get('hicubeds')
            ibed=request.form.get('icubeds')
            vbed=request.form.get('ventbeds')

            # Update the database with the updated data
            hospital_data.HOSPITAL_NAME = hname
            hospital_data.NORMAL_BEDS = nbed
            hospital_data.HIGH_CARE_UNIT_BEDS = hbed
            hospital_data.ICU_BEDS = ibed
            hospital_data.VENTILATOR_BEDS = vbed
                
            db.session.commit()

            # Display a success message and redirect to the hospital dashboard
            flash("Slot Updated","success")
            return redirect(url_for('hospital.hospital_dashboard'))

        # If the request method is GET, render the template for updating the data
        return render_template('hospital/data-update.html' , hospital_data=hospital_data)
    
    except Exception as e:
        db.session.rollback()
        return render_template('error/error-404.html' , error=e)


# Hospital data delete
# # This code sets up a Flask route that deletes a record in the database associated with a given id. 
@bp.route('/delete/<string:id>') 
@login_required  
def hospital_data_delete(id): # The function takes the id as a parameter and is responsible for deleting the data from the database.
    try:
        Hospital.query.filter_by(ID=id).delete()  
        db.session.commit()
        flash("Data Deleted Succesfully" , "success")
        return redirect(url_for('hospital.hospital_dashboard'))
    except Exception as e:
        db.session.rollback()
        return render_template('error/error-404.html' , error=e)
