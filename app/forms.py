#forms.py
# A form is needed to create a new user or login
# from flask_wtf import FlaskForm
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
import re

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=3, max=80, message="Username must be between 3 and 80 characters.")
    ])
    email = StringField('Email', validators=[
        DataRequired(),
        Email(message="Enter a valid email address.")
    ])
    password = PasswordField('Password', validators=[
        DataRequired()
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match.')
    ])
    submit = SubmitField('Register')

    def validate_password(self, field):
        password = field.data
        # At least 8 chars, one uppercase, one digit, one special char
        if not re.match(r"^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$", password):
            raise ValidationError(
                "Password must be at least 8 characters long and include at least one uppercase letter, one digit, and one special character."
            )