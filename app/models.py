from flask import current_app

from . import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from itsdangerous import URLSafeTimedSerializer as Serializer, BadSignature, SignatureExpired


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self) -> str:
        return f'<Role {self.name}>'


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    # 设置密码时存储hash值，校验密码时也校验hash
    password_hash = db.Column(db.String(128))
    # 用户邮箱是否已验证
    confirmed = db.Column(db.Boolean, default=False)

    def generate_confirmation_token(self):
        # current_app.secret_key 这个是不是更好
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'confirm': self.id})

    def confirm(self, token: str, max_age_seconds: int = 3600) -> bool:
        try:
            s = Serializer(current_app.config['SECRET_KEY'])
            data = s.loads(token, max_age=max_age_seconds)
        except (BadSignature, SignatureExpired):
            return False

        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)  # 方法内做这种操作似乎不好
        return True

    @property
    def password(self):
        raise AttributeError('password不是可读属性')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self) -> str:
        return f'<User {self.username}>'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
