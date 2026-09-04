"""
Database Seeding Script
Creates collections, indexes, and initial Admin & Analyst credentials in MongoDB.
"""
import os
import sys
import datetime

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.mongodb import get_db, create_indexes
from utils.auth import hash_password

def seed_database():
    print("Connecting to MongoDB...")
    db = get_db()
    if db is None:
        print("❌ Could not connect to MongoDB. Please ensure MongoDB service is running on localhost:27017.")
        return False

    print("Creating indexes...")
    create_indexes(db)

    # Seed Default Users
    users_col = db['users']
    
    # 1. Admin User
    admin_user = {
        "username": "admin",
        "email": "admin@earthscape.org",
        "password_hash": hash_password("admin123"),
        "role": "ADMIN",
        "created_at": datetime.datetime.utcnow().isoformat()
    }
    users_col.update_one({"username": "admin"}, {"$set": admin_user}, upsert=True)

    # 2. Analyst User
    analyst_user = {
        "username": "analyst",
        "email": "analyst@earthscape.org",
        "password_hash": hash_password("analyst123"),
        "role": "ANALYST",
        "created_at": datetime.datetime.utcnow().isoformat()
    }
    users_col.update_one({"username": "analyst"}, {"$set": analyst_user}, upsert=True)

    print("[SUCCESS] Seeded default users: 'admin' (password: admin123) and 'analyst' (password: analyst123).")
    return True

if __name__ == "__main__":
    seed_database()
