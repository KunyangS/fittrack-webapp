import sys
import os
import uuid
import unittest

# Allow imports from parent directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from app.models import db, User
from app.routes import verification_codes, temp_users
from flask import url_for


class HomepageTestCase(unittest.TestCase):

    def setUp(self):
        # Configure Flask app for testing with isolated SQLite DB
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False

        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        # Clean up database after each test
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    # Check if homepage loads with expected content
    def test_homepage_loads(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome', response.data)

    # Check if login page is accessible and loads expected content
    def test_login_page_loads(self):
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login', response.data)

    # Check if register page is accessible and contains expected elements
    def test_register_page_loads(self):
        response = self.client.get('/register')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Register', response.data)

    # Verify login fails with incorrect credentials
    def test_invalid_login(self):
        response = self.client.post('/login', data={
            'email': 'wrong@example.com',
            'password': 'wrongpass'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid', response.data)

    # Ensure protected route redirects unauthenticated users
    def test_protected_visualise_requires_login(self):
        response = self.client.get('/visualise', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login', response.data)

    # Helper to register a test user
    def register_user(self, email=None, password="Test@1234"):
        if email is None:
            email = f"user_{uuid.uuid4().hex[:8]}@example.com"
        user = User(username='testuser', email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return email

    # Test login functionality with valid user
    def test_login_valid_user(self):
        email = self.register_user()
        response = self.client.post('/login', data={
            'email': email,
            'password': 'Test@1234'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Visualise', response.data)

    # Ensure logout works and redirects to login
    def test_logout_works(self):
        email = self.register_user()
        self.client.post('/login', data={
            'email': email,
            'password': 'Test@1234'
        }, follow_redirects=True)
        response = self.client.post('/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login', response.data)
        protected = self.client.get('/visualise', follow_redirects=True)
        self.assertIn(b'Login', protected.data)

    # Verify authenticated users can access visualisation page
    def test_visualise_access_after_login(self):
        email = self.register_user()
        self.client.post('/login', data={'email': email, 'password': 'Test@1234'}, follow_redirects=True)
        response = self.client.get('/visualise', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Visualise', response.data)

    # Ensure avatar upload is restricted to logged-in users
    def test_upload_avatar_requires_login(self):
        response = self.client.post('/upload_avatar', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login', response.data)

    # Check forgot password page loads
    def test_forgot_password_page_loads(self):
        response = self.client.get('/forgot-password')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Forgot Password', response.data)

    # Test verify-code page requires forgot-password session
    def test_verify_code_requires_forgot_password_flow(self):
        response = self.client.get('/verify-code', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Forgot Password', response.data)

    # Ensure reset-password page requires verified session
    def test_reset_password_requires_verified_session(self):
        response = self.client.get('/reset-password', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Forgot Password', response.data)

    # Simulate full password reset flow and verify success
    def test_successful_reset_password(self):
        email = self.register_user(email="test@example.com")
        self.client.post('/forgot-password', data={'email': email}, follow_redirects=True)
        code = verification_codes[email]['code']
        self.client.post('/verify-code', data={'code': code}, follow_redirects=True)
        response = self.client.post('/reset-password', data={
            'new_password': 'NewPass1234',
            'confirm_password': 'NewPass1234'
        }, follow_redirects=True)
        self.assertIn(b'Password Successfully Reset!', response.data)
        login_response = self.client.post('/login', data={
            'email': email,
            'password': 'NewPass1234'
        }, follow_redirects=True)
        self.assertIn(b'Visualise', login_response.data)

    # Simulate user registration and verify success message
    def test_user_registration_successful(self):
        response = self.client.post('/register', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'Test@1234',
            'confirm_password': 'Test@1234'
        }, follow_redirects=True)
        self.assertIn(b'A verification link has been sent to your email', response.data)
        self.assertIn(b'Login', response.data)

    # Simulate reset with invalid verification code
    def test_invalid_reset_password_code(self):
        self.client.post('/forgot-password', data={'email': 'test@example.com'}, follow_redirects=True)
        response = self.client.post('/verify-code', data={'code': 'invalidcode'}, follow_redirects=True)
        self.assertIn(b'Invalid verification code.', response.data)

    # Check logout redirects to homepage and prevents access to protected pages
    def test_logout_redirect(self):
        self.client.post('/register', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'Test@1234',
            'confirm_password': 'Test@1234'
        }, follow_redirects=True)
        self.client.post('/login', data={
            'email': 'test@example.com',
            'password': 'Test@1234'
        }, follow_redirects=True)
        response = self.client.post('/logout', follow_redirects=True)
        self.assertIn(b'Home', response.data)

    # Verify upload page redirects when not logged in
    def test_upload_page_requires_login(self):
        response = self.client.get('/upload', follow_redirects=True)
        self.assertIn(b'Login', response.data)

    # Ensure Terms and Conditions modal is present on registration page
    def test_terms_and_conditions_modal(self):
        response = self.client.get('/register')
        self.assertIn(b'Terms and Conditions', response.data)

    # Ensure mismatched passwords during reset are caught
    def test_reset_password_mismatch(self):
        email = self.register_user(email="test@example.com")
        self.client.post('/forgot-password', data={'email': email}, follow_redirects=True)
        code = verification_codes[email]['code']
        self.client.post('/verify-code', data={'code': code}, follow_redirects=True)
        response = self.client.post('/reset-password', data={
            'new_password': 'NewPass1234',
            'confirm_password': 'WrongPass999'
        }, follow_redirects=True)
        self.assertIn(b'Passwords do not match', response.data)

    # Check that terms of service page loads correctly
    def test_terms_of_service_page_loads(self):
        response = self.client.get('/terms-of-service')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Terms', response.data)

    # Check that privacy policy page loads correctly
    def test_privacy_policy_page_loads(self):
        response = self.client.get('/privacy-policy')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Privacy', response.data)

    # Check that API for fitness visualisation is protected
    def test_api_fitness_requires_login(self):
        response = self.client.get('/api/visualisation/fitness', follow_redirects=True)
        self.assertIn(b'Login', response.data)

    # Ensure authenticated API access returns JSON
    def test_api_fitness_returns_json_after_login(self):
        email = self.register_user()
        self.client.post('/login', data={'email': email, 'password': 'Test@1234'}, follow_redirects=True)
        response = self.client.get('/api/visualisation/fitness')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')

    # Check that invalid email formats are rejected on registration
    def test_registration_invalid_email_format(self):
        response = self.client.post('/register', data={
            'username': 'testuser2',
            'email': 'invalid-email',
            'password': 'Test@1234',
            'confirm_password': 'Test@1234'
        }, follow_redirects=True)
        self.assertIn(b'Enter a valid email address.', response.data)

    # Ensure short passwords are caught by the validator
    def test_registration_short_password(self):
        response = self.client.post('/register', data={
            'username': 'shortpass',
            'email': 'short@example.com',
            'password': '123',
            'confirm_password': '123'
        }, follow_redirects=True)
        self.assertIn(
            b'Password must be at least 8 characters long and include at least one uppercase letter, one digit, and one special character.',
            response.data
        )

    # Verify that a verification code is generated on registration
    def test_verification_code_generated_on_register(self):
        email = 'verifytest@example.com'
        self.client.post('/register', data={
            'username': 'verifyuser',
            'email': email,
            'password': 'Test@1234',
            'confirm_password': 'Test@1234'
        }, follow_redirects=True)
        self.assertIn(email, temp_users)
        self.assertIn('code', temp_users[email])

    # Valid email format
    def test_valid_email_format(self):
        response = self.client.post('/register', data={
        'username': 'validuser',
        'email': 'valid@example.com', # Valid email format
        'password': 'Test@1234',
        'confirm_password': 'Test@1234'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login', response.data)

    #Password strength validation
    def test_password_strength(self):
        response = self.client.post('/register', data={
        'username': 'weakpassuser',
        'email': 'weakpass@example.com',
        'password': '12345',
        'confirm_password': '12345'
        }, follow_redirects=True)
        self.assertIn(b'Password must be at least 8 characters long and include at least one uppercase letter, one digit, and one special character.', response.data)

if __name__ == '__main__':
    unittest.main(verbosity=2)
