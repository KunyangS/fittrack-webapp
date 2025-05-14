from app import app, db
from app.models import User, UserInfo, FitnessEntry, FoodEntry, ShareEntry

def init_db():
    """Initialize the database by creating all tables."""
    print("Creating database tables...")
    with app.app_context():
        db.create_all()
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_db() 