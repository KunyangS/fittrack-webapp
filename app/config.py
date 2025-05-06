import os

# Get the root path of the project
basedir = os.path.abspath(os.path.dirname(__file__))
# Build the default SQLite database path 
default_database_path = 'sqlite:///'+os.path.join(basedir, 'fitness.db')

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(24)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or default_database_path
    SQLALCHEMY_TRACK_MODIFICATIONS = False