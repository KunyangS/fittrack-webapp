from flask import Flask
import os
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from app.config import Config
from flask_migrate import Migrate

# Load the environment variable
load_dotenv()

# Initialize Flask app, redirect the tamplate folder outside the app folder
template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'templates')
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static')

#Create Flask
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
# Read config.py
app.config.from_object(Config)
# Initialise database
db = SQLAlchemy(app)
# migrate database
migrate = Migrate(app,db)
# import models 
from app import models
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