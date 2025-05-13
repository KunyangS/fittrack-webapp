import datetime
import random
from app import app, db
from app.models import UserInfo, User
from app.database import add_user_fitness_entry, upsert_user_food_entry

# Sample data for generation
sample_activities = [
    "Running", "Cycling", "Weightlifting", "Swimming", "Yoga", "Walking", "HIIT", "Pilates",
    "Basketball", "Football", "Tennis", "Badminton", "Rowing", "Boxing", "Dancing", "Climbing",
    "Jump Rope", "Skateboarding", "Skiing", "Snowboarding", "Surfing", "Golf", "Table Tennis", "Volleyball",
    "Martial Arts", "Horse Riding", "Archery", "Fencing", "Kayaking", "Hiking", "Trail Running", "Rollerblading"
]
sample_emotions = ["Happy", "Tired", "Energized", "Okay", "Stressed", "Relaxed"]
sample_foods = [
    "Chicken Breast", "Broccoli", "Brown Rice", "Salmon Fillet", "Mixed Salad", 
    "Apple", "Banana", "Oatmeal", "Scrambled Eggs", "Protein Shake", "Greek Yogurt",
    "Almonds", "Sweet Potato", "Quinoa", "Spinach", "Lentil Soup", "Tofu Stir-fry"
]
sample_meal_types = ["Breakfast", "Lunch", "Dinner", "Snack"]

def create_batch_data(target_user_id, start_date, end_date):
    """
    Generates and inserts batch data for fitness and food entries for a specific user
    over a defined date range.
    """
    with app.app_context():
        # Check if the target user exists in the User table
        target_user_record = User.query.get(target_user_id)
        if not target_user_record:
            print(f"Error: User with ID {target_user_id} not found in the 'users' table.")
            print("Please ensure a user with this ID exists in the 'users' table before running the script.")
            return

        print(f"Starting batch data insertion for User ID: {target_user_id} (Username: {target_user_record.username})")

        delta = datetime.timedelta(days=1)
        current_date = start_date
        while current_date <= end_date:
            print(f"Processing data for date: {current_date.strftime('%Y-%m-%d')}")

            # 1. Add Fitness Entries (1 to 3 per day)
            num_fitness_entries = random.randint(1, 3)
            for i in range(num_fitness_entries):
                activity = random.choice(sample_activities)
                duration = round(random.uniform(15.0, 120.0), 1)  # Duration in minutes
                calories_burned = round(random.uniform(50.0, 800.0), 1)
                emotion = random.choice(sample_emotions)
                
                try:
                    entry = add_user_fitness_entry(
                        user_id=target_user_id,
                        date_val=current_date,
                        activity_type_val=activity,
                        duration_val=duration,
                        calories_burned_val=calories_burned,
                        emotion_val=emotion
                    )
                    # print(f"  Added Fitness: {activity}, {duration}min, {calories_burned}kcal, Emotion: {emotion}")
                except Exception as e:
                    db.session.rollback()
                    print(f"  Error adding fitness entry for {current_date}, {activity}: {e}")

            # 2. Add Food Entries (2 to 4 per day, trying unique meal types)
            num_food_entries = random.randint(2, 4)
            
            # Ensure we try to use distinct meal types for the day if possible
            meal_types_for_day = random.sample(sample_meal_types, min(num_food_entries, len(sample_meal_types)))
            
            for i in range(num_food_entries):
                if i >= len(meal_types_for_day):  # In case num_food_entries > len(sample_meal_types)
                    meal_type = random.choice(sample_meal_types)  # Fallback to random if we need more entries than unique types
                else:
                    meal_type = meal_types_for_day[i]
                
                food_name = random.choice(sample_foods)
                quantity = round(random.uniform(50.0, 600.0), 1)  # Quantity in grams or ml
                calories = round(random.uniform(50.0, 1000.0), 1)  # Calories for the food item
                
                try:
                    upsert_user_food_entry(
                        user_id=target_user_id,
                        date_val=current_date,
                        food_name_val=food_name,
                        quantity_val=quantity,
                        calories_val=calories,
                        meal_type_val=meal_type
                    )
                    # print(f"  Upserted Food: {meal_type} - {food_name}, {quantity}g/ml, {calories}kcal")
                except Exception as e:
                    db.session.rollback()
                    print(f"  Error upserting food entry for {current_date}, {meal_type}, {food_name}: {e}")
            
            current_date += delta
        
        # The individual DB functions (add_user_fitness_entry, upsert_user_food_entry)
        # already commit the session. So, a final commit here is not strictly necessary
        # unless there are other operations outside those calls that need committing.
        # However, it's good practice if you modify those functions later.
        try:
            db.session.commit()  # Commit any other potential changes if any
            print("\nBatch data insertion process completed successfully.")
        except Exception as e:
            db.session.rollback()
            print(f"\nAn error occurred during the final commit: {e}")

if __name__ == "__main__":
    print("Script execution started...")
    with app.app_context():
        users = User.query.all()
        if not users:
            print("No users found in the database. Please register a user first.")
            exit(1)
        print("Available users:")
        for user in users:
            print(f"  ID: {user.id}  Username: {user.username}")
    user_id_to_process = 1  # Default USER_ID

    try:
        raw_input = input(f"Enter User ID to inject data into (default: {user_id_to_process}): ")
        if raw_input.strip() == "":
            print(f"No User ID provided. Defaulting to User ID {user_id_to_process}.")
        else:
            user_id_to_process = int(raw_input)
            print(f"Targeting User ID from user input: {user_id_to_process}")
    except ValueError:
        print(f"Invalid User ID provided: '{raw_input}'. Must be an integer. Defaulting to User ID {user_id_to_process}.")

    # Ask for month range
    month_input = input("Enter month or month range to insert (e.g. 4 or 1-5, default: 4): ").strip()
    if month_input == "":
        month_start, month_end = 4, 4
    elif "-" in month_input:
        try:
            month_start, month_end = map(int, month_input.split("-"))
        except Exception:
            print("Invalid month range, defaulting to April.")
            month_start, month_end = 4, 4
    else:
        try:
            month_start = month_end = int(month_input)
        except Exception:
            print("Invalid month, defaulting to April.")
            month_start, month_end = 4, 4

    # Calculate date range
    year = 2025
    start_date = datetime.date(year, month_start, 1)
    # Calculate end_date as the last day of month_end
    if month_end == 12:
        end_date = datetime.date(year, 12, 31)
    else:
        end_date = datetime.date(year, month_end + 1, 1) - datetime.timedelta(days=1)

    print(f"Inserting data from {start_date} to {end_date} ...")
    create_batch_data(user_id_to_process, start_date, end_date)
    print("Script execution finished.")
