from app import app
from flask import render_template
@app.route('/upload')
def upload():
    """Renders the data upload page."""
    return render_template('upload.html', title='Upload Data')
