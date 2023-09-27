from datetime import datetime

from flask import make_response, redirect, abort, render_template, session, url_for, flash, current_app

from . import main
from .forms import NameForm, FeedbackForm
from .. import db
from ..models import User
from ..email import send_email


@main.route("/", methods=['GET', 'POST'])
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
            if current_app.config.get('FLASKY_ADMIN'):
                send_email(current_app.config['FLASKY_ADMIN'], 'New User', 'mail/new_user', user=user)
        else:
            session['known'] = True

        session['name'] = new_name
        return redirect(url_for('main.index'))
    name = session.get('name')
    known = session.get('known', False)
    return render_template("index.html", current_time=datetime.utcnow(),
                           form=form, name=name, known=known)


@main.route('/feedback_to_admin', methods=['GET', 'POST'])
def mail_to_admin():
    form = FeedbackForm()
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        if current_app.config.get('FLASKY_ADMIN'):
            send_email(current_app.config['FLASKY_ADMIN'], 'Feedback:' + title, 'mail/feedback_to_admin',
                       content=content)
            flash("反馈已发送")
        else:
            flash("警告：未设置管理员")
        return redirect(url_for('main.mail_to_admin'))

    return render_template('feedback_to_admin.html', current_time=datetime.utcnow(), form=form)


@main.route("/list")
def hello_list():
    _list = ['Hello', 'World', 'Tom', 'Cat']
    return render_template('list.html', commentList=_list)


@main.route("/error")
def error():
    # return "<h1>Bad Request</h1>", 400
    response = make_response('<h1>带cookie的文档</h1>')
    response.set_cookie('answer', '42')
    return response


@main.route('/redirect')
def redirect_page():
    return redirect('https://baidu.com')


@main.route('/abort/<int:code>')
def abort_page(code: int):
    abort(code)
    return '<h1>abort page</h1>'


@main.route('/user/<username>')
def show_user_profile(username: str):
    # return f'User {escape(username)}'
    return render_template('user.html', name=username)


@main.route('/post/<int:post_id>')
def show_post(post_id):
    return f'Post {post_id}'


@main.route('/path/<path:subpath>')
def show_subpath(subpath):
    return f'Subpath {subpath}'
