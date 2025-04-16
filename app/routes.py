# routes.py

from app import app
from flask import render_template

# Route for the Introduction/Home page
@app.route('/')
def index():
    """Renders the introduction page."""
    return render_template('index.html', title='Welcome') # Pass title variable

# Route for Data Upload page (placeholder)
@app.route('/upload')
def upload():
    """Renders the data upload page."""
    # We will create upload.html in the next iteration
    return render_template('upload.html', title='Upload Data')

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