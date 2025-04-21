from flask import Blueprint, request, jsonify, render_template
from app import db
from app.models import UserInfo, FitnessEntry, FoodEntry
from datetime import datetime

upload_bp = Blueprint('upload', __name__)

# Page routing: for displaying HTML forms
@upload_bp.route('/upload', methods=['GET'])
def upload_page():
    return render_template('upload.html', title="Upload")

# API routing: used to receive JSON data and write to the database
@upload_bp.route('/api/upload', methods=['POST'])
def api_upload():
    try:
        data = request.get_json()

        date_obj = datetime.strptime(data['date'], '%Y-%m-%d').date()
        time_obj = datetime.strptime(data['time'], '%H:%M').time()

        user_info = UserInfo(
            date=date_obj,
            time=time_obj,
            gender=data['gender'],
            age=int(data['age']),
            height=float(data['height']),
            weight=float(data['weight']),
        )

        fitness_entry = FitnessEntry(
            date=date_obj,
            activity_type=data['activity_type'],
            duration=float(data['duration']),
            calories_burned=float(data['calories_burned']),
            emotion=data['emotion'],
        )

        food_entry = FoodEntry(
            date=date_obj,
            food_name=data['food_name'],
            quantity=float(data['food_quantity']),
            calories=float(data['food_calories']),
            meal_type=data['meal_type'],
        )

        db.session.add_all([user_info, fitness_entry, food_entry])
        db.session.commit()

        return jsonify({'success': True, 'message': 'Upload successful!'})

    except Exception as e:
        print("❌ Error:", e)
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Upload failed!'}), 500
