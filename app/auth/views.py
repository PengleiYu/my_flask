from datetime import datetime

from flask import render_template
from flask_login import login_required

from . import auth
from .forms import LoginForm


@auth.route('/login')
def login():
    form = LoginForm()
    return render_template('auth/login.html', form=form, current_time=datetime.utcnow())


@auth.route('/secret')
@login_required
def secret():
    return "只有认证用户才能通过"
