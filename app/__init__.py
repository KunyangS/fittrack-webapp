# __init__.py
# Imports
from flask import Flask
import os

# Initialize Flask app, redirect the tamplate folder outside the app folder
template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'templates')
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static')

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
# Set a secret key for session management, which needs to be refined after "Security" lecture
app.config['SECRET_KEY'] = os.urandom(24)

# --- Routes ---
from app import routes