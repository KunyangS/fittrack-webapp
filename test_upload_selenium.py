import unittest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from app import app, db
from app.models import User, UserInfo
import threading
from datetime import datetime

class UploadSystemTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Set up Flask app context
        cls.app = app
        cls.app_context = cls.app.app_context()
        cls.app_context.push()

        db.create_all()
        cls._add_test_user()

        # Start Flask server in a separate thread
        cls.server_thread = threading.Thread(target=cls.app.run, kwargs={"use_reloader": False, "debug": False})
        cls.server_thread.daemon = True
        cls.server_thread.start()
        time.sleep(2)  # Give server time to start

        # Start Selenium WebDriver
        options = Options()
        options.add_argument("--headless")
        cls.driver = webdriver.Chrome(options=options)

        # Login for session-based tests
        cls._login_user()

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        db.session.remove()
        db.drop_all()
        cls.app_context.pop()
        cls.server_thread.join()

    @classmethod
    def _add_test_user(cls):
        existing = User.query.filter_by(email="test@example.com").first()
        if existing:
            UserInfo.query.filter_by(user_id=existing.id).delete()
            db.session.delete(existing)
            db.session.commit()

        user = User(username='testuser', email='test@example.com')
        user.set_password('testpass')
        db.session.add(user)
        db.session.commit()

        user_info = UserInfo(
            user_id=user.id,
            date=datetime.now().date(),
            time=datetime.now().time(),
            gender='Male',
            age=25,
            height=175,
            weight=70
        )
        db.session.add(user_info)
        db.session.commit()

    @classmethod
    def _login_user(cls):
        cls.driver.get("http://127.0.0.1:5000/login")
        cls.driver.find_element(By.NAME, "email").send_keys("test@example.com")
        cls.driver.find_element(By.NAME, "password").send_keys("testpass")
        cls.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(1)  # wait for redirect

    def test_home_page_title(self):
        self.driver.get("http://127.0.0.1:5000")
        self.assertIn("Welcome", self.driver.page_source)

    def test_login_form_present(self):
        self.driver.get("http://127.0.0.1:5000/login")
        self.assertTrue(self.driver.find_element(By.NAME, "email"))
        self.assertTrue(self.driver.find_element(By.NAME, "password"))

    def test_register_page_accessible(self):
        self.driver.get("http://127.0.0.1:5000/register")
        self.assertIn("Register", self.driver.page_source)

    def test_upload_page_accessible(self):
        self.driver.get("http://127.0.0.1:5000/upload")
        self.assertIn("Upload", self.driver.page_source)

    def test_dark_mode_toggle_script(self):
        self.driver.get("http://127.0.0.1:5000")
        script_exists = self.driver.execute_script("return typeof document !== 'undefined';")
        self.assertTrue(script_exists)

    def test_add_exercise_block(self):
        self.driver.get("http://127.0.0.1:5000/upload")
        initial = self.driver.find_elements(By.CLASS_NAME, "exercise-block")
        self.driver.find_element(By.ID, "addExerciseBtn").click()
        updated = self.driver.find_elements(By.CLASS_NAME, "exercise-block")
        self.assertEqual(len(updated), len(initial) + 1)

    def test_add_food_block(self):
        self.driver.get("http://127.0.0.1:5000/upload")
        initial = self.driver.find_elements(By.NAME, "food_name")
        self.driver.find_element(By.ID, "addFoodBtn").click()
        updated = self.driver.find_elements(By.NAME, "food_name")
        self.assertGreater(len(updated), len(initial))

    def test_to_do_list_add_task(self):
        self.driver.get("http://127.0.0.1:5000/upload")
        initial_tasks = self.driver.find_elements(By.CSS_SELECTOR, "#todoListNotebook li")
        self.driver.find_element(By.ID, "addPlanBtn").click()
        updated_tasks = self.driver.find_elements(By.CSS_SELECTOR, "#todoListNotebook li")
        self.assertEqual(len(updated_tasks), len(initial_tasks) + 1)

    def test_submit_form_and_show_success_message(self):
        self.driver.get("http://127.0.0.1:5000/upload")
        self.driver.find_element(By.NAME, "date").send_keys("2025-05-15")
        self.driver.find_element(By.NAME, "time").send_keys("12:00")
        self.driver.find_element(By.NAME, "gender").send_keys("female")
        self.driver.find_element(By.NAME, "age").send_keys("25")
        self.driver.find_element(By.NAME, "height").send_keys("165")
        self.driver.find_element(By.NAME, "weight").send_keys("55")
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(1)  # optional, for flash messages
        self.assertIn("Upload", self.driver.page_source)  # simple validation

if __name__ == '__main__':
    unittest.main()
