import os

# Get the root path of the project
basedir = os.path.abspath(os.path.dirname(__file__))
# Build the default SQLite database path 
instance_path = os.path.join(basedir, 'instance')

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(24)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(instance_path, 'fitness.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False