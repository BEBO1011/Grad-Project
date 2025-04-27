import os
import sys
import time

# Import the database modules
from database import init_db, Base, engine
from init_database import main as seed_data

def initialize_database():
    """Initialize and seed the database."""
    print("Starting database initialization...")
    
    # Initialize the database tables
    print("Creating database tables...")
    try:
        Base.metadata.create_all(engine)
        print("Database tables created successfully.")
    except Exception as e:
        print(f"Error creating database tables: {e}")
        sys.exit(1)
    
    # Seed the database with initial data
    print("Seeding database with initial data...")
    try:
        seed_data()
        print("Database seeded successfully.")
    except Exception as e:
        print(f"Error seeding database: {e}")
        sys.exit(1)
    
    print("Database initialization completed successfully.")

if __name__ == "__main__":
    initialize_database()