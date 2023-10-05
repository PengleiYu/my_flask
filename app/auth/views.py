from datetime import datetime

from flask import render_template, request, url_for, redirect, flash
from flask_login import login_required, login_user, logout_user, current_user

from app import db
from app.email import send_email
from app.models import User
from . import auth
from .forms import LoginForm, RegistrationForm, ChangePasswordForm, PasswordResetRequestForm, PasswordResetFrom


# 全局拦截
@auth.before_app_request
def before_request():
    user: User = current_user
    if user.is_authenticated \
            and not user.confirmed \
            and request.endpoint \
            and request.blueprint != 'auth' \
            and request.endpoint != 'static':
        return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
    user: User = current_user
    if user.is_anonymous or user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html', user=user, current_time=datetime.utcnow())


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


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User()
        user.email = form.email.data
        user.username = form.username.data
        user.password = form.password.data
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, '确认邮件地址', 'auth/email/confirm', user=user, token=token)
        flash('确认邮件已经发送到你的邮箱')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form, current_time=datetime.utcnow())


@auth.route('/confirm/<token>')
@login_required
def confirm(token: str):
    # 前置要求登录，所以一定不是匿名用户
    user: User = current_user
    if user.confirmed:
        return redirect(url_for('main.index'))
    if user.confirm(token):
        user.confirmed = True
        db.session.commit()
        flash('你已验证邮箱')
    else:
        flash('验证链接是非法的或已失效')
    return redirect(url_for('main.index'))


@auth.route('/confirm')
@login_required
def resend_confirm():
    user: User = current_user
    token = user.generate_confirmation_token()
    send_email(user.email, '确认邮件地址', 'auth/email/confirm', user=user, token=token)
    flash('新的确认邮件已经发送到你的邮箱')
    return redirect(url_for('main.index'))


@auth.route('/change_password', methods=['GET', 'POST'])
def change_pwd():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        user: User = current_user
        if user.verify_password(form.old_pwd.data):
            user.password = form.pwd.data
            db.session.add(user)
            db.session.commit()
            flash('您的密码已修改')
            return redirect(url_for('main.index'))
        else:
            flash('密码不正确')
    return render_template('auth/change_pwd.html', form=form, current_time=datetime.utcnow())


@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    # 非匿名用户跳转首页
    cur_user: User = current_user
    if not cur_user.is_anonymous:
        return redirect(url_for('main.index'))
    # 表单合法则发送邮件，并跳转登录页
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user: User = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_token()
            send_email(user.email, '重置密码', 'auth/email/reset_password', user=User, token=token)
            flash('重置密码的邮件已发送到您的邮箱')
            return redirect(url_for('auth.login'))
        else:
            flash('未找到该邮箱')
    # 默认渲染重置密码页面
    return render_template('auth/reset_password.html', form=form, current_time=datetime.utcnow())


@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token: str):
    # 非匿名用户，跳转首页
    cur_user: User = current_user
    if not cur_user.is_anonymous:
        return redirect(url_for('main.index'))
    # 校验通过则更新密码，并跳转登录页
    form = PasswordResetFrom()
    if form.validate_on_submit():
        if User.reset_pwd(form.pwd1.data, token):
            db.session.commit()
            flash('您的密码已更新')
            return redirect(url_for('auth.login'))
        else:
            flash('重置链接是非法的或已时效')
    # 默认渲染重置密码页
    return render_template('auth/reset_password.html', form=form, current_time=datetime.utcnow())


@auth.route('/secret')
@login_required
def secret():
    return "只有认证用户才能通过"
