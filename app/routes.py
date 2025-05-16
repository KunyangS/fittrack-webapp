# routes.py
from datetime import datetime, timedelta, date
from flask import render_template, request, session, redirect, url_for, flash, jsonify, abort
from app import app, db, login_manager
from flask_login import login_user as flask_login_user, logout_user, login_required, current_user
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

# Helper function to map category keys to display names
category_map = {
    'basic_profile': 'Basic Profile',
    'activity_summary': 'Activity Summary',
    'activity_log': 'Activity Log',
    'meal_log': 'Meal Log',
    'daily_nutrition': 'Daily Nutrition Summary',
    'mood_entries': 'Mood Entries',
    'fitness_ranking': 'Fitness Ranking'
}

# Helper function to map time range keys to display names
time_map = {
    'last_7_days': 'Last 7 Days',
    'last_30_days': 'Last 30 Days',
    'all_time': 'All Time'
}

# Helper function to calculate shared data window
def get_share_window(share_entry_time_range: str, share_creation_date: date):
    """
    Calculates the absolute start and end dates for a shared data window.
    The window is defined relative to the share_creation_date.
    """
    end_date_obj = share_creation_date
    start_date_obj = None

    if share_entry_time_range == 'last_7_days':
        start_date_obj = end_date_obj - timedelta(days=6)
    elif share_entry_time_range == 'last_30_days':
        start_date_obj = end_date_obj - timedelta(days=29)
    elif share_entry_time_range == 'all_time':
        pass
    else:
        start_date_obj = end_date_obj - timedelta(days=6)

    return start_date_obj.isoformat() if start_date_obj else None, end_date_obj.isoformat()

# Route for Data Visualisation page (placeholder)
@app.route('/visualise')
@login_required
def visualise():
    try:
        conn = sqlite3.connect("instance/fitness.db")

        fitness_df = pd.read_sql_query(
            "SELECT id, user_id, date, activity_type, duration, calories_burned, emotion FROM fitness_entries WHERE user_id = ?", 
            conn, params=(current_user.id,))
        
        food_df = pd.read_sql_query(
            "SELECT id, user_id, date, food_name, quantity, calories, meal_type FROM food_entries WHERE user_id = ?", 
            conn, params=(current_user.id,))

        fitness_data = fitness_df.to_dict(orient='records')
        food_data = food_df.to_dict(orient='records')

        conn.close()

        print(f"Fetched {len(fitness_data)} fitness entries and {len(food_data)} food entries for user {current_user.username}")

    except Exception as e:
        print(f"Error fetching data: {e}")
        return render_template('error.html', error_message="Database error occurred")

    return render_template(
        'visualise.html',
        username=current_user.username,
        fitness_data=fitness_data,
        food_data=food_data,
        is_viewing_shared_data=False, # Default for own data view
        show_activity_log=True, # Default for own data view
        show_meal_log=True # Default for own data view
    )

@app.route('/api/delete_entry/<string:entry_type>/<int:entry_id>', methods=['DELETE'])
@login_required
def delete_entry(entry_type, entry_id):
    conn = None
    try:
        conn = sqlite3.connect("instance/fitness.db")
        cursor = conn.cursor()

        if entry_type == 'fitness':
            cursor.execute("DELETE FROM fitness_entries WHERE id = ? AND user_id = ?", (entry_id, current_user.id))
        elif entry_type == 'food':
            cursor.execute("DELETE FROM food_entries WHERE id = ? AND user_id = ?", (entry_id, current_user.id))
        else:
            return jsonify({'error': 'Invalid entry type'}), 400

        conn.commit()

        if cursor.rowcount > 0:
            return jsonify({'message': 'Entry deleted successfully'}), 200
        else:
            return jsonify({'error': 'Entry not found or not authorized to delete'}), 404

    except sqlite3.Error as e:
        print(f"SQLite error during delete operation: {e}")
        return jsonify({'error': 'Database error during deletion', 'details': str(e)}), 500
    except Exception as e:
        print(f"Unexpected error during delete operation: {e}")
        return jsonify({'error': 'An unexpected error occurred', 'details': str(e)}), 500
    finally:
        if conn:
            conn.close()

