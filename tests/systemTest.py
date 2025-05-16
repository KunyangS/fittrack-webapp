import unittest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class SystemTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Set up Chrome options for headless testing
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        cls.driver = webdriver.Chrome(options=chrome_options)
        cls.base_url = 'http://127.0.0.1:5000'  # Make sure your server is running here

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    def test_1_register_and_login(self):
        # Test user registration and subsequent login.
        driver = self.driver
        # Navigate to registration page
        driver.get(f'{self.base_url}/register')
        time.sleep(1)
        # Fill in registration form
        driver.find_element(By.NAME, 'username').send_keys('systemuser')
        driver.find_element(By.NAME, 'email').send_keys('systemuser@example.com')
        driver.find_element(By.NAME, 'password').send_keys('Test@1234')
        driver.find_element(By.NAME, 'confirm_password').send_keys('Test@1234')
        driver.find_element(By.ID, 'terms').click()
        # Submit registration form
        driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()
        time.sleep(1)
        # Assert that registration redirects to login page
        self.assertIn('Login', driver.page_source)

        # Simulate email verification (bypass if not required)
        # Navigate to login page
        driver.get(f'{self.base_url}/login')
        # Fill in login form
        driver.find_element(By.NAME, 'email').send_keys('systemuser@example.com')
        driver.find_element(By.NAME, 'password').send_keys('Test@1234')
        # Submit login form
        driver.find_element(By.XPATH, "//button[contains(text(),'Login')]").click()
        time.sleep(1)
        # Assert that login is successful and redirects to a page containing 'Visualise'
        self.assertIn('Visualise', driver.page_source)

    def test_2_protected_route_requires_login(self):
        # Test that accessing a protected route (/visualise) without login redirects to the login page.
        driver = self.driver
        # Log out first
        driver.get(f'{self.base_url}/logout')
        time.sleep(1)
        # Attempt to access protected route
        driver.get(f'{self.base_url}/visualise')
        time.sleep(1)
        # Assert that user is redirected to login page
        self.assertIn('Login', driver.page_source)

    def test_3_upload_requires_login(self):
        # Test that accessing the upload page (/upload) without login redirects to the login page.
        driver = self.driver
        # Log out first
        driver.get(f'{self.base_url}/logout')
        time.sleep(1)
        # Attempt to access upload page
        driver.get(f'{self.base_url}/upload')
        time.sleep(1)
        # Assert that user is redirected to login page
        self.assertIn('Login', driver.page_source)

    def test_4_password_reset_flow(self):
        # Test the password reset flow.
        driver = self.driver
        # Navigate to forgot password page
        driver.get(f'{self.base_url}/forgot-password')
        time.sleep(1)
        # Enter email to send reset code
        driver.find_element(By.NAME, 'email').send_keys('systemuser@example.com')
        driver.find_element(By.XPATH, "//button[contains(text(),'Send Code')]").click()
        time.sleep(2)
        # Simulate code retrieval (in real test, fetch from backend or email mock)
        # For now, just check that the next page loads (verification page)
        self.assertIn('Verification', driver.page_source)

    def test_5_share_requires_login(self):
        # Test that accessing the share page (/share) without login redirects to the login page.
        driver = self.driver
        # Ensure the user is logged out
        driver.get(f'{self.base_url}/logout')
        time.sleep(1)
        # Access the protected /share page
        driver.get(f'{self.base_url}/share')
        time.sleep(1)
        # Should be redirected to the login page
        self.assertIn('Login', driver.page_source)

    def test_6_invalid_login_shows_error(self):
        # Test that an invalid login attempt (e.g., wrong password) displays an error message.
        driver = self.driver
        # Ensure the user is logged out
        driver.get(f'{self.base_url}/logout')
        time.sleep(1)
        # Attempt to login with an incorrect password
        driver.get(f'{self.base_url}/login')
        driver.find_element(By.NAME, 'email').clear()
        driver.find_element(By.NAME, 'email').send_keys('systemuser@example.com')
        driver.find_element(By.NAME, 'password').clear()
        driver.find_element(By.NAME, 'password').send_keys('WrongPassword1!')
        driver.find_element(By.XPATH, "//button[contains(text(),'Login')]").click()
        time.sleep(1)
        # The page should display a login failure message (e.g., containing 'invalid')
        self.assertTrue('invalid' in driver.page_source.lower())

if __name__ == '__main__':
    unittest.main(verbosity=2)
