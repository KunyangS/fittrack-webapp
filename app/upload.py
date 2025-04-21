from flask import Blueprint, render_template, request, redirect, flash
from app import app
upload_bp = Blueprint('upload', __name__)
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # Get form data
        date = request.form.get('date')
        time = request.form.get('time')
        gender = request.form.get('gender')
        age = request.form.get('age')
        height = request.form.get('height')
        weight = request.form.get('weight')
        activity_type = request.form.get('activity_type')
        duration = request.form.get('duration')
        calories_burned = request.form.get('calories_burned')
        emotion = request.form.get('emotion')
        food_name = request.form.get('food_name')
        food_quantity = request.form.get('food_quantity')
        food_calories = request.form.get('food_calories')
        meal_type = request.form.get('meal_type')

        # Save the data to the database here
        print(f"Received: {date}, {activity_type}, {food_name}")

        flash("Upload successful!", "success")
        return redirect('/upload')

    return render_template('upload.html', title='Upload Data')
