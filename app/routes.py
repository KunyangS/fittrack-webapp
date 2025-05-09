# routes.py
from datetime import datetime, timedelta

from app import app, db, login_manager
from flask import render_template, request, session, redirect, url_for, flash
import random
from urllib.parse import urlencode
from app.models import User, UserInfo, ShareEntry, FitnessEntry, FoodEntry
from app.forms import RegistrationForm
import re

# Database helpers
from app.database import (
    login_user as db_login_user, 
    register_user as db_register_user, 
    find_user_by_email, 
    find_user_by_username, 
    reset_password as db_reset_password,
    create_share_entry,
    get_shares_by_sharer,
    revoke_share_entry,
    get_share_entry_by_id,
    get_user_activity_data
)

# Flask-Login helpers
from flask_login import login_user as flask_login_user, logout_user, login_required, current_user

# Temporary in-memory user storage
temp_users = {}  # Temporary unverified users
verification_codes = {}  # Temporary in-memory store for verification codes

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Route for the Introduction/Home page
@app.route('/')
def index():
    """Renders the introduction page."""
    return render_template('index.html', title='Welcome') # Pass title variable

# Route for Data Visualisation page (placeholder)
@app.route('/visualise')
@login_required
def visualise():
    return render_template('visualise.html', username=current_user.username)

# Route for Data Sharing page (placeholder)
@app.route('/share')
@login_required
def share():
    return render_template('share.html', username=current_user.username)

# --- 🛠 UPDATED LOGIN route ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('upload')) # Or wherever you want logged-in users to go

    if request.method == 'POST':
        input_value = request.form.get('email')  # Can be email or username
        password = request.form.get('password')

        user = db_login_user(input_value, password) # Use database function

        if user:
            flask_login_user(user) # Use Flask-Login to handle the session
            next_page = request.args.get('next')
            return redirect(next_page or url_for('upload'))
        else:
            flash("❌ Invalid email/username or password.", "danger")
            return redirect(url_for('login'))

    return render_template('login.html', title='Login')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if request.method == 'POST':
        if not form.validate_on_submit():
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f"❌ {error}", "danger")
            return redirect('/register')

        username = form.username.data
        email = form.email.data
        password = form.password.data

        code = str(random.randint(100000, 999999))
        temp_users[email] = {
            'username': username,
            'password': password,
            'code': code
        }
        verification_link = url_for('verify_email', email=email, code=code, _external=True)
        print("DEBUG: Registration passed validation, about to print verification link")
        print(f"🔔 Verification Link for {email}: {verification_link}")

        flash("A verification link has been sent to your email (Check Console).", "info")
        return redirect('/login')
    return render_template('register.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect('/login')

@app.route('/verify-email')
def verify_email():
    email = request.args.get('email')
    code = request.args.get('code')

    if not email or not code:
        flash('❌ Invalid verification link.', 'danger')
        return redirect(url_for('login'))

    user_data = temp_users.get(email)
    if user_data and user_data['code'] == code:
        registered_user = db_register_user(
            username=user_data['username'],
            email=email,
            password=user_data['password'],
            gender=None,
            age=None,
            height=None,
            weight=None
        )
        if registered_user:
            temp_users.pop(email, None)
            flash('✅ Email verified successfully! Please login.', 'success')
        else:
            flash('❌ Registration failed. Username or email may already exist, or an error occurred.', 'danger')
        return redirect(url_for('login'))
    else:
        flash('❌ Verification failed. Invalid or expired link.', 'danger')
        return redirect(url_for('login'))

# ✅ New UPLOAD Page after successful login
@app.route('/upload')
@login_required
def upload():
    return render_template('upload.html', username=current_user.username)

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        if email:
            code = str(random.randint(100000, 999999))
            verification_codes[email] = {
                'code': code,
                'timestamp': datetime.now()
            }
            session['reset_email'] = email
            print(f"🔐 Verification code for {email}: {code}")
            flash("Verification code sent to your email. (Check console)", "info")
            return redirect(url_for('verify_code'))
    return render_template('forgot_password.html', title='Forgot Password')

# ✅ FIXED: verify_code route now includes 2-minute expiry check
@app.route('/verify-code', methods=['GET', 'POST'])
def verify_code():
    if 'reset_email' not in session:
        return redirect(url_for('forgot_password'))

    email = session['reset_email']
    record = verification_codes.get(email)

    if request.method == 'POST':
        code_input = request.form.get('code')

        if not record:
            flash("❌ Verification code not found. Please request again.", "danger")
            return redirect(url_for('forgot_password'))

        sent_time = record.get('timestamp')
        if datetime.now() - sent_time > timedelta(minutes=2):
            verification_codes.pop(email, None)
            session.pop('code_sent_time', None)
            flash("❌ Verification code expired. Please resend.", "danger")
            return redirect(url_for('forgot_password'))

        if code_input == record.get('code'):
            session['verified'] = True
            return redirect(url_for('reset_password'))
        else:
            flash("❌ Invalid verification code.", "danger")

    return render_template('verify_code.html', title='Verify Code')

@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if not session.get('verified'):
        return redirect(url_for('forgot_password'))

    if request.method == 'POST':
        new_pass = request.form.get('new_password')
        confirm_pass = request.form.get('confirm_password')
        if new_pass == confirm_pass:
            email = session.get('reset_email')
            db_reset_password(email, new_pass)
            flash("✅ Password successfully reset!", "success")
            session['reset_success'] = True
            return redirect(url_for('reset_password'))
        else:
            flash("❌ Passwords do not match.", "danger")

    reset_success = session.pop('reset_success', False)
    return render_template('reset_password.html', title='Reset Password', reset_success=reset_success)


@app.route('/resend_code', methods=['POST'])
def resend_code():
    import random

    if 'email' not in session:
        flash('Session expired. Please try again.', 'danger')
        return redirect(url_for('forgot_password'))

    # Generate new code
    new_code = str(random.randint(100000, 999999))
    session['verification_code'] = new_code
    session['code_sent_time'] = datetime.now().timestamp()
    print(f"[Resent] Verification code sent to {session['email']}: {new_code}")
    flash('A new verification code has been sent to your email. (Check console)', 'info')
    return redirect(url_for('verify_code'))
