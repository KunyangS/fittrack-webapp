# app/models.py

from flask_sqlalchemy import SQLAlchemy
from datetime import date, time, datetime # Added datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash # Added
from flask_login import UserMixin # Added
from sqlalchemy.sql import func # Added for func.now

# User model for authentication and linking entries
class User(db.Model, UserMixin): # Added UserMixin
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    # Changed 'password' to 'password_hash' and increased length
    password_hash = db.Column(db.String(256), nullable=False) 

    # One-to-many relationships
    fitness_entries = db.relationship('FitnessEntry', backref='user', lazy=True)
    food_entries = db.relationship('FoodEntry', backref='user', lazy=True)
    
    # One-to-one relationship to UserInfo (optional, but good for convenience)
    # The backref 'user_account' is created on UserInfo, pointing back to this User
    info = db.relationship('UserInfo', backref=db.backref('user_account', uselist=False), uselist=False, lazy='joined')

    # Relationships for ShareEntry (as sharer and sharee)
    # These are implicitly created by ShareEntry's backrefs if not defined here,
    # but explicitly defining them can be clearer.
    # shares_made = db.relationship('ShareEntry', foreign_keys='ShareEntry.sharer_user_id', backref='sharer_user', lazy='dynamic')
    # shares_received = db.relationship('ShareEntry', foreign_keys='ShareEntry.sharee_user_id', backref='sharee_user', lazy='dynamic')
    # Note: The backrefs in ShareEntry ('sharer', 'sharee') will create these attributes on User model.

    def set_password(self, password): # Added from B
        self.password_hash = generate_password_hash(password)

    def check_password(self, password): # Added from B
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'
    
# User basic information model 
class UserInfo(db.Model):
    __tablename__ = 'user_info'
    
    id = db.Column(db.Integer, primary_key=True)
    # This user_id links UserInfo to a User. The backref 'user_account' is defined in User.info relationship.
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', name='fk_user_info_user_id'), nullable=False, unique=True) # unique=True for one-to-one

    date = db.Column(db.Date, default=date.today)
    time = db.Column(db.Time, nullable=True) # Made nullable to align with B's general approach
    # Made these nullable to align with B's flexibility
    gender = db.Column(db.String(10), nullable=True) 
    age = db.Column(db.Integer, nullable=True)
    height = db.Column(db.Float, nullable=True)  
    weight = db.Column(db.Float, nullable=True)  

    def __repr__(self):
        return f'<UserInfo {self.user_id} - {self.gender} - {self.weight}kg>'


# motion recording model
class FitnessEntry(db.Model):
    __tablename__ = 'fitness_entries'

    id = db.Column(db.Integer, primary_key=True)
    # user_id still refers to users.id, maintaining A's structure
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    date = db.Column(db.Date, default=date.today)
    activity_type = db.Column(db.String(64), nullable=True) 
    duration = db.Column(db.Float, nullable=True)  
    calories_burned = db.Column(db.Float, nullable=True)  
    emotion = db.Column(db.String(32), nullable=True) # Made nullable for consistency

    def __repr__(self):
        return f'<FitnessEntry {self.date} - {self.activity_type}>'


# food intake model
class FoodEntry(db.Model):
    __tablename__ = 'food_entries'

    id = db.Column(db.Integer, primary_key=True)
    # user_id still refers to users.id, maintaining A's structure
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    date = db.Column(db.Date, default=date.today)
    food_name = db.Column(db.String(64), nullable=True)
    quantity = db.Column(db.Float, nullable=True)  
    calories = db.Column(db.Float, nullable=True) 
    meal_type = db.Column(db.String(32), nullable=True) # Made nullable for consistency

    def __repr__(self):
        return f'<FoodEntry {self.date} - {self.food_name}>'

# Data Sharing model (Added from B, adapted FKs)
class ShareEntry(db.Model):
    __tablename__ = 'share_entries'

    id = db.Column(db.Integer, primary_key=True)
    # Foreign keys now point to 'users.id' instead of 'user_info.id'
    sharer_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    sharee_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    data_categories = db.Column(db.String(512), nullable=False)  # e.g., "basic_profile,activity_log"
    time_range = db.Column(db.String(64), nullable=False)  # e.g., "last_7_days", "all_time"
    # Changed default to use sqlalchemy.sql.func for database-side timestamp
    shared_at = db.Column(db.DateTime, default=func.now) # func.now() or datetime.utcnow
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    # Relationships to User model (instead of UserInfo)
    # 'User.shares_made' will be populated by this backref
    sharer = db.relationship('User', foreign_keys=[sharer_user_id], backref=db.backref('shares_made', lazy='dynamic'))
    # 'User.shares_received' will be populated by this backref
    sharee = db.relationship('User', foreign_keys=[sharee_user_id], backref=db.backref('shares_received', lazy='dynamic'))

    __table_args__ = (db.UniqueConstraint('sharer_user_id', 'sharee_user_id', 'data_categories', 'time_range', name='_sharer_sharee_data_time_uc'),)

    def __repr__(self):
        return f'<ShareEntry SharerID:{self.sharer_user_id} -> ShareeID:{self.sharee_user_id} ({self.data_categories})>'
