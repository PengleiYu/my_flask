from datetime import datetime

from flask import Flask, make_response, redirect, abort, render_template, session, url_for, flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
bootstrap = Bootstrap(app)
moment = Moment(app)


class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    submit = SubmitField('Submit')


@app.route("/", methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        old_name = session.get('name')
        new_name = form.name.data
        if old_name is not None and old_name != new_name:
            flash('已修改name!')
        session['name'] = new_name
        return redirect(url_for('index'))
    name = session.get('name')
    return render_template("index.html", current_time=datetime.utcnow(), form=form, name=name)


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


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500
