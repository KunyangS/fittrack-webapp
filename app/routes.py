# routes.py
from datetime import datetime, timedelta

from app import app, db, login_manager
from flask import render_template, request, session, redirect, url_for, flash, jsonify
import random
from urllib.parse import urlencode
from app.models import User, UserInfo, ShareEntry, FitnessEntry, FoodEntry
from app.forms import RegistrationForm
import os
from werkzeug.utils import secure_filename
import re
import sqlite3
import pandas as pd

# Database helpers
from app.database import (
    login_user as db_login_user, 
    register_user as db_register_user, 
    find_user_by_email, 
    find_user_by_username, 
    reset_password as db_reset_password,
    create_share_entry,
    get_shares_by_sharer,
    revoke_share_entry,
    get_share_entry_by_id,
    get_user_activity_data
)

# Flask-Login helpers
from flask_login import login_user as flask_login_user, logout_user, login_required, current_user

# Temporary in-memory user storage
temp_users = {}  # Temporary unverified users
verification_codes = {}  # Temporary in-memory store for verification codes

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Route for the Introduction/Home page
@app.route('/')
def index():
    """Renders the introduction page."""
    return render_template('index.html', title='Welcome') # Pass title variable

# Route for Data Visualisation page (placeholder)
@app.route('/visualise')
@login_required
def visualise():
    try:
        # Connect to the SQLite database (adjust path if necessary)
        conn = sqlite3.connect("instance/fitness.db")

        # Read fitness and food entry data using pandas with columns that match the actual database structure
        fitness_df = pd.read_sql_query(
            "SELECT id, user_id, date, activity_type, duration, calories_burned, emotion FROM fitness_entries WHERE user_id = ?", 
            conn, params=(current_user.id,))
        
        food_df = pd.read_sql_query(
            "SELECT id, user_id, date, food_name, quantity, calories, meal_type FROM food_entries WHERE user_id = ?", 
            conn, params=(current_user.id,))

        # Convert DataFrames to list of dictionaries for rendering in the template
        fitness_data = fitness_df.to_dict(orient='records')
        food_data = food_df.to_dict(orient='records')

        # Close the database connection
        conn.close()

        print(f"Fetched {len(fitness_data)} fitness entries and {len(food_data)} food entries for user {current_user.username}")

    except Exception as e:
        print(f"Error fetching data: {e}")
        # Render a fallback error page if any database issue occurs
        return render_template('error.html', error_message="Database error occurred")

    # Render the visualisation page with the fetched data
    return render_template(
        'visualise.html',
        username=current_user.username,
        fitness_data=fitness_data,
        food_data=food_data
    )

