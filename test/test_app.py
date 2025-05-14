import sys
import os
import uuid
import unittest

# Allow imports from parent directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from app.models import db, User  # Assumes db and User are defined in models.py

class HomepageTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db' # In-memory DB for isolated testing
        self.client = app.test_client()
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_homepage_loads(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome', response.data)

    def test_login_page_loads(self):
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login', response.data)

    def test_register_page_loads(self):
        response = self.client.get('/register')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Register', response.data)

    def test_invalid_login(self):
        response = self.client.post('/login', data={
            'email': 'wrong@example.com',
            'password': 'wrongpass'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid', response.data)

    def test_protected_visualise_requires_login(self):
        response = self.client.get('/visualise', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login', response.data)

    def register_user(self, email=None, password="Test@1234"):
        if email is None:
            email = f"user_{uuid.uuid4().hex[:8]}@example.com"

        with app.app_context():
            user = User(
                username='testuser',
                email=email
            )
            user.set_password(password)  # Properly hash the password
            db.session.add(user)
            db.session.commit()
            print(f"[DEBUG] ✅ Inserted and hashed user: {email}")

        return email
    

    def test_login_valid_user(self):
        email = self.register_user()
        response = self.client.post('/login', data={
            'email': email,
            'password': 'Test@1234'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b'Invalid email/username or password', response.data)
        self.assertIn(b'Visualise', response.data)  # or another known post-login keyword


if __name__ == '__main__':
    unittest.main(verbosity=2)
