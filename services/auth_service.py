"""
Authentication service.
Handles login, password hashing, and session state.
"""

import bcrypt
from models.user_model import get_user_by_username


# Simple session state (single-user desktop app)
_current_user = None


def hash_password(plain_password):
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(plain_password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password, hashed_password):
    """Verify a plain password against a bcrypt hash."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


def login(username, password):
    """
    Attempt to log in.
    Returns (success: bool, message: str).
    """
    global _current_user

    if not username or not username.strip():
        return False, "Username is required."
    if not password:
        return False, "Password is required."

    user = get_user_by_username(username.strip())
    if user is None:
        return False, "Invalid username or password."

    if not verify_password(password, user["password_hash"]):
        return False, "Invalid username or password."

    _current_user = user
    return True, f"Welcome, {user['username']}!"


def logout():
    """Clear the current session."""
    global _current_user
    _current_user = None


def get_current_user():
    """Get the currently logged-in user."""
    return _current_user


def register_user(username, password, role="staff"):
    """
    Register a new user account with hashed password.
    Returns (success: bool, message: str).
    """
    if not username or len(username.strip()) < 3:
        return False, "Username must be at least 3 characters."
    if not password or len(password) < 6:
        return False, "Password must be at least 6 characters."

    existing = get_user_by_username(username.strip())
    if existing:
        return False, f"Username '{username.strip()}' already exists."

    pwd_hash = hash_password(password)
    from models.user_model import create_user
    user_id = create_user(username.strip(), pwd_hash, role)
    return True, f"Account '{username.strip()}' created successfully!"
