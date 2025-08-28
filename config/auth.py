# config/auth.py - COMPLETE FIXED VERSION
"""
Authentication Configuration - COMPLETE
Manages user access control and OAuth settings
"""

import json
import os
from typing import List, Dict, Optional

# Allowed users configuration - Easy to edit
ALLOWED_USERS = {
    # Email addresses that have access to the admin dashboard
    "administrators": [
        "saaitejaa@gmail.com",
        "director@swacchaandhra.gov.in",
        "admin@swacchaap.gov.in",
        "your.email@gmail.com"  # Add your email here
    ],
    
    # Viewers with read-only access
    "viewers": [
        "saiteja7050@gmail.com",
        "analyst@swacchaandhra.gov.in"
    ],
    
    # Super admins with full access
    "super_admins": [
        "saaitejaa@gmail.com"
    ]
}

# OAuth Configuration
OAUTH_CONFIG = {
    "google": {
        "client_secrets_file": "client_secrets.json",  # Your Google OAuth credentials file
        "scopes": ["openid", "email", "profile"],
        "redirect_uri": "https://applied-pursuit-332603.el.r.appspot.com/oauth/callback",  # Adjust for production
        "hosted_domain": None  # Set to your domain to restrict to specific domain users
    }
}

# Session configuration
SESSION_CONFIG = {
    "secret_key": "your-secret-key-change-this-in-production",  # Change this!
    "session_timeout": 3600,  # 1 hour in seconds
    "remember_me_duration": 86400 * 30,  # 30 days in seconds
    "secure_cookies": False  # Set to True in production with HTTPS
}

# Security settings
SECURITY_CONFIG = {
    "max_login_attempts": 5,
    "lockout_duration": 900,  # 15 minutes in seconds
    "require_domain_verification": False,
    "allowed_domains": ["swacchaandhra.gov.in", "gmail.com", "googlemail.com"]  # Add your allowed domains
}

def get_user_role(email: str) -> Optional[str]:
    """
    Get user role based on email address
    
    Args:
        email (str): User email address
        
    Returns:
        str: User role or None if not authorized
    """
    email = email.lower().strip()
    
    if email in ALLOWED_USERS["super_admins"]:
        return "super_admin"
    elif email in ALLOWED_USERS["administrators"]:
        return "administrator"
    elif email in ALLOWED_USERS["viewers"]:
        return "viewer"
    else:
        return None

def is_user_authorized(email: str) -> bool:
    """
    Check if user is authorized to access the system
    
    Args:
        email (str): User email address
        
    Returns:
        bool: True if authorized, False otherwise
    """
    return get_user_role(email) is not None

def load_google_oauth_config() -> Dict:
    """
    Load Google OAuth configuration from client_secrets.json
    
    Returns:
        dict: OAuth configuration
    """
    try:
        with open(OAUTH_CONFIG["google"]["client_secrets_file"], 'r') as f:
            client_config = json.load(f)
        
        # Handle both 'web' and 'installed' app types
        config_key = 'web' if 'web' in client_config else 'installed'
        
        if config_key not in client_config:
            print("Error: Invalid client_secrets.json format.")
            return {}
        
        oauth_section = client_config[config_key]
        
        return {
            "client_id": oauth_section["client_id"],
            "client_secret": oauth_section["client_secret"],
            "auth_uri": oauth_section.get("auth_uri", "https://accounts.google.com/o/oauth2/auth"),
            "token_uri": oauth_section.get("token_uri", "https://oauth2.googleapis.com/token"),
            "redirect_uris": oauth_section.get("redirect_uris", [])
        }
    except FileNotFoundError:
        print("Warning: client_secrets.json not found. Google OAuth will not work.")
        return {}
    except KeyError as e:
        print(f"Error: Invalid client_secrets.json format. Missing key: {e}")
        return {}
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in client_secrets.json: {e}")
        return {}

def get_permissions(role: str) -> List[str]:
    """
    Get permissions based on user role
    
    Args:
        role (str): User role
        
    Returns:
        list: List of permissions
    """
    permissions_map = {
        "super_admin": [
            "view_dashboard",
            "edit_data",
            "manage_users",
            "export_reports",
            "system_admin",
            "view_analytics",
            "manage_settings"
        ],
        "administrator": [
            "view_dashboard",
            "edit_data",
            "export_reports",
            "view_analytics"
        ],
        "viewer": [
            "view_dashboard",
            "view_analytics"
        ]
    }
    
    return permissions_map.get(role, [])

# MISSING FUNCTION - THIS WAS CAUSING THE IMPORT ERROR
def validate_email_domain(email: str) -> bool:
    """
    Validate if email domain is allowed
    
    Args:
        email (str): Email address to validate
        
    Returns:
        bool: True if domain is allowed, False otherwise
    """
    if not SECURITY_CONFIG["require_domain_verification"]:
        return True
    
    try:
        domain = email.split('@')[-1].lower()
        return domain in SECURITY_CONFIG["allowed_domains"]
    except (IndexError, AttributeError):
        return False