# Route for Data Sharing page
@app.route('/share', methods=['GET', 'POST'])
@login_required
def share():
    category_map = {
        'basic_profile': 'Basic Profile',
        'fitness_log': 'Activity Log',
        'food_log': 'Meal Log',
        # Add other mappings as they appear in your form/models
    }
    time_map = {
        'last_7_days': 'Last 7 Days',
        'last_30_days': 'Last 30 Days',
        'all_time': 'All Time',
    }

    if request.method == 'POST':
        recipient_username_or_email = request.form.get('share_users')
        data_categories_list_from_form = sorted(list(set(request.form.getlist('share_options')))) # Ensure unique and sorted
        new_time_range_key = request.form.get('time_range')

        if not recipient_username_or_email:
            flash('Recipient username or email cannot be empty.', 'danger')
            return redirect(url_for('share'))

        if not data_categories_list_from_form:
            flash('Please select at least one data category to share.', 'danger')
            return redirect(url_for('share'))

        recipient = User.query.filter((User.username == recipient_username_or_email) | (User.email == recipient_username_or_email)).first()

        if not recipient:
            flash(f"User '{recipient_username_or_email}' not found.", 'warning')
            return redirect(url_for('share'))
            
        if recipient.id == current_user.id:
            flash("You cannot share data with yourself.", 'warning')
            return redirect(url_for('share'))

        new_data_categories_str_from_form = ','.join(data_categories_list_from_form)

        existing_active_share = ShareEntry.query.filter_by(
            sharer_user_id=current_user.id,
            sharee_user_id=recipient.id,
            is_active=True
        ).first()

        if existing_active_share:
            current_categories_in_db_set = set(existing_active_share.data_categories.split(','))
            new_categories_from_form_set = set(data_categories_list_from_form)
            current_time_range_in_db = existing_active_share.time_range

            # Check if the new request is a subset of or equal to the current share and time range is the same
            if new_categories_from_form_set.issubset(current_categories_in_db_set) and new_time_range_key == current_time_range_in_db:
                requested_display_categories = [category_map.get(cat, cat) for cat in data_categories_list_from_form]
                display_time_range = time_map.get(new_time_range_key, new_time_range_key)
                flash(f"Data including the selected categories ({', '.join(requested_display_categories)}) is already shared with {recipient.username} for the time range {display_time_range}.", 'info')
            else:
                # Update existing share
                combined_categories_set = current_categories_in_db_set.union(new_categories_from_form_set)
                final_categories_str = ','.join(sorted(list(combined_categories_set)))
                
                actually_added_category_keys = combined_categories_set - current_categories_in_db_set
                time_range_updated = new_time_range_key != current_time_range_in_db

                existing_active_share.data_categories = final_categories_str
                existing_active_share.time_range = new_time_range_key
                existing_active_share.shared_at = datetime.utcnow() # Update timestamp
                db.session.commit()

                update_messages = []
                if actually_added_category_keys:
                    added_display_names = [category_map.get(cat, cat) for cat in sorted(list(actually_added_category_keys))]
                    update_messages.append(f"Added data categories: {', '.join(added_display_names)}")
                
                if time_range_updated:
                    display_new_time_range = time_map.get(new_time_range_key, new_time_range_key)
                    update_messages.append(f"Time range updated to {display_new_time_range}")
                
                if not update_messages and not actually_added_category_keys and not time_range_updated:
                     # This case implies new_categories_from_form_set was not a subset, but union resulted in no change to categories, and time range was same.
                     # This should ideally be caught by the issubset check if logic is perfect, but as a fallback.
                    flash(f"Share with {recipient.username} is already up to date with the requested settings.", 'info')
                else:
                    flash(f"Share with {recipient.username} updated. {'. '.join(update_messages)}.", 'success')
        else:
            # No active share exists, create a new one
            share_entry_instance = create_share_entry(
                sharer_user_id=current_user.id,
                sharee_user_id=recipient.id,
                data_categories=new_data_categories_str_from_form,
                time_range=new_time_range_key
            )
            if share_entry_instance:
                flash(f"Data successfully shared with {recipient.username}.", 'success')
            else:
                flash(f"Failed to process share request with {recipient.username}. Please try again.", 'danger')
        
        return redirect(url_for('share'))

    # GET request: Query current shares for this user (existing logic)
    share_entries = get_shares_by_sharer(current_user.id)
    current_shares = []
    for entry in share_entries:
        sharee_name = entry.sharee.username if hasattr(entry.sharee, 'username') else str(entry.sharee_user_id)
        categories_keys = entry.data_categories.split(',')
        categories_display = [category_map.get(cat, cat.replace('_', ' ').title()) for cat in categories_keys if cat]
        time_range_display = time_map.get(entry.time_range, entry.time_range.replace('_', ' ').title())
        current_shares.append({
            'sharee_name': sharee_name,
            'data_categories': categories_display,
            'time_range': time_range_display,
            'share_id': entry.id
        })

    # Get shares shared with the current user
    shares_with_user = ShareEntry.query.filter_by(sharee_user_id=current_user.id, is_active=True).all()
    shared_with_you_data = []
    for entry in shares_with_user:
        sharer_name = entry.sharer.username if hasattr(entry.sharer, 'username') else str(entry.sharer_user_id)
        categories_keys = entry.data_categories.split(',')
        categories_display = [category_map.get(cat, cat.replace('_', ' ').title()) for cat in categories_keys if cat]
        time_range_display = time_map.get(entry.time_range, entry.time_range.replace('_', ' ').title())
        shared_with_you_data.append({
            'sharer_name': sharer_name,
            'data_categories': categories_display,
            'time_range': time_range_display,
            'shared_at': entry.shared_at.strftime('%Y-%m-%d %H:%M')
        })

    # Get share history (inactive shares)
    share_history_entries = ShareEntry.query.filter(
        ((ShareEntry.sharer_user_id == current_user.id) | (ShareEntry.sharee_user_id == current_user.id)) & (ShareEntry.is_active == False)
    ).order_by(ShareEntry.shared_at.desc()).all()
    share_history_data = []
    for entry in share_history_entries:
        sharer_name = entry.sharer.username if hasattr(entry.sharer, 'username') else str(entry.sharer_user_id)
        sharee_name = entry.sharee.username if hasattr(entry.sharee, 'username') else str(entry.sharee_user_id)
        categories_keys = entry.data_categories.split(',')
        categories_display = [category_map.get(cat, cat.replace('_', ' ').title()) for cat in categories_keys if cat]
        time_range_display = time_map.get(entry.time_range, entry.time_range.replace('_', ' ').title())
        share_history_data.append({
            'sharer_name': sharer_name,
            'sharee_name': sharee_name,
            'data_categories': categories_display,
            'time_range': time_range_display,
            'shared_at': entry.shared_at.strftime('%Y-%m-%d %H:%M'),
            'status': 'Revoked' # Or determine based on other fields if necessary
        })

    return render_template('share.html', current_shares=current_shares, username=current_user.username, shared_with_you=shared_with_you_data, share_history=share_history_data)

