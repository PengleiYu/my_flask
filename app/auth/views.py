from datetime import datetime

from flask import render_template, request, url_for, redirect, flash
from flask_login import login_required, login_user, logout_user

from app.models import User
from . import auth
from .forms import LoginForm


@auth.route('/login', methods=['GET', 'POST'])
def login():
    # 根据email查询用户，查到则记录登录状态并重定向到之前页面
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            next_url = request.args.get('next')
            if next_url is None or not next_url.startswith("/"):
                next_url = url_for('main.index')
            return redirect(next_url)
        flash('非法的用户名或密码')
    return render_template('auth/login.html', form=form, current_time=datetime.utcnow())


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('您已登出')
    return redirect(url_for('main.index'))


@auth.route('/secret')
@login_required
def secret():
    return "只有认证用户才能通过"
