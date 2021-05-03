import smtplib, ssl

from todo_service_api.extensions import celery
from todo_service_api.extensions import db
from todo_service_api.models import User
from todo_service_api.config import (
    MAIL_USERNAME,
    MAIL_PASSWORD,
    MAIL_SERVER,
    MAIL_PORT
)



@celery.task
def send_email_all_user(msg):
    emails = list(map(lambda x: x[0], db.session.query(User.email).all()))
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(MAIL_SERVER, MAIL_PORT, context=context) as server:
        server.login(MAIL_USERNAME, MAIL_PASSWORD)
        server.sendmail(MAIL_USERNAME, emails, msg.encode('utf-8'))
    return "OK"

@celery.task
def send_email(msg, email):
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(MAIL_SERVER, MAIL_PORT, context=context) as server:
        server.login(MAIL_USERNAME, MAIL_PASSWORD)
        server.sendmail(MAIL_USERNAME, [email, ], msg=msg.encode('utf-8'))
    return "OK"
