from threading import Thread

from flask import Flask, current_app, render_template
from flask_mail import Message

from . import mail


def send_email_impl(app: Flask, msg: Message):
    with app.app_context():
        mail.send(msg)


def send_email(to: str, subject: str, template: str, **kwargs) -> Thread:
    app = current_app._get_current_object()
    msg = Message(subject=app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + subject,
                  sender=app.config['FLASKY_MAIL_SENDER'],
                  recipients=[to])
    msg.body = render_template(template + ".txt", **kwargs)
    msg.html = render_template(template + ".html", **kwargs)
    thr: Thread = Thread(target=send_email_impl, args=[app, msg])
    thr.start()
    return thr
