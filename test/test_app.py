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
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # In-memory database
        app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing

        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        # Clean up database after each test
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    # Test if the homepage loads correctly
    def test_homepage_loads(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome', response.data)

    # Test if login page loads correctly
    def test_login_page_loads(self):
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login', response.data)

    # Test if register page loads correctly
    def test_register_page_loads(self):
        response = self.client.get('/register')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Register', response.data)

    # Test login with invalid credentials
    def test_invalid_login(self):
        response = self.client.post('/login', data={
            'email': 'wrong@example.com',
            'password': 'wrongpass'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid', response.data)

    # Test that accessing visualise page without login redirects to login
    def test_protected_visualise_requires_login(self):
        response = self.client.get('/visualise', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login', response.data)

    # Helper method to register a user for testing purposes
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

    # Test logout functionality
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

    # Ensure logged-in users can access visualise page
    def test_visualise_access_after_login(self):
        email = self.register_user()
        self.client.post('/login', data={
            'email': email,
            'password': 'Test@1234'
        }, follow_redirects=True)

        response = self.client.get('/visualise', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Visualise', response.data)

    # Test upload avatar requires user to be logged in
    def test_upload_avatar_requires_login(self):
        response = self.client.post('/upload_avatar', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login', response.data)

    # Test forgot password page loading
    def test_forgot_password_page_loads(self):
        response = self.client.get('/forgot-password')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Forgot Password', response.data)

    # Test verify code page redirects if forgot password flow wasn't initiated
    def test_verify_code_requires_forgot_password_flow(self):
        response = self.client.get('/verify-code', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Forgot Password', response.data)

    # Test reset password page redirects if verify code step not completed
    def test_reset_password_requires_verified_session(self):
        response = self.client.get('/reset-password', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Forgot Password', response.data)

    # Test successful password reset flow from forgot password to reset
    def test_successful_reset_password(self):
        email = self.register_user(email="test@example.com")
        self.client.post('/forgot-password', data={'email': email}, follow_redirects=True)

        with app.app_context():
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
    
    def test_user_registration_successful(self):
        # Simulate registering a user
        response = self.client.post('/register', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'Test@1234',
            'confirm_password': 'Test@1234'
        }, follow_redirects=True)

        # Check if the flash message is displayed
        self.assertIn(b'A verification link has been sent to your email (Check Console).', response.data)
        # Check if the redirect happened (to login page)
        self.assertIn(b'Login', response.data)

    def test_invalid_reset_password_code(self):
        # Simulate the forgotten password process
        self.client.post('/forgot-password', data={'email': 'test@example.com'}, follow_redirects=True)

        # Simulate using an invalid or expired reset password code
        response = self.client.post('/verify-code', data={'code': 'invalidcode'}, follow_redirects=True)

        # Check if the flash message for invalid code appears
        self.assertIn(b'Invalid verification code.', response.data)

    def test_logout_redirect(self):
        # Register and log in the user
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

        # Log out the user
        response = self.client.post('/logout', follow_redirects=True)

        # Check if it redirects to the homepage
        self.assertIn(b'Home', response.data)

    def test_upload_page_requires_login(self):
        # Try to access the upload page without being logged in
        response = self.client.get('/upload', follow_redirects=True)

        # Check if it redirects to the login page
        self.assertIn(b'Login', response.data)

    def test_terms_and_conditions_modal(self):
        # Simulate visiting the registration page
        response = self.client.get('/register')

        # Check if the modal for Terms and Conditions is present in the response
        self.assertIn(b'Terms and Conditions', response.data)

    def test_upload_form_submission(self):
        email = self.register_user()
        self.client.post('/login', data={'email': email, 'password': 'Test@1234'}, follow_redirects=True)

        data = {
            'date': '2025-05-15',
            'time': '10:30',
            'gender': 'Female',
            'age': '25',
            'height': '160',
            'weight': '60',
            'activity_type': ['Running'],
            'duration': ['30'],
            'calories_burned': ['200'],
            'emotion': ['Happy'],
            'food_name': ['Oats'],
            'food_quantity': ['1'],
            'food_calories': ['150'],
            'meal_type': ['Breakfast']
        }

        response = self.client.post('/upload', data=data, follow_redirects=True)
        self.assertIn(b'Upload successful', response.data)

    def test_reset_password_mismatch(self):
        email = self.register_user(email="test@example.com")
        self.client.post('/forgot-password', data={'email': email}, follow_redirects=True)

        with app.app_context():
            code = verification_codes[email]['code']

        self.client.post('/verify-code', data={'code': code}, follow_redirects=True)

        response = self.client.post('/reset-password', data={
            'new_password': 'NewPass1234',
            'confirm_password': 'WrongPass999'
        }, follow_redirects=True)

        self.assertIn(b'Passwords do not match', response.data)

    def test_terms_of_service_page_loads(self):
        response = self.client.get('/terms-of-service')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Terms', response.data)

    def test_privacy_policy_page_loads(self):
        response = self.client.get('/privacy-policy')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Privacy', response.data)

    def test_api_fitness_requires_login(self):
        response = self.client.get('/api/visualisation/fitness', follow_redirects=True)
        self.assertIn(b'Login', response.data)  # Should redirect to login

    def test_api_fitness_returns_json_after_login(self):
        email = self.register_user()
        self.client.post('/login', data={'email': email, 'password': 'Test@1234'}, follow_redirects=True)
        response = self.client.get('/api/visualisation/fitness')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
if __name__ == '__main__':
    unittest.main(verbosity=2)