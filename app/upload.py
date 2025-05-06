from flask import Blueprint, request, jsonify, render_template
from app import db
from app.database import (
    update_user_profile_details,
    add_user_fitness_entry,
    upsert_user_food_entry,
    find_user_by_email
)
from app.models import UserInfo, FitnessEntry, FoodEntry
from datetime import datetime, date, time
from flask_login import current_user, login_required

upload_bp = Blueprint('upload', __name__)

# Page routing: for displaying HTML forms
@upload_bp.route('/upload', methods=['GET'])
@login_required
def upload_page():
    username = current_user.username if hasattr(current_user, 'username') else None
    return render_template('upload.html', title="Upload Data", username=username)

# API routing: used to receive JSON data and write to the database
@upload_bp.route('/api/upload', methods=['POST'])
@login_required
def api_upload():
    if not current_user.is_authenticated:
        return jsonify({'success': False, 'message': 'User not authenticated.'}), 401

    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No data provided or invalid JSON.'}), 400

        user_id = current_user.id
        operations_performed = []
        errors_occurred = []

        # Date is crucial for all entries. Time is optional for profile.
        date_str = data.get('date')
        time_str = data.get('time')  # Optional

        if not date_str:
            return jsonify({'success': False, 'message': 'Date is required for all entries.'}), 400

        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            time_obj = datetime.strptime(time_str, '%H:%M').time() if time_str else None
        except ValueError:
            return jsonify({'success': False, 'message': 'Invalid date or time format. Use YYYY-MM-DD for date and HH:MM for time.'}), 400

        # 1. UserInfo (Profile Update)
        profile_fields_present = {
            'gender': data.get('gender'),
            'age': data.get('age'),
            'height': data.get('height'),
            'weight': data.get('weight')
        }
        if any(value is not None and str(value).strip() != '' for value in profile_fields_present.values()):
            try:
                age_val = int(profile_fields_present['age']) if profile_fields_present['age'] not in [None, ''] else None
                height_val = float(profile_fields_present['height']) if profile_fields_present['height'] not in [None, ''] else None
                weight_val = float(profile_fields_present['weight']) if profile_fields_present['weight'] not in [None, ''] else None

                updated_user = update_user_profile_details(
                    user_id_to_update=user_id,
                    date_val=date_obj,
                    time_val=time_obj,
                    gender_val=profile_fields_present['gender'] if profile_fields_present['gender'] and str(profile_fields_present['gender']).strip() else None,
                    age_val=age_val,
                    height_val=height_val,
                    weight_val=weight_val
                )
                if updated_user:
                    operations_performed.append("User profile information updated.")
            except ValueError:
                errors_occurred.append("Invalid number format for age, height, or weight.")
            except Exception as e:
                errors_occurred.append(f"Error updating user profile: {str(e)}")

        # 2. Fitness Entries
        activities_data = data.get('activities')
        if isinstance(activities_data, list) and activities_data:
            for act in activities_data:
                activity_type = act.get('activity_type')
                duration_str = act.get('duration')
                calories_burned_str = act.get('calories_burned')
                emotion = act.get('emotion')

                if activity_type and str(activity_type).strip() and duration_str and calories_burned_str:
                    try:
                        duration_val = float(duration_str)
                        calories_burned_val = float(calories_burned_str)

                        add_user_fitness_entry(
                            user_id=user_id,
                            date_val=date_obj,
                            activity_type_val=str(activity_type).strip(),
                            duration_val=duration_val,
                            calories_burned_val=calories_burned_val,
                            emotion_val=str(emotion).strip() if emotion and str(emotion).strip() else None
                        )
                        operations_performed.append(f"Fitness entry for '{activity_type}' added.")
                    except ValueError:
                        errors_occurred.append(f"Invalid number format for duration or calories in activity '{activity_type}'.")
                    except Exception as e:
                        errors_occurred.append(f"Error adding fitness entry '{activity_type}': {str(e)}")
                elif activity_type or duration_str or calories_burned_str:
                    errors_occurred.append(f"Skipped fitness entry: Incomplete data (activity type, duration, and calories burned are required). Provided: Type='{activity_type}', Duration='{duration_str}', Calories='{calories_burned_str}'.")

        # 3. Food Entry
        food_name = data.get('food_name')
        quantity_str = data.get('food_quantity')
        calories_str = data.get('food_calories')
        meal_type = data.get('meal_type')

        if food_name and str(food_name).strip() and quantity_str and calories_str and meal_type and str(meal_type).strip():
            try:
                quantity_val = float(quantity_str)
                calories_val = float(calories_str)

                upsert_user_food_entry(
                    user_id=user_id,
                    date_val=date_obj,
                    food_name_val=str(food_name).strip(),
                    quantity_val=quantity_val,
                    calories_val=calories_val,
                    meal_type_val=str(meal_type).strip()
                )
                operations_performed.append(f"Food entry for '{food_name}' processed.")
            except ValueError:
                errors_occurred.append(f"Invalid number format for quantity or calories in food entry '{food_name}'.")
            except Exception as e:
                errors_occurred.append(f"Error processing food entry '{food_name}': {str(e)}")
        elif food_name or quantity_str or calories_str or meal_type:
            errors_occurred.append(f"Skipped food entry: Incomplete data (food name, quantity, calories, and meal type are required). Provided: Name='{food_name}', Qty='{quantity_str}', Cal='{calories_str}', Meal='{meal_type}'.")

        if not operations_performed and not errors_occurred:
            return jsonify({'success': False, 'message': 'No data sections were sufficiently filled to process. Please provide details for profile, fitness, or food entries.'}), 400

        response_message = ""
        if operations_performed:
            response_message += " Operations successful: " + "; ".join(operations_performed) + "."
        if errors_occurred:
            response_message += " Errors encountered: " + "; ".join(errors_occurred) + "."

        status_code = 200
        final_success_state = True
        if errors_occurred:
            status_code = 207
            if not operations_performed:
                final_success_state = False
                status_code = 400

        return jsonify({'success': final_success_state, 'message': response_message.strip()}), status_code

    except Exception as e:
        db.session.rollback()
        print(f"Critical Error in /api/upload: {e}")
        return jsonify({'success': False, 'message': f'An unexpected server error occurred: {str(e)}'}), 500

