# upload.py
from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import UserInfo, FitnessEntry, FoodEntry
from datetime import datetime, date

upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_page():
    if request.method == 'POST':
        if not current_user.is_authenticated:
            flash("User not authenticated", "danger")
            return redirect(url_for('login'))

        try:
            data = request.form
            user_id = current_user.id

            date_obj = datetime.strptime(data['date'], '%Y-%m-%d').date()
            time_obj = datetime.strptime(data['time'], '%H:%M').time()

            # Handle UserInfo
            user_info_record = UserInfo.query.filter_by(user_id=user_id).first()
            if user_info_record:
                user_info_record.date = date_obj
                user_info_record.time = time_obj
                user_info_record.gender = data.get('gender')
                user_info_record.age = int(data['age']) if data.get('age') else None
                user_info_record.height = float(data['height']) if data.get('height') else None
                user_info_record.weight = float(data['weight']) if data.get('weight') else None
            else:
                user_info_record = UserInfo(
                    user_id=user_id,
                    date=date_obj,
                    time=time_obj,
                    gender=data.get('gender'),
                    age=int(data['age']) if data.get('age') else None,
                    height=float(data['height']) if data.get('height') else None,
                    weight=float(data.get('weight') or 0.0)
                )
                db.session.add(user_info_record)

            # Fitness Entries
            activity_types = request.form.getlist('activity_type')
            durations = request.form.getlist('duration')
            burned = request.form.getlist('calories_burned')
            emotions = request.form.getlist('emotion')

            for i in range(len(activity_types)):
                if activity_types[i]:
                    db.session.add(FitnessEntry(
                        user_id=user_id,
                        date=date_obj,
                        activity_type=activity_types[i],
                        duration=float(durations[i]) if durations[i] else None,
                        calories_burned=float(burned[i]) if burned[i] else None,
                        emotion=emotions[i]
                    ))

            # Food Entries
            food_names = request.form.getlist('food_name')
            quantities = request.form.getlist('food_quantity')
            calories = request.form.getlist('food_calories')
            meal_types = request.form.getlist('meal_type')

            for i in range(len(food_names)):
                if food_names[i]:
                    db.session.add(FoodEntry(
                        user_id=user_id,
                        date=date_obj,
                        food_name=food_names[i],
                        quantity=float(quantities[i]) if quantities[i] else None,
                        calories=float(calories[i]) if calories[i] else None,
                        meal_type=meal_types[i]
                    ))

            db.session.commit()
            flash("✅ Upload successful!", "success")
            return redirect(url_for('upload.upload_page'))

        except Exception as e:
            db.session.rollback()
            flash(f"❌ Upload failed: {str(e)}", "danger")
            return redirect(url_for('upload.upload_page'))

    # GET method - show form
    user_info = UserInfo.query.filter_by(user_id=current_user.id).first()
    if not user_info:
        now = datetime.now()
        user_info = UserInfo(
            user_id=current_user.id,
            date=now.date(),
            time=now.time()
        )
        db.session.add(user_info)
        db.session.commit()

    now = datetime.now()
    return render_template(
        'upload.html', 
        title="Upload", 
        user_info=user_info,
        default_date=now.strftime('%Y-%m-%d'),
        default_time=now.strftime('%H:%M'),
        username=current_user.username,
        active_page='upload.upload_page'
    )
