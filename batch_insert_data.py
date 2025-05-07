\
import datetime
import random
from app import app, db
from app.models import UserInfo
from app.database import add_user_fitness_entry, upsert_user_food_entry

# Sample data for generation
sample_activities = ["Running", "Cycling", "Weightlifting", "Swimming", "Yoga", "Walking", "HIIT", "Pilates"]
sample_emotions = ["Happy", "Tired", "Energized", "Okay", "Stressed", "Relaxed"]
sample_foods = [
    "Chicken Breast", "Broccoli", "Brown Rice", "Salmon Fillet", "Mixed Salad", 
    "Apple", "Banana", "Oatmeal", "Scrambled Eggs", "Protein Shake", "Greek Yogurt",
    "Almonds", "Sweet Potato", "Quinoa", "Spinach", "Lentil Soup", "Tofu Stir-fry"
]
sample_meal_types = ["Breakfast", "Lunch", "Dinner", "Snack"]

USER_ID = 1

def create_batch_data():
    """
    Generates and inserts batch data for fitness and food entries for a specific user
    over a defined date range.
    """
    with app.app_context():
        # Check if the target user exists
        user = UserInfo.query.get(USER_ID)
        if not user:
            print(f"Error: User with ID {USER_ID} not found in the database.")
            print("Please create this user before running the script.")
            # Example: You might want to create a dummy user here if needed for full automation
            # from app.database import register_user # Assuming such a function exists
            # register_user(username=f"testuser{USER_ID}", email=f"test{USER_ID}@example.com", password="password",
            #               gender="Other", age=30, height=170, weight=70)
            # db.session.commit() # If register_user doesn't commit
            # user = UserInfo.query.get(USER_ID)
            # if not user:
            #     print("Failed to create dummy user. Exiting.")
            #     return
            # print(f"Created dummy user {USER_ID} for testing.")
            return

        print(f"Starting batch data insertion for User ID: {USER_ID}")

        start_date = datetime.date(2025, 4, 1)
        end_date = datetime.date(2025, 4, 30)
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
                        user_id=USER_ID,
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
                if i >= len(meal_types_for_day): # In case num_food_entries > len(sample_meal_types)
                    meal_type = random.choice(sample_meal_types) # Fallback to random if we need more entries than unique types
                else:
                    meal_type = meal_types_for_day[i]
                
                food_name = random.choice(sample_foods)
                quantity = round(random.uniform(50.0, 600.0), 1)  # Quantity in grams or ml
                calories = round(random.uniform(50.0, 1000.0), 1) # Calories for the food item
                
                try:
                    upsert_user_food_entry(
                        user_id=USER_ID,
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
            db.session.commit() # Commit any other potential changes if any
            print("\\nBatch data insertion process completed successfully.")
        except Exception as e:
            db.session.rollback()
            print(f"\\nAn error occurred during the final commit: {e}")

if __name__ == "__main__":
    print("Script execution started...")
    create_batch_data()
    print("Script execution finished.")