# Route for Data Sharing page
@app.route('/share', methods=['GET', 'POST'])
@login_required
def share():
    category_map = {
        'basic_profile': 'Basic Profile',
        'fitness_log': 'Activity Log',
        'food_log': 'Meal Log',
        'activity_summary': 'Activity Summary',
        'daily_nutrition': 'Daily Nutrition Summary',
        'mood_entries': 'Mood Entries',
        'fitness_ranking': 'Fitness Ranking'
    }
    time_map = {
        'last_7_days': 'Last 7 Days',
        'last_30_days': 'Last 30 Days',
        'all_time': 'All Time',
    }

    if request.method == 'POST':
        recipient_username_or_email = request.form.get('share_users')
        data_categories_list_from_form = sorted(list(set(request.form.getlist('share_options'))))
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

            if new_categories_from_form_set.issubset(current_categories_in_db_set) and new_time_range_key == current_time_range_in_db:
                requested_display_categories = [category_map.get(cat, cat) for cat in data_categories_list_from_form]
                display_time_range = time_map.get(new_time_range_key, new_time_range_key)
                flash(f"Data including the selected categories ({', '.join(requested_display_categories)}) is already shared with {recipient.username} for the time range {display_time_range}.", 'info')
            else:
                combined_categories_set = current_categories_in_db_set.union(new_categories_from_form_set)
                final_categories_str = ','.join(sorted(list(combined_categories_set)))
                
                actually_added_category_keys = combined_categories_set - current_categories_in_db_set
                time_range_updated = new_time_range_key != current_time_range_in_db

                existing_active_share.data_categories = final_categories_str
                existing_active_share.time_range = new_time_range_key
                existing_active_share.shared_at = datetime.utcnow()
                db.session.commit()

                update_messages = []
                if actually_added_category_keys:
                    added_display_names = [category_map.get(cat, cat) for cat in sorted(list(actually_added_category_keys))]
                    update_messages.append(f"Added data categories: {', '.join(added_display_names)}")
                
                if time_range_updated:
                    display_new_time_range = time_map.get(new_time_range_key, new_time_range_key)
                    update_messages.append(f"Time range updated to {display_new_time_range}")
                
                if not update_messages and not actually_added_category_keys and not time_range_updated:
                    flash(f"Share with {recipient.username} is already up to date with the requested settings.", 'info')
                else:
                    flash(f"Share with {recipient.username} updated. {'. '.join(update_messages)}.", 'success')
        else:
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
            'shared_at': entry.shared_at.strftime('%Y-%m-%d %H:%M'),
            'share_id': entry.id
        })

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
            'status': 'Revoked'
        })

    return render_template('share.html', current_shares=current_shares, username=current_user.username, shared_with_you=shared_with_you_data, share_history=share_history_data)