# Easy configuration updates
def add_user(email: str, role: str = "viewer") -> bool:
    """
    Add a new user to the allowed users list
    Note: This is for reference - you'll need to manually edit this file
    
    Args:
        email (str): User email address
        role (str): User role (viewer, administrator, super_admin)
        
    Returns:
        bool: Success status
    """
    role_key = f"{role}s" if role != "super_admin" else "super_admins"
    
    if role_key in ALLOWED_USERS:
        if email not in ALLOWED_USERS[role_key]:
            print(f"To add user {email} as {role}, edit config/auth.py and add to ALLOWED_USERS['{role_key}']")
            return True
    return False

def remove_user(email: str) -> bool:
    """
    Remove a user from all roles
    Note: This is for reference - you'll need to manually edit this file
    
    Args:
        email (str): User email address
        
    Returns:
        bool: Success status
    """
    removed = False
    for role_list in ALLOWED_USERS.values():
        if email in role_list:
            print(f"To remove user {email}, edit config/auth.py and remove from appropriate ALLOWED_USERS list")
            removed = True
    return removed

# Environment-based configuration
def get_environment_config():
    """Get configuration based on environment"""
    environment = os.getenv('FLASK_ENV', 'development')
    
    if environment == 'production':
        return {
            "redirect_uri": "https://yourdomain.com/oauth/callback",
            "secure_cookies": True,
            "session_timeout": 7200,  # 2 hours
            "require_domain_verification": True
        }
    else:
        return {
            "redirect_uri": "https://applied-pursuit-332603.el.r.appspot.com/oauth/callback",
            "secure_cookies": False,
            "session_timeout": 3600,  # 1 hour
            "require_domain_verification": False
        }

def get_user_display_name(email: str, role: str) -> str:
    """Get display name for user"""
    name = email.split('@')[0].replace('.', ' ').title()
    role_display = role.replace('_', ' ').title()
    return f"{name} ({role_display})"

# NEW FUNCTION - for compatibility with auth_service.py
def is_user_allowed(email: str) -> bool:
    """
    Alternative name for is_user_authorized for backward compatibility
    """
    return is_user_authorized(email)

def get_user_info(email: str) -> Dict:
    """
    Get user information including role and permissions
    
    Args:
        email (str): User email address
        
    Returns:
        dict: User information
    """
    role = get_user_role(email)
    if not role:
        return {}
    
    return {
        'email': email,
        'role': role,
        'permissions': get_permissions(role),
        'display_name': get_user_display_name(email, role),
        'is_authorized': True
    }

def get_settings() -> Dict:
    """
    Get current settings configuration
    
    Returns:
        dict: Settings configuration
    """
    return {
        'session_timeout_minutes': SESSION_CONFIG['session_timeout'] // 60,
        'max_login_attempts': SECURITY_CONFIG['max_login_attempts'],
        'lockout_duration_minutes': SECURITY_CONFIG['lockout_duration'] // 60,
        'require_domain_verification': SECURITY_CONFIG['require_domain_verification'],
        'allowed_domains': SECURITY_CONFIG['allowed_domains']
    }

# Export configuration
__all__ = [
    'ALLOWED_USERS',
    'OAUTH_CONFIG', 
    'SESSION_CONFIG',
    'SECURITY_CONFIG',
    'get_user_role',
    'is_user_authorized',
    'is_user_allowed',  # Added for compatibility
    'load_google_oauth_config',
    'get_permissions',
    'validate_email_domain',  # This was missing!
    'get_user_display_name',
    'get_user_info',  # Added for compatibility
    'get_settings',  # Added for compatibility
    'add_user',
    'remove_user',
    'get_environment_config'
]

def get_tab_permissions(role: str) -> List[str]:
    """
    Get tab access permissions based on user role
    
    Args:
        role (str): User role
        
    Returns:
        list: List of allowed tab IDs
    """
    tab_permissions_map = {
        "super_admin": [
            "dashboard",
            "analytics", 
            "charts",
            "reports",
            "reviews",
            "forecasting",
            "upload"
        ],
        "administrator": [
            "dashboard",
            "analytics",
            "charts", 
            "reports",
            "reviews",
            "forecasting",
            "upload"
        ],
        "viewer": [
            "dashboard",
            "analytics", 
            "charts",
            "reports"
            # Note: 'reviews' and 'forecasting' are excluded for viewers
        ]
    }
    
    return tab_permissions_map.get(role, ["dashboard"])


def can_user_access_tab(user_role: str, tab_id: str) -> bool:
    """
    Check if user can access a specific tab
    
    Args:
        user_role (str): User role
        tab_id (str): Tab identifier
        
    Returns:
        bool: True if user can access tab, False otherwise
    """
    allowed_tabs = get_tab_permissions(user_role)
    return tab_id in allowed_tabs