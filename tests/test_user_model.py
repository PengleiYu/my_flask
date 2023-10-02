import time
import unittest
from app.models import User
from app import db


class UserModelTestCase(unittest.TestCase):
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
