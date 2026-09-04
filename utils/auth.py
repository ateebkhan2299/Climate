"""
Authentication and User Management Module
Supports bcrypt password hashing and session management for Streamlit.
"""
import bcrypt
from pymongo import MongoClient

def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against its bcrypt hash."""
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False

def authenticate_user(db, username: str, password: str):
    """
    Authenticate user against MongoDB 'users' collection.
    Returns user document if valid, else None.
    """
    user = db['users'].find_one({'username': username})
    if user and verify_password(password, user.get('password_hash', '')):
        return user
    return None
