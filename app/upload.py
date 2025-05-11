from flask import Blueprint, request, jsonify, render_template, redirect
from app import db
from app.models import UserInfo, FitnessEntry, FoodEntry
from datetime import datetime, date, time
from flask_login import current_user
from flask_login import login_required


upload_bp = Blueprint('upload', __name__)

# Page routing: for displaying HTML forms
@upload_bp.route('/upload', methods=['GET'])
@login_required
def upload_page():

    if not current_user or not current_user.is_authenticated:
        return redirect('/login')

    user_info = UserInfo.query.filter_by(user_id=current_user.id).first()

    if not user_info:
        user_info = UserInfo(
            user_id=current_user.id,
            date=date.today(),
            time=None,
            gender=None,
            age=None,
            height=None,
            weight=None
        )
        db.session.add(user_info)
        db.session.commit()
        
    now = datetime.now()
    return render_template('upload.html', title="Upload", user_info=user_info, active_page='upload.upload_page',username=current_user.username,default_date=now.strftime('%Y-%m-%d'), default_time=now.strftime('%H:%M'))


# API routing: used to receive JSON data and write to the database
@upload_bp.route('/api/upload', methods=['POST'])
def api_upload():
    if not current_user or not current_user.is_authenticated:
        return jsonify({'success': False, 'message': 'User not authenticated'}), 401

    try:
        data = request.get_json()
        user_id = current_user.id

        date_obj = datetime.strptime(data['date'], '%Y-%m-%d').date()
        time_obj = datetime.strptime(data['time'], '%H:%M').time()

        # Handle UserInfo: update if exists, create if not, and associate with user_id
        user_info_record = UserInfo.query.filter_by(user_id=user_id).first()
        if user_info_record:
            # Update existing UserInfo
            user_info_record.date = date_obj
            user_info_record.time = time_obj
            user_info_record.gender = data['gender']
            user_info_record.age = int(data['age']) if data.get('age') else None
            user_info_record.height = float(data['height']) if data.get('height') else None
            user_info_record.weight = float(data['weight']) if data.get('weight') else None
            # SQLAlchemy tracks changes, no explicit add needed for update
        else:
            # Create new UserInfo if it doesn't exist
            user_info_record = UserInfo(
                user_id=user_id,
                date=date_obj,
                time=time_obj,
                gender=data['gender'],
                age=int(data['age']) if data.get('age') else None,
                height=float(data['height']) if data.get('height') else None,
                weight=float(data['weight']) if data.get('weight') else None,
            )
            db.session.add(user_info_record)

        # FitnessEntry: Add user_id and prepare for batch add
        fitness_entries_to_add = []
        for act in data['activities']:
         if any([act.get('activity_type'), act.get('duration'), act.get('calories_burned'), act.get('emotion')]):

            fitness_entries_to_add.append(FitnessEntry(
                user_id=user_id,
                date=date_obj,
                activity_type=act['activity_type'],
                duration=float(act['duration']) if act.get('duration') else None,
                calories_burned=float(act['calories_burned']) if act.get('calories_burned') else None,
                emotion=act['emotion'],
            ))
        if fitness_entries_to_add:
            db.session.add_all(fitness_entries_to_add)

        food_names = request.form.getlist('food_name')
        quantities = request.form.getlist('food_quantity')
        calories = request.form.getlist('food_calories')
        meal_types = request.form.getlist('meal_type')

        for i in range(len(food_names)):
            if food_names[i]:
                db.session.add(FoodEntry(
                user_id=current_user.id,
                date=date_obj,
                food_name=food_names[i],
                quantity=float(quantities[i]) if quantities[i] else None,
                calories=float(calories[i]) if calories[i] else None,
                meal_type=meal_types[i]
            ))




        db.session.commit()

        return jsonify({'success': True, 'message': 'Upload successful!'})

    except Exception as e:
        print(f"❌ Error during API upload: {e}")  # Log specific error
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