import secrets , os
from config import MailConfig
from flask_mail import Message
from flask import render_template
from Flaskapp.extensions import mail

import redis
redis_instance = redis.Redis.from_url(os.getenv('REDIS_URL'))

# for pythonanywhere
# from redislite import Redis


# redis_instance = Redis('/home/Medilab/covid-19-Bed-Slot-Booking-System/redis.db')


class OTP:
    def __init__(self , type , email, sid) :
        self.email = email
        self.type = type
        self.sid = sid

    def generate_and_store_otp(self):

        otp = "{:06d}".format(secrets.randbelow(10**6))             # Generate a new OTP 
        redis_instance.setex(f'{self.type}:{self.sid}:{self.email}', 300, otp) # save email and otp with unique user session ID in redis
        return otp

    def send_otp(self , otp):

        subject = f'Verify your {self.type} {otp}'
        recipients = [self.email]
        msg = Message(
                    subject, 
                    sender=MailConfig.MAIL_USERNAME, 
                    recipients=recipients
                    )
        msg.html = render_template('email/test-otp.html', email=self.email, otp=otp)
        mail.send(msg)

    def verify_otp(self , otp):
        
        sent_otp = redis_instance.get(f'{self.type}:{self.sid}:{self.email}')

        if sent_otp is not None and otp == sent_otp.decode():
            return True
        return False