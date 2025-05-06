# app/models.py

from flask_sqlalchemy import SQLAlchemy
from datetime import date, time
from app import db
from werkzeug.security import generate_password_hash, check_password_hash


# User basic information model
class UserInfo(db.Model):
    __tablename__ = 'user_info'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    date = db.Column(db.Date, default=date.today)
    time = db.Column(db.Time)
    gender = db.Column(db.String(10))
    age = db.Column(db.Integer)
    height = db.Column(db.Float)  
    weight = db.Column(db.Float)  
    fitness_entries = db.relationship('FitnessEntry', backref='user', lazy=True)
    food_entries = db.relationship('FoodEntry', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<UserInfo {self.date} - {self.gender} - {self.weight}kg>'


# motion recording model
class FitnessEntry(db.Model):
    __tablename__ = 'fitness_entries'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user_info.id'), nullable=False)
    date = db.Column(db.Date, default=date.today)
    activity_type = db.Column(db.String(64), nullable=False) 
    duration = db.Column(db.Float, nullable=False)  
    calories_burned = db.Column(db.Float, nullable=False)  
    emotion = db.Column(db.String(32))  

    def __repr__(self):
        return f'<FitnessEntry {self.date} - {self.activity_type}>'


# food intake model
class FoodEntry(db.Model):
    __tablename__ = 'food_entries'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user_info.id'), nullable=False)
    date = db.Column(db.Date, default=date.today)
    food_name = db.Column(db.String(64), nullable=False)
    quantity = db.Column(db.Float, nullable=False)  
    calories = db.Column(db.Float, nullable=False) 
    meal_type = db.Column(db.String(32)) 

    def __repr__(self):
        return f'<FoodEntry {self.date} - {self.food_name}>'
