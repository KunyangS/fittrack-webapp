from app import db
from app.models import User, UserInfo, FitnessEntry, FoodEntry, ShareEntry  # Added ShareEntry
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import date, time, datetime, timedelta  # Added datetime, timedelta
from sqlalchemy.exc import IntegrityError  # Added IntegrityError
from sqlalchemy import or_  # Added or_

def login_user(email_or_username, password):
    """
    Logs in a user by email or username.
    Args:
        email_or_username (str): The user's email or username.
        password (str): The user's password.
    Returns:
        User: The User object if login is successful, None otherwise.
    """
    user = User.query.filter(or_(User.email == email_or_username, User.username == email_or_username)).first()
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
        User: The newly created User object if registration is successful, None otherwise.
    """
    if User.query.filter_by(email=email).first() is not None:  # Changed from UserInfo to User
        return None  # Email already exists
    if User.query.filter_by(username=username).first() is not None:  # Changed from UserInfo to User
        return None  # Username already exists
    
    new_user = User(  # Changed from UserInfo to User
        username=username,
        email=email
    )
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()  # Commit to get new_user.id

    # Create UserInfo associated with the new User
    new_user_info = UserInfo(
        user_id=new_user.id,  # Link to the new User
        gender=gender,
        age=age,
        height=height,
        weight=weight,
        date=date.today()  # Add default date
    )
    db.session.add(new_user_info)
    db.session.commit()
    return new_user

def find_user_by_email(email):
    """
    Finds a user by email.
    Args:
        email (str): The user's email.
    Returns:
        User: The User object if found, None otherwise.
    """
    return User.query.filter_by(email=email).first()  # Changed from UserInfo to User

def find_user_by_username(username: str):
    """
    Finds a user by username.
    Args:
        username (str): The user's username.
    Returns:
        User: The User object if found, None otherwise.
    """
    return User.query.filter_by(username=username).first()

def reset_password(user, new_password):
    """
    Resets a user's password.
    Args:
        user (User): The User object.  # Changed from UserInfo to User
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
    'user_id_to_update' now refers to the User.id.
    Only updates fields if a new value is provided.
    'date_val' and 'time_val' update the UserInfo.date and UserInfo.time fields,
    representing the date/time associated with this profile data snapshot.
    """
    user_info = UserInfo.query.filter_by(user_id=user_id_to_update).first()  # Query UserInfo by user_id
    if not user_info:
        # Consider logging this or raising an error
        return None 

    updated = False
    # Update fields only if new values are provided and meaningful
    if date_val is not None:
        user_info.date = date_val  # Changed user to user_info
        updated = True
    if time_val is not None:
        user_info.time = time_val  # Changed user to user_info
        updated = True
    if gender_val is not None and gender_val.strip():  # Check for non-empty string
        user_info.gender = gender_val  # Changed user to user_info
        updated = True
    if age_val is not None:
        user_info.age = age_val  # Changed user to user_info
        updated = True
    if height_val is not None:
        user_info.height = height_val  # Changed user to user_info
        updated = True
    if weight_val is not None:
        user_info.weight = weight_val  # Changed user to user_info
        updated = True
    
    if updated:
        db.session.commit()
    return user_info  # Return UserInfo object

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

# --- Share Functions ---
def create_share_entry(sharer_user_id: int, sharee_user_id: int, data_categories: str, time_range: str):
    """
    Creates a new share entry.
    Args:
        sharer_user_id (int): The ID of the user sharing the data.
        sharee_user_id (int): The ID of the user with whom data is shared.
        data_categories (str): Comma-separated string of data categories (e.g., "basic_profile,activity_log").
        time_range (str): String representing the time range (e.g., "last_7_days").
    Returns:
        ShareEntry: The created ShareEntry object, or None if creation failed (e.g. duplicate).
    """
    try:
        # Check if sharer and sharee exist
        sharer = User.query.get(sharer_user_id)
        sharee = User.query.get(sharee_user_id)
        if not sharer or not sharee:
            return None # Or raise an error

        new_share = ShareEntry(
            sharer_user_id=sharer_user_id,
            sharee_user_id=sharee_user_id,
            data_categories=data_categories,
            time_range=time_range
        )
        db.session.add(new_share)
        db.session.commit()
        return new_share
    except IntegrityError:
        db.session.rollback()
        return None # Duplicate entry or other integrity issue
    except Exception as e:
        db.session.rollback()
        # Log error e
        return None

def get_shares_by_sharer(sharer_user_id: int):
    """
    Retrieves all active share entries made by a specific user.
    Args:
        sharer_user_id (int): The ID of the sharer user.
    Returns:
        list[ShareEntry]: A list of active ShareEntry objects.
    """
    return ShareEntry.query.filter_by(sharer_user_id=sharer_user_id, is_active=True).all()

def revoke_share_entry(share_entry_id: int, current_user_id: int):
    """
    Revokes a share entry by setting its is_active flag to False.
    Only the original sharer can revoke the share.
    Args:
        share_entry_id (int): The ID of the share entry to revoke.
        current_user_id (int): The ID of the user attempting to revoke the share.
    Returns:
        bool: True if revocation was successful, False otherwise.
    """
    share_entry = ShareEntry.query.get(share_entry_id)
    if share_entry and share_entry.sharer_user_id == current_user_id:
        share_entry.is_active = False
        db.session.commit()
        return True
    return False

def get_share_entry_by_id(share_entry_id: int):
    """
    Retrieves a specific share entry by its ID.
    Args:
        share_entry_id (int): The ID of the share entry.
    Returns:
        ShareEntry: The ShareEntry object if found, None otherwise.
    """
    return ShareEntry.query.get(share_entry_id)

# --- Data Retrieval for Sharing ---
def get_user_activity_data(user_id: int, data_categories_str: str, time_range_str: str):
    """
    Retrieves user data based on specified categories and time range.
    Args:
        user_id (int): The ID of the user whose data is being requested.
        data_categories_str (str): Comma-separated string of data categories.
                                (e.g., "basic_profile,fitness_log,food_log")
        time_range_str (str): String describing the time range.
                           (e.g., "all_time", "last_7_days", "last_30_days", "custom_start_end")
                           If "custom_start_end", it might need additional date parameters or parsing.
    Returns:
        dict: A dictionary containing the requested data, structured by category.
    """
    user = User.query.get(user_id)
    if not user:
        return None # Or raise an error

    data_categories = [category.strip() for category in data_categories_str.split(',')]
    results = {'user_id': user_id, 'username': user.username}

    # Define time filters
    end_date = date.today()
    start_date = None

    if time_range_str == "last_7_days":
        start_date = end_date - timedelta(days=7)
    elif time_range_str == "last_30_days":
        start_date = end_date - timedelta(days=30)
    # Add more time_range options as needed, e.g., "all_time" means start_date remains None

    if 'basic_profile' in data_categories:
        user_info = UserInfo.query.filter_by(user_id=user_id).order_by(UserInfo.date.desc()).first()
        if user_info:
            results['basic_profile'] = {
                'gender': user_info.gender,
                'age': user_info.age,
                'height': user_info.height,
                'weight': user_info.weight,
                'last_updated': user_info.date.isoformat() if user_info.date else None
            }

    if 'fitness_log' in data_categories:
        query = FitnessEntry.query.filter_by(user_id=user_id)
        if start_date:
            query = query.filter(FitnessEntry.date >= start_date)
        query = query.filter(FitnessEntry.date <= end_date).order_by(FitnessEntry.date.desc())
        fitness_entries = query.all()
        results['fitness_log'] = [
            {
                'date': entry.date.isoformat(),
                'activity_type': entry.activity_type,
                'duration': entry.duration,
                'calories_burned': entry.calories_burned,
                'emotion': entry.emotion
            } for entry in fitness_entries
        ]

    if 'food_log' in data_categories:
        query = FoodEntry.query.filter_by(user_id=user_id)
        if start_date:
            query = query.filter(FoodEntry.date >= start_date)
        query = query.filter(FoodEntry.date <= end_date).order_by(FoodEntry.date.desc(), FoodEntry.meal_type)
        food_entries = query.all()
        results['food_log'] = [
            {
                'date': entry.date.isoformat(),
                'food_name': entry.food_name,
                'quantity': entry.quantity,
                'calories': entry.calories,
                'meal_type': entry.meal_type
            } for entry in food_entries
        ]
        
    return results