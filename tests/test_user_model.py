import time

from app import db
from app.models import User
from test_basics import BasicsTestCase


class UserModelTestCase(BasicsTestCase):
    def test_password_setter(self):
        u = User(password='cat')
        self.assertIsNotNone(u.password_hash)

    def test_password_getter(self):
        u = User(password='cat')
        with self.assertRaises(AttributeError):
            u.password()

    def test_password_verification(self):
        u = User(password='cat')
        self.assertTrue(u.verify_password('cat'))
        self.assertFalse(u.verify_password('dog'))

    def test_password_salts_are_random(self):
        u = User(password='cat')
        u2 = User(password='cat')
        self.assertNotEqual(u.password_hash, u2.password_hash)

    def test_invalidate_confirmation_token(self):
        u = User()
        u2 = User()
        db.session.add_all([u, u2])
        db.session.commit()
        token = u.generate_confirmation_token()
        self.assertTrue(u.confirm(token))
        self.assertFalse(u2.confirm(token))

    def test_expired_confirmation_token(self):
        u = User()
        db.session.add(u)
        token = u.generate_confirmation_token()
        time.sleep(2)
        self.assertFalse(u.confirm(token, max_age_seconds=1))
        self.assertTrue(u.confirm(token, max_age_seconds=3))

    def test_valid_reset_token(self):
        u = User()
        u.password = 'cat'
        db.session.add(u)
        db.session.commit()
        token = u.generate_reset_token()
        self.assertTrue(u.reset_pwd('dog', token))
        self.assertTrue(u.verify_password('dog'))

    def test_invalid_reset_token(self):
        u = User()
        u.password = 'cat'
        db.session.add(u)
        db.session.commit()
        token = u.generate_reset_token()
        self.assertFalse(u.reset_pwd('dog', token + 'a'))
        self.assertTrue(u.verify_password('cat'))

    def test_valid_email_change_token(self):
        """
        合法token正确修改email
        """
        u = User()
        u.email = 'a@qq.com'
        db.session.add(u)
        db.session.commit()
        token = u.generate_email_change_token('b@qq.com')
        self.assertTrue(u.change_email(token))
        self.assertEqual('b@qq.com', u.email)

    def test_invalid_email_change_token(self):
        """
        user1生成的token不能用于其他用户修改邮箱
        """
        u = User()
        u.email = 'a@qq.com'
        u2 = User()
        u2.email = 'b@qq.com'
        db.session.add_all([u, u2])
        db.session.commit()
        token = u.generate_email_change_token('c@qq.com')
        self.assertFalse(u2.change_email(token))
        self.assertEqual('b@qq.com', u2.email)

    def test_duplicate_email_change_token(self):
        """
        user1修改的邮箱不能与其他用户相同
        """
        u = User()
        u.email = 'a@qq.com'
        u2 = User()
        u2.email = 'b@qq.com'
        db.session.add_all([u, u2])
        db.session.commit()
        token = u.generate_email_change_token('b@qq.com')
        self.assertFalse(u.change_email(token))
        self.assertTrue('a@qq.com', u.email)
