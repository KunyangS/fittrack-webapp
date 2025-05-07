from app import app, db
from app.models import UserInfo, FitnessEntry, FoodEntry
from tabulate import tabulate

# app = create_app() # This line is no longer needed as we import app directly

with app.app_context():
    print("\n--- UserInfo Table ---")
    users = UserInfo.query.all()
    if users:
        headers = ["ID", "Username", "Email", "Date", "Gender", "Age", "Height", "Weight"]
        user_data = [[user.id, user.username, user.email, user.date, user.gender, user.age, user.height, user.weight] for user in users]
        print(tabulate(user_data, headers=headers, tablefmt="fancy_grid"))
    else:
        print("  No data in UserInfo table.")

    print("\n--- FitnessEntry Table ---")
    fitness_entries = FitnessEntry.query.all()
    if fitness_entries:
        headers = ["ID", "User ID", "Date", "Activity", "Duration", "Calories Burned", "Emotion"]
        fitness_data = [[entry.id, entry.user_id, entry.date, entry.activity_type, entry.duration, entry.calories_burned, entry.emotion] for entry in fitness_entries]
        print(tabulate(fitness_data, headers=headers, tablefmt="fancy_grid"))
    else:
        print("  No data in FitnessEntry table.")

    print("\n--- FoodEntry Table ---")
    food_entries = FoodEntry.query.all()
    if food_entries:
        headers = ["ID", "User ID", "Date", "Food", "Quantity", "Calories", "Meal Type"]
        food_data = [[entry.id, entry.user_id, entry.date, entry.food_name, entry.quantity, entry.calories, entry.meal_type] for entry in food_entries]
        print(tabulate(food_data, headers=headers, tablefmt="fancy_grid"))
    else:
        print("  No data in FoodEntry table.")

print("\nScript finished.")