@app.route('/view_shared_data/<int:share_id>')
@login_required
def view_shared_data(share_id):
    share_entry = ShareEntry.query.get_or_404(share_id)

    if not (share_entry.sharee_user_id == current_user.id and share_entry.is_active):
        flash('You are not authorized to view this shared data or the share is inactive.', 'danger')
        return redirect(url_for('share'))

    sharer = User.query.get(share_entry.sharer_user_id)
    if not sharer:
        flash('Sharer user not found.', 'danger')
        return redirect(url_for('share'))

    effective_start_date_str, effective_end_date_str = get_share_window(
        share_entry.time_range,
        share_entry.shared_at.date()
    )

    fitness_data = []
    food_data = []

    try:
        conn = sqlite3.connect("instance/fitness.db")
        fitness_query = "SELECT id, user_id, date, activity_type, duration, calories_burned, emotion FROM fitness_entries WHERE user_id = ?"
        params = [sharer.id]

        if effective_start_date_str and share_entry.time_range != 'all_time':
            fitness_query += " AND date >= ?"
            params.append(effective_start_date_str)
        fitness_query += " AND date <= ?"
        params.append(effective_end_date_str)
        
        fitness_df = pd.read_sql_query(fitness_query, conn, params=tuple(params))
        fitness_df['date'] = pd.to_datetime(fitness_df['date']).dt.strftime('%Y-%m-%d')

        food_query = "SELECT id, user_id, date, food_name, quantity, calories, meal_type FROM food_entries WHERE user_id = ?"
        food_params = [sharer.id]

        if effective_start_date_str and share_entry.time_range != 'all_time':
            food_query += " AND date >= ?"
            food_params.append(effective_start_date_str)
        food_query += " AND date <= ?"
        food_params.append(effective_end_date_str)

        food_df = pd.read_sql_query(food_query, conn, params=tuple(food_params))
        food_df['date'] = pd.to_datetime(food_df['date']).dt.strftime('%Y-%m-%d')

        conn.close()

        actual_min_date_fitness = fitness_df['date'].min() if not fitness_df.empty else None
        actual_min_date_food = food_df['date'].min() if not food_df.empty else None
        
        all_actual_min_dates = [d for d in [actual_min_date_fitness, actual_min_date_food] if d]
        final_effective_start_date = effective_start_date_str
        if share_entry.time_range == 'all_time':
            final_effective_start_date = min(all_actual_min_dates) if all_actual_min_dates else effective_end_date_str

        fitness_data = fitness_df.to_dict(orient='records')
        food_data = food_df.to_dict(orient='records')

    except Exception as e:
        print(f"Error fetching shared data: {e}")
        flash('Could not load shared data due to a database error.', 'danger')
        return redirect(url_for('share'))

    shared_categories = set(share_entry.data_categories.split(','))

    show_basic_profile = 'basic_profile' in shared_categories
    show_activity_summary = 'activity_summary' in shared_categories
    show_activity_log = 'activity_log' in shared_categories
    show_meal_log = 'meal_log' in shared_categories
    show_daily_nutrition_summary = 'daily_nutrition' in shared_categories
    show_mood_entries = 'mood_entries' in shared_categories

    return render_template(
        'visualise.html',
        username=current_user.username,
        fitness_data=fitness_data,
        food_data=food_data,
        is_viewing_shared_data=True,
        sharer_username=sharer.username,
        effective_start_date_str=final_effective_start_date if share_entry.time_range == 'all_time' else effective_start_date_str,
        effective_end_date_str=effective_end_date_str,
        show_basic_profile=show_basic_profile,
        show_activity_summary=show_activity_summary,
        show_activity_log=show_activity_log,
        show_meal_log=show_meal_log,
        show_daily_nutrition_summary=show_daily_nutrition_summary,
        show_mood_entries=show_mood_entries,
        title=f"Data from {sharer.username}"
    )

