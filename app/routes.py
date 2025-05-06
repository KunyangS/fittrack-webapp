from datetime import datetime, timedelta
from app import app, db
from flask import render_template, request, session, redirect, url_for, flash
import random
from urllib.parse import urlencode
from app.models import UserInfo
from app.database import login_user, register_user, find_user_by_email, reset_password as db_reset_password

verification_codes = {}

# Route for the Introduction/Home page
@app.route('/')
def index():
    """Renders the introduction page."""
    return render_template('index.html', title='Welcome')

# Route for Data Visualisation page
@app.route('/visualise')
def visualise():
    if 'user_id' not in session:
        flash("Please login to access this page.", "warning")
        return redirect(url_for('login'))
    user = UserInfo.query.get(session['user_id'])
    return render_template('visualise.html', username=user.username if user else "User")

# Route for Data Sharing page
@app.route('/share')
def share():
    if 'user_id' not in session:
        flash("Please login to access this page.", "warning")
        return redirect(url_for('login'))
    user = UserInfo.query.get(session['user_id'])
    return render_template('share.html', username=user.username if user else "User")

# --- UPDATED LOGIN route ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email_or_username = request.form.get('email')
        password = request.form.get('password')

        user = login_user(email_or_username, password)

        if user:
            session['user_id'] = user.id
            session['username'] = user.username
            flash(f"Welcome back, {user.username}!", "success")
            return redirect(url_for('upload'))
        else:
            flash("Invalid email/username or password.", "danger")
            return redirect(url_for('login'))

    return render_template('login.html', title='Login')

# Route for Registration page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        gender = "Not specified"
        age = 0
        height = 0.0
        weight = 0.0

        if not username or not email or not password:
            flash("All fields are required.", "danger")
            return redirect(url_for('register'))

        new_user = register_user(username, email, password, gender, age, height, weight)

        if new_user:
            flash("Registration successful! Please login.", "success")
            return redirect(url_for('login'))
        else:
            flash("Registration failed. Email or username may already exist.", "danger")
            return redirect(url_for('register'))

    return render_template('register.html', title='Register')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# UPLOAD Page after successful login
@app.route('/upload')
def upload():
    if 'user_id' not in session:
        flash("Please login to access this page.", "warning")
        return redirect(url_for('login'))
    user = UserInfo.query.get(session['user_id'])
    return render_template('upload.html', username=user.username if user else "User")

# Forgot Password Route
@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = find_user_by_email(email)
        if user:
            code = str(random.randint(100000, 999999))
            verification_codes[email] = {
                'code': code,
                'timestamp': datetime.now(),
                'user_id': user.id
            }
            session['reset_email'] = email
            print(f"🔐 Verification code for {email}: {code}")
            flash("A verification code has been sent to your email (check console).", "info")
            return redirect(url_for('verify_code'))
        else:
            flash("Email address not found.", "danger")
    return render_template('forgot_password.html', title='Forgot Password')

# Verify Code Route
@app.route('/verify-code', methods=['GET', 'POST'])
def verify_code():
    if 'reset_email' not in session:
        flash("Session expired or invalid access.", "warning")
        return redirect(url_for('forgot_password'))

    email = session['reset_email']
    record = verification_codes.get(email)

    if not record:
        flash("Verification code not found or expired. Please request again.", "danger")
        return redirect(url_for('forgot_password'))

    if request.method == 'POST':
        code_input = request.form.get('code')
        
        if datetime.now() - record['timestamp'] > timedelta(minutes=5):
            verification_codes.pop(email, None)
            flash("Verification code expired. Please request a new one.", "danger")
            return redirect(url_for('forgot_password'))

        if code_input == record['code']:
            session['verified_for_reset'] = True
            session['user_id_for_reset'] = record['user_id']
            verification_codes.pop(email, None)
            return redirect(url_for('reset_password'))
        else:
            flash("Invalid verification code.", "danger")
            
    return render_template('verify_code.html', title='Verify Code', email=email)

# Reset Password Route
@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if not session.get('verified_for_reset') or 'user_id_for_reset' not in session:
        flash("Please verify your email first.", "warning")
        return redirect(url_for('forgot_password'))

    if request.method == 'POST':
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if new_password == confirm_password:
            user_id = session['user_id_for_reset']
            user = UserInfo.query.get(user_id)
            if user:
                db_reset_password(user, new_password)
                flash("Password successfully reset! Please login.", "success")
                session.pop('verified_for_reset', None)
                session.pop('user_id_for_reset', None)
                session.pop('reset_email', None)
                return redirect(url_for('login'))
            else:
                flash("User not found. Password reset failed.", "danger")
        else:
            flash("Passwords do not match.", "danger")
    
    reset_success_flag = session.pop('reset_success', False)
    return render_template('reset_password.html', title='Reset Password', reset_success=reset_success_flag)

@app.route('/resend-code', methods=['POST'])
def resend_code():
    email = session.get('reset_email')
    if not email:
        flash('Session expired or email not found. Please start over.', 'danger')
        return redirect(url_for('forgot_password'))

    user = find_user_by_email(email)
    if user:
        new_code = str(random.randint(100000, 999999))
        verification_codes[email] = {
            'code': new_code,
            'timestamp': datetime.now(),
            'user_id': user.id
        }
        print(f"🔐 [Resent] Verification code for {email}: {new_code}")
        flash('A new verification code has been sent to your email (check console).', 'info')
    else:
        flash('User not found for this email.', 'danger')
        return redirect(url_for('forgot_password'))
        
    return redirect(url_for('verify_code'))
