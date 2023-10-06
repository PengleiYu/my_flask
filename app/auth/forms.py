from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo, ValidationError

from app.models import User


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')


class RegistrationForm(FlaskForm):
    email = StringField('邮箱', validators=[DataRequired(), Length(1, 64), Email()])
    username = StringField('用户名', validators=[
        DataRequired(),
        Regexp('^[a-zA-Z][a-zA-Z0-9_.]*$', message='用户名只能包含字符、数字、点、下划线'),
    ])
    password = StringField('密码', validators=[DataRequired(), EqualTo('password2', '密码必须匹配')])
    password2 = StringField('重复密码', validators=[DataRequired()])
    submit = SubmitField('注册')

    # 必须保持这个方法签名，框架会自动调用
    # validate是标记，后半部分为要验证的字段
    def validate_email(self, email_field: StringField):
        if User.query.filter_by(email=email_field.data).first():
            raise ValidationError('邮箱已被注册')

    def validate_username(self, username_field: StringField):
        if User.query.filter_by(username=username_field.data).first():
            raise ValidationError('用户名已被使用')


class ChangePasswordForm(FlaskForm):
    old_pwd = PasswordField('旧密码', validators=[DataRequired()])  # 这里不自定义校验函数，是因为需要当前user，不适合在这里获取当前user
    pwd = PasswordField('新密码', validators=[DataRequired(), EqualTo('pwd2', message='两次密码必须匹配')])
    pwd2 = PasswordField('确认新密码', validators=[DataRequired()])
    submit = SubmitField('更新密码')


class PasswordResetRequestForm(FlaskForm):
    email = StringField('邮箱', validators=[DataRequired(), Length(1, 64), Email()])
    submit = SubmitField('重置密码')

    def validate_email(self, email_field: StringField):
        user: User = User.query_().filter_by(email=email_field.data).first()
        if user is None:
            raise ValidationError('未找到该邮箱')


class PasswordResetFrom(FlaskForm):
    pwd1 = PasswordField('新密码', validators=[DataRequired(), EqualTo('pwd2', message='两次密码必须匹配')])
    pwd2 = PasswordField('确认新密码', validators=[DataRequired()])
    submit = SubmitField('重置密码')