@app.route('/revoke_share/<int:share_id>', methods=['POST'])
@login_required
def revoke_share(share_id):
    """
    Handles revoking a share entry. Only the sharer can revoke.
    """
    success = revoke_share_entry(share_id, current_user.id)
    if success:
        flash('Share revoked successfully.', 'success')
    else:
        flash('Failed to revoke share. Ensure you are the owner or the share exists.', 'danger')
    return redirect(url_for('share'))

# --- 🛠 UPDATED LOGIN route ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('upload.upload_page')) # Or wherever you want logged-in users to go

    if request.method == 'POST':
        input_value = request.form.get('email')  # Can be email or username
        password = request.form.get('password')

        user = db_login_user(input_value, password) # Use database function

        if user:
            flask_login_user(user) # Use Flask-Login to handle the session
            next_page = request.args.get('next')
            return redirect(next_page or url_for('upload.upload_page'))
        else:
            flash("❌ Invalid email/username or password.", "danger")
            return redirect(url_for('login'))

    return render_template('login.html', title='Login')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if request.method == 'POST':
        if not form.validate_on_submit():
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f"❌ {error}", "danger")
            return redirect('/register')
        
        username = form.username.data
        email = form.email.data
        password = form.password.data

        code = str(random.randint(100000, 999999))
        temp_users[email] = {
            'username': username,
            'password': password,
            'code': code
        }
        verification_link = url_for('verify_email', email=email, code=code, _external=True)
        print("DEBUG: Registration passed validation, about to print verification link")
        print(f"🔔 Verification Link for {email}: {verification_link}")

        flash("A verification link has been sent to your email (Check Console).", "info")
        return redirect('/login')
    return render_template('register.html', form=form)

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/verify-email')
def verify_email():
    email = request.args.get('email')
    code = request.args.get('code')

    if not email or not code:
        flash('❌ Invalid verification link.', 'danger')
        return redirect(url_for('login'))

    user_data = temp_users.get(email)
    if user_data and user_data['code'] == code:
        registered_user = db_register_user(
            username=user_data['username'],
            email=email,
            password=user_data['password'],
            gender=None,
            age=None,
            height=None,
            weight=None
        )
        if registered_user:
            temp_users.pop(email, None)
            flash('✅ Email verified successfully! Please login.', 'success')
        else:
            flash('❌ Registration failed. Username or email may already exist, or an error occurred.', 'danger')
        return redirect(url_for('login'))
    else:
        flash('❌ Verification failed. Invalid or expired link.', 'danger')
        return redirect(url_for('login'))


@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        if email:
            code = str(random.randint(100000, 999999))
            verification_codes[email] = {
                'code': code,
                'timestamp': datetime.now()
            }
            session['reset_email'] = email
            print(f"🔐 Verification code for {email}: {code}")
            flash("Verification code sent to your email. (Check console)", "info")
            return redirect(url_for('verify_code'))
    return render_template('forgot_password.html', title='Forgot Password')

# ✅ FIXED: verify_code route now includes 2-minute expiry check
@app.route('/verify-code', methods=['GET', 'POST'])
def verify_code():
    if 'reset_email' not in session:
        return redirect(url_for('forgot_password'))

    email = session['reset_email']
    record = verification_codes.get(email)

    if request.method == 'POST':
        code_input = request.form.get('code')

        if not record:
            flash("❌ Verification code not found. Please request again.", "danger")
            return redirect(url_for('forgot_password'))

        sent_time = record.get('timestamp')
        if datetime.now() - sent_time > timedelta(minutes=2):
            verification_codes.pop(email, None)
            session.pop('code_sent_time', None)
            flash("❌ Verification code expired. Please resend.", "danger")
            return redirect(url_for('forgot_password'))

        if code_input == record.get('code'):
            session['verified'] = True
            return redirect(url_for('reset_password'))
        else:
            flash("❌ Invalid verification code.", "danger")

    return render_template('verify_code.html', title='Verify Code')

