from datetime import datetime, timedelta
from app import app, db
from flask import render_template, request, session, redirect, url_for, flash
import random
from urllib.parse import urlencode
from app.models import UserInfo, ShareEntry
from app.database import (
    login_user as db_login_user, 
    register_user, 
    find_user_by_email, 
    find_user_by_username,
    reset_password as db_reset_password,
    create_share_entry,
    get_shares_by_sharer,
    revoke_share_entry,
    get_share_entry_by_id,
    get_user_activity_data
)
from flask_login import login_user, logout_user, login_required, current_user


# Temporary in-memory user storage
users = {}
temp_users = {}  # Temporary unverified users

# Route for the Introduction/Home page
@app.route('/')
def index():
    """Renders the introduction page."""
    return render_template('index.html', title='Welcome')

# Route for Data Visualisation page
@app.route('/visualise')
@login_required
def visualise():
    return render_template('visualise.html', username=current_user.username if hasattr(current_user, 'username') else "User")

# Route for Data Sharing page
@app.route('/share')
@login_required
def share():
    return render_template('share.html', username=current_user.username if hasattr(current_user, 'username') else "User")

# --- UPDATED LOGIN route ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('upload'))
    if request.method == 'POST':
        email_or_username = request.form.get('email')
        password = request.form.get('password')

        user = db_login_user(email_or_username, password)

        if user:
            login_user(user)
            flash(f"Welcome back, {user.username}!", "success")
            next_page = request.args.get('next')
            return redirect(next_page or url_for('upload'))
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
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect('/login')

# ✅ New UPLOAD Page after successful login
@app.route('/upload')
def upload():
    if 'user' not in session:
        return redirect('/login')
    return render_template('upload.html', username=session.get('user'))

# ✅ (ALL YOUR OTHER ROUTES REMAIN SAME AS YOU GAVE)
# ✅ UPDATED /verify-email Route
@app.route('/verify-email')
def verify_email():
    email = request.args.get('email')
    code = request.args.get('code')

    if not email or not code:
        flash('❌ Invalid verification link.', 'danger')
        return redirect('/login')

    user = temp_users.get(email)

    if user and user['code'] == code:
        users[email] = {
            'username': user['username'],
            'password': user['password']
        }
        temp_users.pop(email, None)
        flash('✅ Email verified successfully! Please login.', 'success')
        return redirect('/login')
    else:
        flash('❌ Verification failed. Invalid or expired link.', 'danger')
        return redirect('/login')
    
# m.extra
def forgot_password():
    return render_template('forgot_password.html', title='Forgot Password')

def reset_password():
    reset_success = session.pop('reset_success', False)
    return render_template('reset_password.html', title='Reset Password', reset_success=reset_success)

def reset_password():
    reset_success = session.pop('reset_success', False)
    return render_template('reset_password.html', title='Reset Password', reset_success=reset_success)

from flask import request, session, redirect, url_for, flash
import random

# Temporary in-memory store
verification_codes = {}

def reset_password():
    step = session.get('reset_step', 'email')

    if request.method == 'POST':
        if step == 'email':
            email = request.form.get('email')
            if email:
                code = str(random.randint(100000, 999999))
                verification_codes[email] = code
                session['reset_email'] = email
                session['reset_step'] = 'verify'
                print(f"🔐 Verification code for {email} is: {code}")
                flash("Verification code sent to your email. (Check console for test)", "info")
                return redirect(url_for('reset_password'))
        elif step == 'verify':
            email = session.get('reset_email')
            code_input = request.form.get('code')
            new_pass = request.form.get('new_password')
            confirm_pass = request.form.get('confirm_password')
            if code_input == verification_codes.get(email):
                if new_pass == confirm_pass:
                    flash("✅ Password successfully reset!", "success")
                    session.pop('reset_email', None)
                    session.pop('reset_step', None)
                    verification_codes.pop(email, None)
                    return redirect(url_for('login'))
                else:
                    flash("❌ Passwords do not match.", "danger")
            else:
                flash("❌ Invalid verification code.", "danger")

    step = session.get('reset_step', 'email')
    return render_template('reset_password.html', step=step, title='Reset Password')

verification_codes = {}

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
