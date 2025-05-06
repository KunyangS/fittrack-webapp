from app import db
from app.models import UserInfo
from werkzeug.security import check_password_hash, generate_password_hash

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