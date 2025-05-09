
# routes.py
from datetime import datetime, timedelta

from app.models import User
from app import app
from flask import render_template, redirect, url_for, flash, request, session
import random
from urllib.parse import urlencode
from app import db
from app.forms import RegistrationForm
import re 


# Temporary in-memory user storage
temp_users = {}  # Temporary unverified users

# Route for the Introduction/Home page
@app.route('/')
def index():
    """Renders the introduction page."""
    return render_template('index.html', title='Welcome') # Pass title variable

# Route for Data Visualisation page (placeholder)
@app.route('/visualise')
def visualise():
    if 'user' not in session:
        return redirect('/login')
    return render_template('visualise.html', username=session.get('user'))

# Route for Data Sharing page (placeholder)
@app.route('/share')
def share():
    if 'user' not in session:
        return redirect('/login') 
    return render_template('share.html', username=session.get('user'))

# --- 🛠 UPDATED LOGIN route ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        input_value = request.form.get('email')  # Can be email or username
        password = request.form.get('password')

        # Check database: base on email
        user = User.query.filter_by(email=input_value).first()

        if not user:
            # then check username :))
            user = User.query.filter_by(username=input_value).first()

        if user and user.password == password:
            session['user'] = user.username
            return redirect('/upload')
        else:
            flash("❌ Invalid email/username or password.", "danger")
            return redirect('/login')

    return render_template('login.html', title='Login')


@app.route('/register', methods=['GET', 'POST'])
def register():
    print("DEBUG: Entered /register route")
    form = RegistrationForm()

    if request.method == 'POST':
        print("DEBUG: POST request received")
        if not form.validate_on_submit():
            print("DEBUG: Form did not validate")
            print("Form errors:", form.errors)
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f"❌ {error}", "danger")
            return redirect('/register')

        print("DEBUG: Form validated successfully")
        username = form.username.data
        email = form.email.data
        password = form.password.data

        code = str(random.randint(100000, 999999))
        temp_users[email] = {
            'username': username,
            'password': password,
            'code': code
        }
        query_params = urlencode({'email': email, 'code': code})
        verification_link = f"http://127.0.0.1:5000/verify-email?{query_params}"
        print("DEBUG: Registration passed validation, about to print verification link")
        print(f"🔔 Verification Link for {email}: {verification_link}")

        flash("A verification link has been sent to your email (Check Console).", "info")
        return redirect('/login')
    return render_template('register.html', form=form)

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('You have been logged out.', 'info')
    return redirect('/login')

@app.route('/verify-email')
def verify_email():

    email = request.args.get('email')
    code = request.args.get('code')

    if not email or not code:
        flash('❌ Invalid verification link.', 'danger')
        return redirect('/login')

    user = temp_users.get(email)
    if user and user['code'] == code:
        new_user = User(
            username=user['username'],
            email=email,
            password=user['password']
        )
        db.session.add(new_user)
        db.session.commit()
        temp_users.pop(email, None)
        flash('✅ Email verified successfully! Please login.', 'success')
        return redirect('/login')
    else:
        flash('❌ Verification failed. Invalid or expired link.', 'danger')
        return redirect('/login')

# ✅ New UPLOAD Page after successful login
@app.route('/upload')
def upload():
    if 'user' not in session:
        return redirect('/login')
    return render_template('upload.html', username=session.get('user'))

    
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
