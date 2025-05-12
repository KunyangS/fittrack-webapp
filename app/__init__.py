# __init__.py
# Imports

from flask import Flask
import os
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from config import Config, instance_path # Import instance_path
from flask_migrate import Migrate
from flask_wtf import CSRFProtect
from flask_login import LoginManager



# Load the environment variable
load_dotenv()

# Initialize Flask app, redirect the tamplate folder outside the app folder
template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'templates')
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static')

#Create Flask
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
# Read config.py
app.config.from_object(Config)

# Ensure the instance folder exists
if not os.path.exists(instance_path):
    os.makedirs(instance_path)

# Initialise database
db = SQLAlchemy(app)
# migrate database
migrate = Migrate(app,db)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' # Changed from 'routes.login'

# import models 
from app import models

# User loader function for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    print(f"--- load_user called with user_id: {user_id} ---")
    user = models.User.query.get(int(user_id)) # Changed UserInfo to User
    print(f"--- load_user returning: {user} ---")
    return user

#  Input routes
from app import routes
#  Register Bluprints
from app.upload import upload_bp
app.register_blueprint(upload_bp)



from flask_dance.contrib.google import make_google_blueprint
google_bp = make_google_blueprint(
    client_id="YOUR_GOOGLE_CLIENT_ID",
    client_secret="YOUR_GOOGLE_CLIENT_SECRET",
    redirect_to="google_login"  # Define this route in your app
)
app.register_blueprint(google_bp, url_prefix="/login")

# Facebook OAuth setup
from flask_dance.contrib.facebook import make_facebook_blueprint
facebook_bp = make_facebook_blueprint(
    client_id="YOUR_FACEBOOK_APP_ID",
    client_secret="YOUR_FACEBOOK_APP_SECRET",
    redirect_to="facebook_login"  # Define this route in your app
)
app.register_blueprint(facebook_bp, url_prefix="/login")