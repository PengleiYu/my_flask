from flask import Flask
from markupsafe import escape

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "<h1>Hello, world</h1>"


@app.route('/user/<username>')
def show_user_profile(username):
    return f'User {escape(username)}'


@app.route('/post/<int:post_id>')
def show_post(post_id):
    return f'Post {post_id}'


@app.route('/path/<path:subpath>')
def show_subpath(subpath):
    return f'Subpath {subpath}'
