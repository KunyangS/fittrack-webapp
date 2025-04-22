# __init__.py
# Imports
from flask import Flask
import os
from flask_sqlalchemy import SQLAlchemy

# Initialize Flask app, redirect the tamplate folder outside the app folder
template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'templates')
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static')

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
# Set a secret key for session management, which needs to be refined after "Security" lecture
app.config['SECRET_KEY'] = os.urandom(24)

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fitness.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# --- Routes ---
from app import routes

# Register Blueprints
from app.upload import upload_bp   
app.register_blueprint(upload_bp) 

app.secret_key = "fittrack@2025_secret_reset_feature"