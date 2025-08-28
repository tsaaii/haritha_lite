"""
Authentication utilities for username/password login
"""

import json
import hashlib
import time
from datetime import datetime
from pathlib import Path
import os


class AuthenticationManager:
    def __init__(self, credentials_file="user_credentials.json"):
        """Initialize authentication manager"""
        self.credentials_file = credentials_file
        self.failed_attempts = {}  # Track failed login attempts
        
    def load_credentials(self):
        """Load user credentials from JSON file"""
        try:
            if os.path.exists(self.credentials_file):
                with open(self.credentials_file, 'r') as f:
                    return json.load(f)
            else:
                print(f"Warning: Credentials file {self.credentials_file} not found")
                return {"users": {}, "config": {}}
        except Exception as e:
            print(f"Error loading credentials: {e}")
            return {"users": {}, "config": {}}
    
    def save_credentials(self, data):
        """Save user credentials to JSON file"""
        try:
            with open(self.credentials_file, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving credentials: {e}")
            return False
    
    def hash_password(self, password):
        """Hash password using SHA256 (simple hashing for demo)"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def is_account_locked(self, username):
        """Check if account is locked due to failed attempts"""
        if username not in self.failed_attempts:
            return False
        
        attempts = self.failed_attempts[username]
        config = self.load_credentials().get("config", {})
        max_attempts = config.get("max_login_attempts", 3)
        lockout_duration = config.get("lockout_duration", 300)  # 5 minutes
        
        if attempts["count"] >= max_attempts:
            time_since_last_attempt = time.time() - attempts["last_attempt"]
            if time_since_last_attempt < lockout_duration:
                return True
            else:
                # Reset attempts after lockout period
                self.failed_attempts[username] = {"count": 0, "last_attempt": 0}
                return False
        
        return False
    
    def record_failed_attempt(self, username):
        """Record a failed login attempt"""
        if username not in self.failed_attempts:
            self.failed_attempts[username] = {"count": 0, "last_attempt": 0}
        
        self.failed_attempts[username]["count"] += 1
        self.failed_attempts[username]["last_attempt"] = time.time()
    
    def reset_failed_attempts(self, username):
        """Reset failed attempts for successful login"""
        if username in self.failed_attempts:
            del self.failed_attempts[username]
    
    def authenticate_user(self, username, password):
        """
        Authenticate user with username and password
        Returns: (success: bool, message: str, user_data: dict)
        """
        if not username or not password:
            return False, "Username and password are required", {}
        
        # Check if account is locked
        if self.is_account_locked(username):
            return False, "Account temporarily locked due to multiple failed attempts", {}
        
        # Load credentials
        credentials = self.load_credentials()
        users = credentials.get("users", {})
        
        # Check if user exists
        if username not in users:
            self.record_failed_attempt(username)
            return False, "Invalid username or password", {}
        
        user_data = users[username]
        stored_password = user_data.get("password", "")
        
        # For simplicity, using plain text comparison
        # In production, you should hash passwords
        if password == stored_password:
            # Successful login
            self.reset_failed_attempts(username)
            
            # Update last login time
            user_data["last_login"] = datetime.now().isoformat()
            credentials["users"][username] = user_data
            self.save_credentials(credentials)
            
            return True, "Login successful", {
                "username": username,
                "role": user_data.get("role", "user"),
                "permissions": user_data.get("permissions", []),
                "last_login": user_data.get("last_login")
            }
        else:
            # Failed login
            self.record_failed_attempt(username)
            attempts_left = credentials.get("config", {}).get("max_login_attempts", 3) - self.failed_attempts[username]["count"]
            
            if attempts_left > 0:
                return False, f"Invalid username or password. {attempts_left} attempts remaining", {}
            else:
                return False, "Account locked due to multiple failed attempts", {}
    
    def get_user_info(self, username):
        """Get user information"""
        credentials = self.load_credentials()
        users = credentials.get("users", {})
        
        if username in users:
            user_data = users[username].copy()
            # Don't return password
            user_data.pop("password", None)
            return user_data
        
        return None
    
    def add_user(self, username, password, role="user", permissions=None):
        """Add a new user"""
        if permissions is None:
            permissions = ["dashboard"]
        
        credentials = self.load_credentials()
        
        # Check if user already exists
        if username in credentials.get("users", {}):
            return False, "User already exists"
        
        # Add new user
        credentials["users"][username] = {
            "password": password,  # In production, hash this
            "role": role,
            "permissions": permissions,
            "created_date": datetime.now().isoformat(),
            "last_login": None
        }
        
        if self.save_credentials(credentials):
            return True, "User added successfully"
        else:
            return False, "Failed to save user"
    
    def change_password(self, username, old_password, new_password):
        """Change user password"""
        # First authenticate with old password
        success, message, user_data = self.authenticate_user(username, old_password)
        
        if not success:
            return False, "Current password is incorrect"
        
        # Update password
        credentials = self.load_credentials()
        credentials["users"][username]["password"] = new_password
        
        if self.save_credentials(credentials):
            return True, "Password changed successfully"
        else:
            return False, "Failed to save new password"


# Global authentication manager instance
auth_manager = AuthenticationManager()


def validate_credentials(username, password):
    """
    Convenience function to validate credentials
    Returns: (success: bool, message: str, user_data: dict)
    """
    return auth_manager.authenticate_user(username, password)


def get_quick_login_credentials(user_type):
    """Get credentials for quick login buttons"""
    quick_logins = {
        "admin": {"username": "admin", "password": "admin123"},
        "demo": {"username": "demo", "password": "demo123"},
        "viewer": {"username": "viewer", "password": "view123"}
    }
    
    return quick_logins.get(user_type, {"username": "", "password": ""})


# Session management functions (for use with Flask session)
def create_user_session(user_data):
    """Create session data for authenticated user"""
    return {
        "authenticated": True,
        "username": user_data.get("username"),
        "role": user_data.get("role"),
        "permissions": user_data.get("permissions", []),
        "login_time": datetime.now().isoformat(),
        "auth_method": "credentials"
    }


def is_user_authenticated(session_data):
    """Check if user session is valid"""
    if not session_data:
        return False
    
    return session_data.get("authenticated", False)


def has_permission(session_data, required_permission):
    """Check if user has required permission"""
    if not is_user_authenticated(session_data):
        return False
    
    user_permissions = session_data.get("permissions", [])
    return required_permission in user_permissions or "full_access" in user_permissions