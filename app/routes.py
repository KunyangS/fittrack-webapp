# routes.py

from app import app
from flask import render_template

# Route for the Introduction/Home page
@app.route('/')
def index():
    """Renders the introduction page."""
    return render_template('index.html', title='Welcome') # Pass title variable


# Route for Data Visualisation page (placeholder)
@app.route('/visualise')
def visualise():
    """Renders the data visualisation page."""
    # We will create visualise.html in the next iteration
    return render_template('visualise.html', title='Visualise Data')

# Route for Data Sharing page (placeholder)
@app.route('/share')
def share():
    """Renders the data sharing page."""
    # We will create share.html in the next iteration
    return render_template('share.html', title='Share Data')

# Route for Login page (placeholder)
@app.route('/login')
def login():
    """Renders the login page."""
    # We will create login.html later if needed, or handle via modals
    # For now, just show a basic template or redirect
    # Let's create a simple placeholder login.html
    return render_template('login.html', title='Login')

# Route for Registration page (placeholder)
@app.route('/register')
def register():
    """Renders the registration page."""
    # We will create register.html later if needed
    # Let's create a simple placeholder register.html
    return render_template('register.html', title='Register')

# m.extra
def forgot_password():
    return render_template('forgot_password.html', title='Forgot Password')

def reset_password():
    return render_template('reset_password.html', title='Reset Password')

def reset_password():
    return render_template('reset_password.html', title='Reset Password')

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
            verification_codes[email] = code
            session['reset_email'] = email
            print(f"🔐 Verification code for {email}: {code}")
            flash("Verification code sent to your email. (Check console)", "info")
            return redirect(url_for('verify_code'))
    return render_template('forgot_password.html', title='Forgot Password')

@app.route('/verify-code', methods=['GET', 'POST'])
def verify_code():
    if 'reset_email' not in session:
        return redirect(url_for('forgot_password'))

    if request.method == 'POST':
        code_input = request.form.get('code')
        email = session['reset_email']
        if code_input == verification_codes.get(email):
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
            session.clear()
            return redirect(url_for('login'))
        else:
            flash("❌ Passwords do not match.", "danger")

    return render_template('reset_password.html', title='Reset Password')