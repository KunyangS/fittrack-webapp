# app/models.py

from flask_sqlalchemy import SQLAlchemy
from datetime import date, time
from app import db

# User model for authentication and linking entries
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

    # One-to-many relationships
    fitness_entries = db.relationship('FitnessEntry', backref='user', lazy=True)
    food_entries = db.relationship('FoodEntry', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'
    
# User basic information model 
class UserInfo(db.Model):
    __tablename__ = 'user_info'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    date = db.Column(db.Date, default=date.today)
    time = db.Column(db.Time)
    gender = db.Column(db.String(10), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    height = db.Column(db.Float, nullable=False)  
    weight = db.Column(db.Float, nullable=False)  

    def __repr__(self):
        return f'<UserInfo {self.date} - {self.gender} - {self.weight}kg>'


# motion recording model
class FitnessEntry(db.Model):
    __tablename__ = 'fitness_entries'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

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
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    date = db.Column(db.Date, default=date.today)
    food_name = db.Column(db.String(64), nullable=False)
    quantity = db.Column(db.Float, nullable=False)  
    calories = db.Column(db.Float, nullable=False) 
    meal_type = db.Column(db.String(32)) 

    def __repr__(self):
        return f'<FoodEntry {self.date} - {self.food_name}>'