@app.route('/revoke_share/<int:share_id>', methods=['POST'])
@login_required
def revoke_share(share_id):
    success = revoke_share_entry(share_id, current_user.id)
    if success:
        flash('Share revoked successfully.', 'success')
    else:
        flash('Failed to revoke share. Ensure you are the owner or the share exists.', 'danger')
    return redirect(url_for('share'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('upload.upload_page'))

    if request.method == 'POST':
        input_value = request.form.get('email')
        password = request.form.get('password')

        user = db_login_user(input_value, password)

        if user:
            flask_login_user(user)
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
                session['reset_success'] = True
                return redirect(url_for('reset_password'))
            else:
                flash("❌ User not found.", "danger")
        else:
            flash("❌ Passwords do not match.", "danger")

    reset_success = session.pop('reset_success', False)
    return render_template('reset_password.html', title='Reset Password', reset_success=reset_success)

@app.route('/resend_code', methods=['POST'])
def resend_code():
    if 'email' not in session:
        flash('Session expired. Please try again.', 'danger')
        return redirect(url_for('forgot_password'))

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
        current_user.avatar_url = filename
        db.session.commit()
        flash('Avatar updated!', 'success')
    return redirect(request.referrer or url_for('upload.upload_page'))

@app.route('/privacy-policy')
def privacy_policy():
    return render_template('privacy_policy.html', title="Privacy Policy")

@app.route('/terms-of-service')
def terms_of_service():
    return render_template('terms_of_service.html', title="Terms of Service")

@app.context_processor
def inject_current_year():
    return {'current_year': datetime.now().year}

@app.route('/api/visualisation/ranking')
@login_required
def fitness_ranking():
    try:
        time_range = request.args.get('time_range', 'week')
        sort_by = request.args.get('sort_by', 'calories')
        
        today = datetime.today().date()
        if time_range == 'week':
            start_date = today - timedelta(days=7)
        elif time_range == 'month':
            start_date = today - timedelta(days=30)
        elif time_range == 'year':
            start_date = today - timedelta(days=365)
        else:
            start_date = today - timedelta(days=7)

        sharer_ids_who_shared_ranking = db.session.query(ShareEntry.sharer_user_id)\
            .filter(ShareEntry.sharee_user_id == current_user.id)\
            .filter(ShareEntry.is_active == True)\
            .filter(ShareEntry.data_categories.contains('fitness_ranking'))\
            .distinct().all()

        allowed_sharer_ids = [item[0] for item in sharer_ids_who_shared_ranking]
        user_ids_for_ranking = list(set([current_user.id] + allowed_sharer_ids))

        fitness_entries_query = db.session.query(
            User.username,
            User.id.label('user_id'),
            db.func.sum(FitnessEntry.calories_burned).label('total_calories'),
            db.func.sum(FitnessEntry.duration).label('total_duration'),
            db.func.count(FitnessEntry.id).label('activity_count')
        ).join(
            FitnessEntry, User.id == FitnessEntry.user_id
        ).filter(
            User.id.in_(user_ids_for_ranking)
        ).filter(
            FitnessEntry.date >= start_date
        ).group_by(
            User.username, User.id
        )
        
        if sort_by == 'duration':
            fitness_entries = fitness_entries_query.order_by(
                db.func.sum(FitnessEntry.duration).desc()
            ).all()
        elif sort_by == 'activity_count':
            fitness_entries = fitness_entries_query.order_by(
                db.func.count(FitnessEntry.id).desc()
            ).all()
        else:
            fitness_entries = fitness_entries_query.order_by(
                db.func.sum(FitnessEntry.calories_burned).desc()
            ).all()

        ranking_data = []
        for i, (username, user_id_in_ranking, total_calories, total_duration, activity_count) in enumerate(fitness_entries, 1):
            ranking_data.append({
                'rank': i,
                'username': username,
                'total_calories_burned': round(total_calories, 2) if total_calories else 0,
                'total_duration': round(total_duration, 2) if total_duration else 0,
                'activity_count': activity_count,
                'is_current_user': (user_id_in_ranking == current_user.id)
            })

        return jsonify({
            'ranking': ranking_data, 
            'time_range': time_range,
            'sort_by': sort_by
        })
    
    except Exception as e:
        app.logger.error(f"Error in fitness ranking API: {str(e)}")
        return jsonify({'error': 'Failed to retrieve ranking data', 'details': str(e)}), 500

@app.route('/api/visualisation/fitness')
@login_required
def fitness_visualization():
    try:
        user_id = current_user.id
        days = request.args.get('days', default=30, type=int)
        end_date = datetime.today().date()
        start_date = end_date - timedelta(days=days)
        
        fitness_entries = FitnessEntry.query.filter(
            FitnessEntry.user_id == user_id,
            FitnessEntry.date >= start_date,
            FitnessEntry.date <= end_date
        ).order_by(FitnessEntry.date).all()
        
        food_entries = FoodEntry.query.filter(
            FoodEntry.user_id == user_id,
            FoodEntry.date >= start_date,
            FoodEntry.date <= end_date
        ).order_by(FoodEntry.date).all()
        
        fitness_data = []
        for entry in fitness_entries:
            fitness_data.append({
                'date': entry.date.isoformat(),
                'activity_type': entry.activity_type,
                'duration': entry.duration,
                'calories_burned': entry.calories_burned,
                'emotion': entry.emotion
            })
        
        food_data = []
        for entry in food_entries:
            food_data.append({
                'date': entry.date.isoformat(),
                'food_name': entry.food_name,
                'quantity': entry.quantity,
                'calories': entry.calories,
                'meal_type': entry.meal_type
            })
        
        total_calories_burned = sum(entry.calories_burned for entry in fitness_entries if entry.calories_burned)
        total_workout_minutes = sum(entry.duration for entry in fitness_entries if entry.duration)
        total_calories_consumed = sum(entry.calories for entry in food_entries if entry.calories)
        
        avg_daily_calories_burned = total_calories_burned / days if days > 0 else 0
        avg_daily_workout_minutes = total_workout_minutes / days if days > 0 else 0
        avg_daily_calories_consumed = total_calories_consumed / days if days > 0 else 0
        
        activity_types = {}
        for entry in fitness_entries:
            if entry.activity_type:
                activity_types[entry.activity_type] = activity_types.get(entry.activity_type, 0) + 1
        
        sorted_activities = sorted(activity_types.items(), key=lambda x: x[1], reverse=True)
        top_activities = [{'type': k, 'count': v} for k, v in sorted_activities[:5]]
        
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