from datetime import datetime, timedelta
# routes.py

from app import app
from flask import render_template
import random
from urllib.parse import urlencode

# Temporary in-memory user storage
users = {}
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
        input_value = request.form.get('email')  # still using 'email' field name for both
        password = request.form.get('password')

        # First, try to match by email
        user = users.get(input_value)

        # If not found by email, try to match by username
        if not user:
            for u in users.values():
                if u['username'] == input_value:
                    user = u
                    break

        if user and user['password'] == password:
            session['user'] = user['username']
            return redirect('/upload')
        else:
            flash("❌ Invalid email/username or password.", "danger")
            return redirect('/login')

    return render_template('login.html', title='Login')


# Route for Registration page (placeholder)
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        code = str(random.randint(100000, 999999))  # Random 6 digit code

        temp_users[email] = {
            'username': username,
            'password': password,
            'code': code
        }

        # Generate Verification Link
        query_params = urlencode({'email': email, 'code': code})
        verification_link = f"http://127.0.0.1:5000/verify-email?{query_params}"

        print(f"🔔 Verification Link for {email}: {verification_link}")

        flash("A verification link has been sent to your email (Check Console).", "info")
        return redirect('/login')
    return render_template('register.html')

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