@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if not session.get('verified'):
        return redirect(url_for('forgot_password'))

    if request.method == 'POST':
        new_pass = request.form.get('new_password')
        confirm_pass = request.form.get('confirm_password')
        if new_pass == confirm_pass:
            email = session.get('reset_email')
            user = find_user_by_email(email)
            if user:
                db_reset_password(user, new_pass)
                flash("✅ Password successfully reset!", "success")
                session['reset_success'] = True  # Make sure this line is added
                return redirect(url_for('reset_password'))  # Redirect to show the success message
            else:
                flash("❌ User not found.", "danger")
        else:
            flash("❌ Passwords do not match.", "danger")

    reset_success = session.pop('reset_success', False)  # Pop it from the session
    return render_template('reset_password.html', title='Reset Password', reset_success=reset_success)

@app.route('/resend_code', methods=['POST'])
def resend_code():
    import random

    if 'email' not in session:
        flash('Session expired. Please try again.', 'danger')
        return redirect(url_for('forgot_password'))

    # Generate new code
    new_code = str(random.randint(100000, 999999))
    session['verification_code'] = new_code
    session['code_sent_time'] = datetime.now().timestamp()
    print(f"[Resent] Verification code sent to {session['email']}: {new_code}")
    flash('A new verification code has been sent to your email. (Check console)', 'info')
    return redirect(url_for('verify_code'))

@app.route('/upload_avatar', methods=['POST'])
@login_required
def upload_avatar():
    if 'avatar' not in request.files:
        flash('No file part', 'danger')
        return redirect(request.referrer or url_for('upload'))
    file = request.files['avatar']
    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(request.referrer or url_for('upload'))
    if file:
        filename = secure_filename(file.filename)
        avatar_folder = os.path.join(app.static_folder, 'avatars')
        os.makedirs(avatar_folder, exist_ok=True)
        file.save(os.path.join(avatar_folder, filename))
        # Save filename to user (make sure your User model has avatar_url)
        current_user.avatar_url = filename
        db.session.commit()
        flash('Avatar updated!', 'success')
    return redirect(request.referrer or url_for('upload'))

@app.route('/privacy-policy')
def privacy_policy():
    return render_template('privacy_policy.html', title="Privacy Policy")

@app.route('/terms-of-service')
def terms_of_service():
    return render_template('terms_of_service.html', title="Terms of Service")

@app.context_processor
def inject_current_year():
    return {'current_year': datetime.now().year}

# API endpoint for fitness ranking data
@app.route('/api/visualisation/ranking')
@login_required
def fitness_ranking():
    try:
        # Get the time range parameter (default to 'week')
        time_range = request.args.get('time_range', 'week')
        
        # Get the sort by parameter (default to 'calories')
        sort_by = request.args.get('sort_by', 'calories')
        
        # Calculate the start date based on the time range
        today = datetime.today().date()
        if time_range == 'week':
            start_date = today - timedelta(days=7)
        elif time_range == 'month':
            start_date = today - timedelta(days=30)
        elif time_range == 'year':
            start_date = today - timedelta(days=365)
        else:
            # Default to one week
            start_date = today - timedelta(days=7)

        # Query for fitness entries within the date range
        fitness_entries_query = db.session.query(
            User.username,
            db.func.sum(FitnessEntry.calories_burned).label('total_calories'),
            db.func.sum(FitnessEntry.duration).label('total_duration'),
            db.func.count(FitnessEntry.id).label('activity_count')
        ).join(
            FitnessEntry, User.id == FitnessEntry.user_id
        ).filter(
            FitnessEntry.date >= start_date
        ).group_by(
            User.username
        )
        
        # Apply ordering based on sort parameter
        if sort_by == 'duration':
            fitness_entries = fitness_entries_query.order_by(
                db.func.sum(FitnessEntry.duration).desc()
            ).all()
        elif sort_by == 'activity_count':
            fitness_entries = fitness_entries_query.order_by(
                db.func.count(FitnessEntry.id).desc()
            ).all()
        else:  # default to calories
            fitness_entries = fitness_entries_query.order_by(
                db.func.sum(FitnessEntry.calories_burned).desc()
            ).all()

        # Prepare the ranking data
        ranking_data = []
        for i, (username, total_calories, total_duration, activity_count) in enumerate(fitness_entries, 1):
            ranking_data.append({
                'rank': i,
                'username': username,
                'total_calories_burned': round(total_calories, 2) if total_calories else 0,
                'total_duration': round(total_duration, 2) if total_duration else 0,
                'activity_count': activity_count
            })

        # Highlight the current user in the rankings
        for entry in ranking_data:
            entry['is_current_user'] = (entry['username'] == current_user.username)

        return jsonify({
            'ranking': ranking_data, 
            'time_range': time_range,
            'sort_by': sort_by
        })
    
    except Exception as e:
        app.logger.error(f"Error in fitness ranking API: {str(e)}")
        return jsonify({'error': 'Failed to retrieve ranking data', 'details': str(e)}), 500

