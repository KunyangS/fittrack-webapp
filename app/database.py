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

def update_user_profile_details(user_id_to_update: int, 
                                date_val: date | None = None, 
                                time_val: time | None = None, 
                                gender_val: str | None = None, 
                                age_val: int | None = None, 
                                height_val: float | None = None, 
                                weight_val: float | None = None):
    """
    Updates specified profile details for a given user.
    Only updates fields if a new value is provided.
    'date_val' and 'time_val' update the UserInfo.date and UserInfo.time fields,
    representing the date/time associated with this profile data snapshot.
    """
    user = UserInfo.query.get(user_id_to_update)
    if not user:
        # Consider logging this or raising an error
        return None 

    updated = False
    # Update fields only if new values are provided and meaningful
    if date_val is not None:
        user.date = date_val
        updated = True
    if time_val is not None:
        user.time = time_val
        updated = True
    if gender_val is not None and gender_val.strip(): # Check for non-empty string
        user.gender = gender_val
        updated = True
    if age_val is not None:
        user.age = age_val
        updated = True
    if height_val is not None:
        user.height = height_val
        updated = True
    if weight_val is not None:
        user.weight = weight_val
        updated = True
    
    if updated:
        db.session.commit()
    return user

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