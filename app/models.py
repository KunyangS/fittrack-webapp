# app/models.py

from flask_sqlalchemy import SQLAlchemy
from datetime import date, time, datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy.sql import func

# User model for authentication and linking entries
class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    # One-to-many relationships
    fitness_entries = db.relationship('FitnessEntry', backref='user', lazy=True)
    food_entries = db.relationship('FoodEntry', backref='user', lazy=True)
    
    # One-to-one relationship to UserInfo
    info = db.relationship('UserInfo', backref=db.backref('user_account', uselist=False), uselist=False, lazy='joined')

    # Relationships for ShareEntry (as sharer and sharee) are handled by backrefs

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

# User basic information model 
class UserInfo(db.Model):
    __tablename__ = 'user_info'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', name='fk_user_info_user_id'), nullable=False, unique=True)
    date = db.Column(db.Date, default=date.today)
    time = db.Column(db.Time, nullable=True)
    gender = db.Column(db.String(10), nullable=True)
    age = db.Column(db.Integer, nullable=True)
    height = db.Column(db.Float, nullable=True)
    weight = db.Column(db.Float, nullable=True)

    def __repr__(self):
        return f'<UserInfo {self.user_id} - {self.gender} - {self.weight}kg>'

# Motion recording model
class FitnessEntry(db.Model):
    __tablename__ = 'fitness_entries'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, default=date.today)
    activity_type = db.Column(db.String(64), nullable=False)
    duration = db.Column(db.Float, nullable=False)
    calories_burned = db.Column(db.Float, nullable=False)
    emotion = db.Column(db.String(32), nullable=True)

    def __repr__(self):
        return f'<FitnessEntry {self.date} - {self.activity_type}>'

# Food intake model
class FoodEntry(db.Model):
    __tablename__ = 'food_entries'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, default=date.today)
    food_name = db.Column(db.String(64), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    calories = db.Column(db.Float, nullable=False)
    meal_type = db.Column(db.String(32), nullable=True)

    def __repr__(self):
        return f'<FoodEntry {self.date} - {self.food_name}>'

# Data Sharing model
class ShareEntry(db.Model):
    __tablename__ = 'share_entries'

    id = db.Column(db.Integer, primary_key=True)
    sharer_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    sharee_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    data_categories = db.Column(db.String(512), nullable=False)
    time_range = db.Column(db.String(64), nullable=False)
    shared_at = db.Column(db.DateTime, default=func.now)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    # Relationships to User model
    sharer = db.relationship('User', foreign_keys=[sharer_user_id], backref=db.backref('shares_made', lazy='dynamic'))
    sharee = db.relationship('User', foreign_keys=[sharee_user_id], backref=db.backref('shares_received', lazy='dynamic'))

    __table_args__ = (db.UniqueConstraint('sharer_user_id', 'sharee_user_id', 'data_categories', 'time_range', name='_sharer_sharee_data_time_uc'),)

    def __repr__(self):
        return f'<ShareEntry SharerID:{self.sharer_user_id} -> ShareeID:{self.sharee_user_id} ({self.data_categories})>'