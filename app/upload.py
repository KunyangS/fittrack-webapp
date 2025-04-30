from flask import Blueprint, request, jsonify, render_template
from app import db
from app.models import UserInfo, FitnessEntry, FoodEntry
from datetime import datetime, date, time


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

        fitness_entry = []
        for act in data['activities']:
            fitness_entry.append(FitnessEntry(
                date=date_obj,
                activity_type=act['activity_type'],
                duration=float(act['duration']),
                calories_burned=float(act['calories_burned']),
                emotion=act['emotion'],
            ))


        food_entry = FoodEntry(
            date=date_obj,
            food_name=data['food_name'],
            quantity=float(data['food_quantity']),
            calories=float(data['food_calories']),
            meal_type=data['meal_type'],
        )

        db.session.add_all([user_info, *fitness_entry, food_entry])
        db.session.commit()

        return jsonify({'success': True, 'message': 'Upload successful!'})

    except Exception as e:
        print("❌ Error:", e)
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Upload failed!'}), 500

@upload_bp.route('/api/data', methods=['GET'])
def get_all_data():
    all_userinfo = UserInfo.query.all()
    all_fitness = FitnessEntry.query.all()
    all_food = FoodEntry.query.all()

    def serialize(model):
        result = {}
        for column in model.__table__.columns:
            value = getattr(model, column.name)
            if isinstance(value, (date, time)):
                value = value.isoformat()
            result[column.name] = value
        return result

    return jsonify({
        "user_info": [serialize(u) for u in all_userinfo],
        "fitness_entries": [serialize(f) for f in all_fitness],
        "food_entries": [serialize(food) for food in all_food]
    })

@upload_bp.route('/api/visualisation/fitness', methods=['GET'])
def visualisation_fitness_data():
    fitness = FitnessEntry.query.all()
    return jsonify([
        {
            "date": entry.date.isoformat(),
            "activity_type": entry.activity_type,
            "duration": entry.duration,
            "calories_burned": entry.calories_burned,
            "emotion": entry.emotion
        }
        for entry in fitness
    ])