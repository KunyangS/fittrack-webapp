from app import db
from app.models import UserInfo, FitnessEntry, FoodEntry
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import date, time

def login_user(email, password):
    """
    Logs in a user.
    Args:
        email (str): The user's email.
        password (str): The user's password.
    Returns:
        UserInfo: The UserInfo object if login is successful, None otherwise.
    """
    user = UserInfo.query.filter_by(email=email).first()
    if user and user.check_password(password):
        return user
    return None

def register_user(username, email, password, gender, age, height, weight):
    """
    Registers a new user.
    Args:
        username (str): The user's username.
        email (str): The user's email.
        password (str): The user's password.
        gender (str): The user's gender.
        age (int): The user's age.
        height (float): The user's height.
        weight (float): The user's weight.
    Returns:
        UserInfo: The newly created UserInfo object if registration is successful, None otherwise.
    """
    if UserInfo.query.filter_by(email=email).first() is not None:
        return None  # Email already exists
    if UserInfo.query.filter_by(username=username).first() is not None:
        return None  # Username already exists
    
    new_user = UserInfo(
        username=username,
        email=email,
        gender=gender,
        age=age,
        height=height,
        weight=weight
    )
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    return new_user

def find_user_by_email(email):
    """
    Finds a user by email.
    Args:
        email (str): The user's email.
    Returns:
        UserInfo: The UserInfo object if found, None otherwise.
    """
    return UserInfo.query.filter_by(email=email).first()

def reset_password(user, new_password):
    """
    Resets a user's password.
    Args:
        user (UserInfo): The UserInfo object.
        new_password (str): The new password.
    """
    user.set_password(new_password)
    db.session.commit()

def upsert_daily_user_data(user_id, date_val: date, time_val: time, gender_val: str, age_val: int, height_val: float, weight_val: float):
    """
    Creates or updates a daily user data snapshot.
    Assumes UserInfo model can store these daily logs and has a user_id field.
    An entry is identified by user_id and date_val for updates.
    """
    daily_log = UserInfo.query.filter_by(user_id=user_id, date=date_val).first()

    if daily_log:
        # Update existing daily log
        daily_log.time = time_val
        daily_log.gender = gender_val
        daily_log.age = age_val
        daily_log.height = height_val
        daily_log.weight = weight_val
    else:
        # Create new daily log
        daily_log = UserInfo(
            user_id=user_id,
            date=date_val,
            time=time_val,
            gender=gender_val,
            age=age_val,
            height=height_val,
            weight=weight_val
        )
        db.session.add(daily_log)
    db.session.commit()
    return daily_log

def add_user_fitness_entry(user_id, date_val: date, activity_type_val: str, duration_val: float, calories_burned_val: float, emotion_val: str):
    """
    Adds a new fitness entry for the user.
    Assumes FitnessEntry model has a user_id field.
    """
    new_entry = FitnessEntry(
        user_id=user_id,
        date=date_val,
        activity_type=activity_type_val,
        duration=duration_val,
        calories_burned=calories_burned_val,
        emotion=emotion_val
    )
    db.session.add(new_entry)
    db.session.commit()
    return new_entry

def upsert_user_food_entry(user_id, date_val: date, food_name_val: str, quantity_val: float, calories_val: float, meal_type_val: str):
    """
    Creates or updates a food entry for the user.
    An entry is identified by user_id, date_val, and meal_type_val for updates.
    Assumes FoodEntry model has a user_id field.
    """
    food_entry = FoodEntry.query.filter_by(user_id=user_id, date=date_val, meal_type=meal_type_val).first()

    if food_entry:
        # Update existing food entry
        food_entry.food_name = food_name_val
        food_entry.quantity = quantity_val
        food_entry.calories = calories_val
    else:
        # Create new food entry
        food_entry = FoodEntry(
            user_id=user_id,
            date=date_val,
            food_name=food_name_val,
            quantity=quantity_val,
            calories=calories_val,
            meal_type=meal_type_val
        )
        db.session.add(food_entry)
    db.session.commit()
    return food_entry