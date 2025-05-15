import datetime
import random
from app import app, db
from app.models import User
from batch_insert_data import create_batch_data
from app.database import register_user

def generate_ranking_data():
    """
    Generate data for at least 10 users to make the ranking feature functional.
    Creates users if they don't exist and adds fitness and food data for each user.
    """
    print("Starting ranking data generation...")
    
    with app.app_context():
        # Define users to create (at least 10)
        users_to_create = [
            {"username": "Alex", "email": "alex@example.com", "gender": "Male", "age": 28, "height": 180.0, "weight": 75.0},
            {"username": "Emma", "email": "emma@example.com", "gender": "Female", "age": 26, "height": 168.0, "weight": 61.0},
            {"username": "Michael", "email": "michael@example.com", "gender": "Male", "age": 32, "height": 185.0, "weight": 82.0},
            {"username": "Sophia", "email": "sophia@example.com", "gender": "Female", "age": 24, "height": 165.0, "weight": 58.0},
            {"username": "Daniel", "email": "daniel@example.com", "gender": "Male", "age": 30, "height": 178.0, "weight": 79.0},
            {"username": "Olivia", "email": "olivia@example.com", "gender": "Female", "age": 27, "height": 170.0, "weight": 63.0},
            {"username": "William", "email": "william@example.com", "gender": "Male", "age": 35, "height": 183.0, "weight": 88.0},
            {"username": "Ava", "email": "ava@example.com", "gender": "Female", "age": 29, "height": 172.0, "weight": 65.0},
            {"username": "James", "email": "james@example.com", "gender": "Male", "age": 31, "height": 179.0, "weight": 77.0},
            {"username": "Isabella", "email": "isabella@example.com", "gender": "Female", "age": 25, "height": 167.0, "weight": 60.0},
            {"username": "Benjamin", "email": "benjamin@example.com", "gender": "Male", "age": 33, "height": 182.0, "weight": 80.0},
            {"username": "Mia", "email": "mia@example.com", "gender": "Female", "age": 28, "height": 169.0, "weight": 62.0}
        ]
        
        # Create or get existing users
        users = []
        for user_data in users_to_create:
            # Check if user already exists
            user = User.query.filter_by(username=user_data["username"]).first()
            
            if not user:
                # Create new user
                user = register_user(
                    username=user_data["username"],
                    email=user_data["email"],
                    password="test1234",  # Using the same password for all test users
                    gender=user_data["gender"],
                    age=user_data["age"],
                    height=user_data["height"],
                    weight=user_data["weight"]
                )
                if user:
                    print(f"Created user: {user.username} (ID: {user.id})")
                else:
                    print(f"Failed to create user: {user_data['username']}")
                    continue
            else:
                print(f"User already exists: {user.username} (ID: {user.id})")
            
            users.append(user)
        
        # Generate varied fitness and food data for all users
        year = 2025
        for user in users:
            # Define date ranges with varying activity levels
            date_ranges = [
                # Each user gets a different activity pattern over several months
                {
                    "start_date": datetime.date(year, 1, 1),
                    "end_date": datetime.date(year, 1, 31)
                },
                {
                    "start_date": datetime.date(year, 2, 1),
                    "end_date": datetime.date(year, 2, 28)
                },
                {
                    "start_date": datetime.date(year, 3, 1),
                    "end_date": datetime.date(year, 3, 31)
                },
                {
                    "start_date": datetime.date(year, 4, 1),
                    "end_date": datetime.date(year, 4, 30)
                },
                {
                    "start_date": datetime.date(year, 5, 1),
                    "end_date": datetime.date(year, 5, 15)
                }
            ]
            
            # Randomize which months to generate data for - some users will have more data than others
            user_date_ranges = random.sample(date_ranges, random.randint(3, 5))
            
            print(f"Generating data for {user.username}...")
            for date_range in user_date_ranges:
                print(f"  - Period: {date_range['start_date']} to {date_range['end_date']}")
                create_batch_data(user.id, date_range["start_date"], date_range["end_date"])
        
        print("\nRanking data generation completed. At least 10 users with fitness data created.")
        print("\nUser summary:")
        for user in users:
            print(f"  - {user.username} (ID: {user.id}, Email: {user.email})")

if __name__ == "__main__":
    generate_ranking_data() 