# API endpoint for fitness visualization data
@app.route('/api/visualisation/fitness')
@login_required
def fitness_visualization():
    try:
        # Get the user ID
        user_id = current_user.id
        
        # Get time range parameters (optional)
        days = request.args.get('days', default=30, type=int)
        
        # Calculate the start date
        end_date = datetime.today().date()
        start_date = end_date - timedelta(days=days)
        
        # Query fitness entries for the user within the time range
        fitness_entries = FitnessEntry.query.filter(
            FitnessEntry.user_id == user_id,
            FitnessEntry.date >= start_date,
            FitnessEntry.date <= end_date
        ).order_by(FitnessEntry.date).all()
        
        # Query food entries for the user within the time range
        food_entries = FoodEntry.query.filter(
            FoodEntry.user_id == user_id,
            FoodEntry.date >= start_date,
            FoodEntry.date <= end_date
        ).order_by(FoodEntry.date).all()
        
        # Prepare the fitness data for visualization
        fitness_data = []
        for entry in fitness_entries:
            fitness_data.append({
                'date': entry.date.isoformat(),
                'activity_type': entry.activity_type,
                'duration': entry.duration,
                'calories_burned': entry.calories_burned,
                'emotion': entry.emotion
            })
        
        # Prepare the food data for visualization
        food_data = []
        for entry in food_entries:
            food_data.append({
                'date': entry.date.isoformat(),
                'food_name': entry.food_name,
                'quantity': entry.quantity,
                'calories': entry.calories,
                'meal_type': entry.meal_type
            })
        
        # Prepare summary statistics
        total_calories_burned = sum(entry.calories_burned for entry in fitness_entries if entry.calories_burned)
        total_workout_minutes = sum(entry.duration for entry in fitness_entries if entry.duration)
        total_calories_consumed = sum(entry.calories for entry in food_entries if entry.calories)
        
        avg_daily_calories_burned = total_calories_burned / days if days > 0 else 0
        avg_daily_workout_minutes = total_workout_minutes / days if days > 0 else 0
        avg_daily_calories_consumed = total_calories_consumed / days if days > 0 else 0
        
        # Group activities by type
        activity_types = {}
        for entry in fitness_entries:
            if entry.activity_type:
                activity_types[entry.activity_type] = activity_types.get(entry.activity_type, 0) + 1
        
        # Sort activities by frequency
        sorted_activities = sorted(activity_types.items(), key=lambda x: x[1], reverse=True)
        top_activities = [{'type': k, 'count': v} for k, v in sorted_activities[:5]]
        
        # Return the compiled data
        return jsonify({
            'fitness_entries': fitness_data,
            'food_entries': food_data,
            'summary': {
                'total_calories_burned': round(total_calories_burned, 2),
                'total_workout_minutes': round(total_workout_minutes, 2),
                'total_calories_consumed': round(total_calories_consumed, 2),
                'avg_daily_calories_burned': round(avg_daily_calories_burned, 2),
                'avg_daily_workout_minutes': round(avg_daily_workout_minutes, 2),
                'avg_daily_calories_consumed': round(avg_daily_calories_consumed, 2),
                'calorie_balance': round(total_calories_consumed - total_calories_burned, 2),
                'top_activities': top_activities
            },
            'time_range': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days': days
            }
        })
    
    except Exception as e:
        app.logger.error(f"Error in fitness visualization API: {str(e)}")
        return jsonify({'error': 'Failed to retrieve visualization data', 'details': str(e)}), 500