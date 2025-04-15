# app.py
# Imports
from flask import Flask, render_template

# Initialize Flask app
app = Flask(__name__)

# --- Routes ---

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

# Route for Data Visualization page (placeholder)
@app.route('/visualize')
def visualize():
    """Renders the data visualization page."""
    # We will create visualize.html in the next iteration
    return render_template('visualize.html', title='Visualize Data')

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


# --- Run the App ---
if __name__ == '__main__':
    # Runs the Flask development server
    # Debug=True allows auto-reloading on code changes
    app.run(debug=True)