import os
from datetime import datetime
from threading import Thread

from flask import Flask, make_response, redirect, abort, render_template, session, url_for, flash
from flask_bootstrap import Bootstrap
from flask_mail import Mail, Message
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "db.sqlite3")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

bootstrap = Bootstrap(app)
moment = Moment(app)
db: SQLAlchemy = SQLAlchemy(app)

MAIL_SERVER = os.environ.get('MAIL_SERVER')
MAIL_PORT = os.environ.get('MAIL_PORT')
MAIL_SENDER_USERNAME = os.environ.get('MAIL_USERNAME')
MAIL_SENDER_PASSWORD = os.environ.get('MAIL_PASSWORD')
ADMIN_MAIL = os.environ.get('FLASKY_ADMIN')

app.config.update(dict(
    DEBUG=True,
    MAIL_SERVER=MAIL_SERVER,
    MAIL_PORT=MAIL_PORT,
    MAIL_USERNAME=MAIL_SENDER_USERNAME,
    MAIL_PASSWORD=MAIL_SENDER_PASSWORD,
    MAIL_USE_TLS=True,
    MAIL_USE_SSL=False,
))

app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[Flasky]'
app.config['FLASKY_MAIL_SENDER'] = MAIL_SENDER_USERNAME
app.config['FLASKY_ADMIN'] = ADMIN_MAIL
mail = Mail(app)


def send_email_impl(app: Flask, msg: Message):
    with app.app_context():
        mail.send(msg)


def send_email(to: str, subject: str, template: str, **kwargs) -> Thread:
    msg = Message(subject=app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + subject,
                  sender=app.config['FLASKY_MAIL_SENDER'],
                  recipients=[to])
    msg.body = render_template(template + ".txt", **kwargs)
    msg.html = render_template(template + ".html", **kwargs)
    thr: Thread = Thread(target=send_email_impl, args=[app, msg])
    thr.start()
    return thr


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self) -> str:
        return f'<Role {self.name}>'


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self) -> str:
        return f'<User {self.username}>'


class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    submit = SubmitField('Submit')


@app.route("/", methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        new_name = form.name.data
        if user is None:
            user = User(username=new_name)
            db.session.add(user)
            db.session.commit()
            session['known'] = False
            if app.config.get('FLASKY_ADMIN'):
                send_email(app.config['FLASKY_ADMIN'], 'New User', 'mail/new_user', user=user)
        else:
            session['known'] = True

        session['name'] = new_name
        return redirect(url_for('index'))
    name = session.get('name')
    known = session.get('known', False)
    return render_template("index.html", current_time=datetime.utcnow(),
                           form=form, name=name, known=known)


class FeedbackForm(FlaskForm):
    title = StringField('标题', validators=[DataRequired()])
    content = TextAreaField('内容', validators=[DataRequired()])
    submit = SubmitField('发送')


@app.route('/feedback_to_admin', methods=['GET', 'POST'])
def mail_to_admin():
    form = FeedbackForm()
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        if app.config.get('FLASKY_ADMIN'):
            send_email(app.config['FLASKY_ADMIN'], 'Feedback:' + title, 'mail/feedback_to_admin', content=content)
            flash("反馈已发送")
        return redirect(url_for('mail_to_admin'))

    return render_template('feedback_to_admin.html', current_time=datetime.utcnow(), form=form)


@app.route("/list")
def hello_list():
    _list = ['Hello', 'World', 'Tom', 'Cat']
    return render_template('list.html', commentList=_list)


@app.route("/error")
def error():
    # return "<h1>Bad Request</h1>", 400
    response = make_response('<h1>带cookie的文档</h1>')
    response.set_cookie('answer', '42')
    return response


@app.route('/redirect')
def redirect_page():
    return redirect('https://baidu.com')


@app.route('/abort/<int:code>')
def abort_page(code: int):
    abort(code)
    return '<h1>abort page</h1>'


@app.route('/user/<username>')
def show_user_profile(username: str):
    # return f'User {escape(username)}'
    return render_template('user.html', name=username)


@app.route('/post/<int:post_id>')
def show_post(post_id):
    return f'Post {post_id}'


@app.route('/path/<path:subpath>')
def show_subpath(subpath):
    return f'Subpath {subpath}'
# @app.errorhandler(404)
# def page_not_found(e):
#     return render_template('404.html'), 404
#
#
# @app.errorhandler(500)
# def internal_server_error(e):
#     return render_template('500.html'), 500
