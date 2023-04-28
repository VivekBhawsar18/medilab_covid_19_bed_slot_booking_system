from flask import render_template
from Flaskapp.extensions import mail
from flask_mail import Message
from config import MailConfig



def send_booking_confirmation_email(patient_name, patient_email , hospital_name, patient_bedtype, hospital_code):
    """
    Sends a booking confirmation email to the user.

    """
    # Create a message object to send an email to the user
    msg = Message(
        f'Dear {patient_name} your booking on Medilab is confirmed!',
        sender = MailConfig.MAIL_USERNAME,
        recipients = [patient_email]
    )

    # Set the HTML template for the email
    msg.html = render_template(
        'email/bed-slot-booking.html',
        name=patient_name,
        hospital_name=hospital_name,
        hospital_code=hospital_code ,
        bedtype=patient_bedtype
    )

    # Send the email
    mail.send(msg)



def send_google_user_creation_confirmation_email(user_name, user_email):
    """
    Sends a confirmation email to the user upon successful account creation through google.

    """
    # Create a message object to send an email to the user
    msg = Message(
        f'Congratulations {user_name}, your account on Medilab has been successfully created.',
        sender=MailConfig.MAIL_USERNAME,
        recipients=[user_email]
    )

    msg.html = render_template(
        'email/welcome-user.html',
        name=user_name,
        email=user_email
    )

    # Send the email
    mail.send(msg)



def send_user_creation_confirmation_email(user_name, user_email , user_password):
    """
    Sends a confirmation email to the user upon successful account creation.

    """
    # Create a message object to send an email to the user
    msg = Message(
        f'Congratulations {user_name}, your account on Medilab has been successfully created.',
        sender=MailConfig.MAIL_USERNAME,
        recipients=[user_email]
    )

    msg.html = render_template(
        'email/welcome-user.html',
        name=user_name,
        email=user_email,
        password=user_password
    )

    # Send the email
    mail.send(msg)



def send_hospital_user_creation_confirmation_email(user_hcode, user_email , user_password):
    # Create and send an email to the new hospital user
    msg = Message(
            f' COVID CARE CENTER Congratulation ..! You can now Login on MediLab',
            sender = MailConfig.MAIL_USERNAME,
            recipients = [user_email]
            )

    msg.html = render_template(
        'email/new-hospital-added.html' , 
        hcode=user_hcode , 
        email=user_email , 
        password=user_password 
    )

    mail.send(msg)