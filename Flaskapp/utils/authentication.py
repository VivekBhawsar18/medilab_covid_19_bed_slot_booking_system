import functools
from functools import wraps
from Flaskapp.models.users import *
from Flaskapp.models.hospital import *
from datetime import datetime, timedelta
from flask import render_template, session



class authentication:

    # check_session_timeout decorator will check whether the session has exceeded the maximum time limit
    def check_session_timeout(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Check if session has started
            if 'start_time' not in session:
                session['start_time'] = datetime.now()  # Set session start time
            else:
                # Calculate session duration
                duration = datetime.now() - session['start_time']
                
                # Check if session has exceeded maximum time limit
                if duration > timedelta(seconds=300):
                    session.clear()
                    # Display a popup window with a button to redirect the user to the home page:
                    
                    return """
                    <script>
                    alert("Session expired! Please try again.");
                    window.location.href = "/";
                    </script>
                    """
            
            return func(*args, **kwargs)
        
        return wrapper
    

    def handle_auth_errors(func):
        @functools.wraps(func)
        def handle_errors(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except (AttributeError, KeyError, ValueError) as e:
                db.session.rollback()
                # Remove the data stored in session variables
                session.clear()          # Clear expired session
                session.modified = True  # Notify Flask that session has been modified
                return render_template('error/error-404.html', error=e)
            except Exception as e:
                db.session.rollback()
                session.clear()
                session.modified = True
                # flash('An unexpected error occurred.' , 'danger')
                return render_template('error/error-404.html',error=e)

        return functools.update_wrapper(handle_errors, func)


    def is_email_registered(email):
        patient = User.query.filter_by(EMAIL=email).first()
        hospital_user = HospitalUser.query.filter_by(EMAIL=email).first()
        return patient is not None or hospital_user is not None
