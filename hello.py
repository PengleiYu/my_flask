from flask import Flask, request, make_response, redirect, abort, render_template
from markupsafe import escape
from flask_bootstrap import Bootstrap

app = Flask(__name__)
bootstrap = Bootstrap(app)


@app.route("/")
def hello_world():
    # user_agent = request.headers.get('User-Agent')
    # return f'<h1>UA</h1><p>{user_agent}</p>'
    return render_template("index.html")


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