@upload_bp.route('/api/data', methods=['GET'])
@login_required
def get_all_data_for_user():
    if not current_user.is_authenticated:
        return jsonify({"error": "User not authenticated"}), 401

    user_id = current_user.id

    user_info = UserInfo.query.filter_by(id=user_id).first()
    fitness_entries = FitnessEntry.query.filter_by(user_id=user_id).all()
    food_entries = FoodEntry.query.filter_by(user_id=user_id).all()

    def serialize(model_instance):
        if not model_instance:
            return None
        result = {}
        for column in model_instance.__table__.columns:
            value = getattr(model_instance, column.name)
            if isinstance(value, (date, time)):
                value = value.isoformat()
            elif isinstance(value, datetime):
                value = value.isoformat()
            result[column.name] = value
        return result

    return jsonify({
        "user_info": serialize(user_info),
        "fitness_entries": [serialize(f) for f in fitness_entries],
        "food_entries": [serialize(food) for food in food_entries]
    })

@upload_bp.route('/api/visualisation/fitness', methods=['GET'])
@login_required
def visualisation_fitness_data_for_user():
    if not current_user.is_authenticated:
        return jsonify({"error": "User not authenticated"}), 401

    user_id = current_user.id
    fitness_entries = FitnessEntry.query.filter_by(user_id=user_id).order_by(FitnessEntry.date).all()

    return jsonify([
        {
            "date": entry.date.isoformat(),
            "activity_type": entry.activity_type,
            "duration": entry.duration,
            "calories_burned": entry.calories_burned,
            "emotion": entry.emotion
        }
        for entry in fitness_entries
    ])