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
        print(f'field={email_field}')
        if User.query.filter_by(email=email_field.data).first():
            raise ValidationError('邮箱已被注册')

    def validate_username(self, username_field: StringField):
        print(f'field={username_field}')
        if User.query.filter_by(username=username_field.data).first():
            raise ValidationError('用户名已被使用')
