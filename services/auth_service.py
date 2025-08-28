# services/auth_service.py
"""
Authentication Service
Handles Google OAuth and session management
"""

import json
import secrets
import time
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
import requests
from urllib.parse import urlencode, parse_qs
import jwt

from config.auth import (
    load_google_oauth_config, 
    is_user_authorized, 
    get_user_role,
    get_permissions,
    validate_email_domain,
    SESSION_CONFIG,
    SECURITY_CONFIG
)

class AuthenticationService:
    """Handles all authentication operations"""
    
    def __init__(self):
        self.oauth_config = load_google_oauth_config()
        self.sessions = {}  # In production, use Redis or database
        self.login_attempts = {}  # Track failed login attempts
        
    def generate_oauth_url(self, state: str = None) -> Tuple[str, str]:
        """
        Generate Google OAuth authorization URL
        
        Args:
            state (str): Optional state parameter for CSRF protection
            
        Returns:
            Tuple[str, str]: (authorization_url, state)
        """
        if not self.oauth_config:
            raise ValueError("Google OAuth not configured. Check client_secrets.json")
        
        if state is None:
            state = secrets.token_urlsafe(32)
        
        params = {
            'client_id': self.oauth_config['client_id'],
            'redirect_uri': 'https://applied-pursuit-332603.el.r.appspot.com/oauth/callback',  # Adjust for production
            'scope': 'openid email profile',
            'response_type': 'code',
            'state': state,
            'access_type': 'offline',
            'prompt': 'consent'
        }
        
        auth_url = f"{self.oauth_config['auth_uri']}?{urlencode(params)}"
        return auth_url, state
    
    def exchange_code_for_token(self, code: str, state: str) -> Dict:
        """
        Exchange authorization code for access token
        
        Args:
            code (str): Authorization code from OAuth callback
            state (str): State parameter for verification
            
        Returns:
            dict: Token response or error
        """
        if not self.oauth_config:
            return {"error": "OAuth not configured"}
        
        try:
            token_data = {
                'client_id': self.oauth_config['client_id'],
                'client_secret': self.oauth_config['client_secret'],
                'code': code,
                'grant_type': 'authorization_code',
                'redirect_uri': 'https://applied-pursuit-332603.el.r.appspot.com/oauth/callback'
            }
            
            response = requests.post(
                self.oauth_config['token_uri'],
                data=token_data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Token exchange failed: {response.status_code}"}
                
        except Exception as e:
            return {"error": f"Token exchange error: {str(e)}"}
    
    def get_user_info(self, access_token: str) -> Dict:
        """
        Get user information from Google using access token
        
        Args:
            access_token (str): Google access token
            
        Returns:
            dict: User information or error
        """
        try:
            response = requests.get(
                'https://www.googleapis.com/oauth2/v2/userinfo',
                headers={'Authorization': f'Bearer {access_token}'}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Failed to get user info: {response.status_code}"}
                
        except Exception as e:
            return {"error": f"User info error: {str(e)}"}
    
    def authenticate_user(self, user_info: Dict) -> Tuple[bool, str, Dict]:
        """
        Authenticate user and create session
        
        Args:
            user_info (dict): User information from OAuth
            
        Returns:
            tuple: (success, message, session_data)
        """
        email = user_info.get('email', '').lower()
        name = user_info.get('name', '')
        picture = user_info.get('picture', '')
        
        # Check if email domain is allowed
        if not validate_email_domain(email):
            return False, "Email domain not authorized", {}
        
        # Check if user is in allowed list
        if not is_user_authorized(email):
            self._record_failed_attempt(email)
            return False, "User not authorized for this system", {}
        
        # Check for account lockout
        if self._is_account_locked(email):
            return False, "Account temporarily locked due to multiple failed attempts", {}
        
        # Get user role and permissions
        role = get_user_role(email)
        permissions = get_permissions(role)
        
        # Create session
        session_id = secrets.token_urlsafe(32)
        session_data = {
            'session_id': session_id,
            'user_id': email,
            'email': email,
            'name': name,
            'picture': picture,
            'role': role,
            'permissions': permissions,
            'created_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(seconds=SESSION_CONFIG['session_timeout'])).isoformat(),
            'last_activity': datetime.now().isoformat()
        }
        
        # Store session
        self.sessions[session_id] = session_data
        
        # Clear failed attempts
        if email in self.login_attempts:
            del self.login_attempts[email]
        
        return True, f"Welcome, {name}!", session_data
    
    def validate_session(self, session_id: str) -> Tuple[bool, Dict]:
        """
        Validate user session
        
        Args:
            session_id (str): Session identifier
            
        Returns:
            tuple: (valid, session_data)
        """
        if not session_id or session_id not in self.sessions:
            return False, {}
        
        session = self.sessions[session_id]
        
        # Check if session has expired
        expires_at = datetime.fromisoformat(session['expires_at'])
        if datetime.now() > expires_at:
            self.logout_user(session_id)
            return False, {}
        
        # Update last activity
        session['last_activity'] = datetime.now().isoformat()
        self.sessions[session_id] = session
        
        return True, session
    
    def refresh_session(self, session_id: str) -> bool:
        """
        Refresh session expiration time
        
        Args:
            session_id (str): Session identifier
            
        Returns:
            bool: Success status
        """
        if session_id in self.sessions:
            self.sessions[session_id]['expires_at'] = (
                datetime.now() + timedelta(seconds=SESSION_CONFIG['session_timeout'])
            ).isoformat()
            return True
        return False
    
    def logout_user(self, session_id: str) -> bool:
        """
        Logout user and destroy session
        
        Args:
            session_id (str): Session identifier
            
        Returns:
            bool: Success status
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False
    
    def debug_oauth_config(self) -> Dict:
        """
        Debug OAuth configuration for troubleshooting
        
        Returns:
            dict: Debug information about OAuth config
        """
        debug_info = {
            'config_loaded': bool(self.oauth_config),
            'has_client_id': bool(self.oauth_config.get('client_id') if self.oauth_config else False),
            'has_client_secret': bool(self.oauth_config.get('client_secret') if self.oauth_config else False),
            'redirect_uris': self.oauth_config.get('redirect_uris', []) if self.oauth_config else [],
            'auth_uri': self.oauth_config.get('auth_uri', 'Not found') if self.oauth_config else 'Not found',
            'token_uri': self.oauth_config.get('token_uri', 'Not found') if self.oauth_config else 'Not found'
        }
        
        if self.oauth_config:
            debug_info['expected_redirect_uri'] = 'https://applied-pursuit-332603.el.r.appspot.com/oauth/callback'
            debug_info['redirect_uri_configured'] = 'https://applied-pursuit-332603.el.r.appspot.com/oauth/callback' in self.oauth_config.get('redirect_uris', [])
        
        return debug_info
    
    def _record_failed_attempt(self, email: str):
        """Record failed login attempt"""
        current_time = time.time()
        
        if email not in self.login_attempts:
            self.login_attempts[email] = []
        
        # Clean old attempts (older than lockout duration)
        self.login_attempts[email] = [
            attempt_time for attempt_time in self.login_attempts[email]
            if current_time - attempt_time < SECURITY_CONFIG['lockout_duration']
        ]
        
        # Add current attempt
        self.login_attempts[email].append(current_time)
    
    def _is_account_locked(self, email: str) -> bool:
        """Check if account is locked due to failed attempts"""
        if email not in self.login_attempts:
            return False
        
        current_time = time.time()
        recent_attempts = [
            attempt_time for attempt_time in self.login_attempts[email]
            if current_time - attempt_time < SECURITY_CONFIG['lockout_duration']
        ]
        
        return len(recent_attempts) >= SECURITY_CONFIG['max_login_attempts']
    
    def get_user_sessions(self, email: str) -> list:
        """Get all active sessions for a user"""
        user_sessions = []
        for session_id, session_data in self.sessions.items():
            if session_data['email'] == email:
                user_sessions.append({
                    'session_id': session_id,
                    'created_at': session_data['created_at'],
                    'last_activity': session_data['last_activity'],
                    'expires_at': session_data['expires_at']
                })
        return user_sessions
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        current_time = datetime.now()
        expired_sessions = []
        
        for session_id, session_data in self.sessions.items():
            expires_at = datetime.fromisoformat(session_data['expires_at'])
            if current_time > expires_at:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.sessions[session_id]
        
        return len(expired_sessions)

class SessionManager:
    """Manages user sessions for Dash app"""
    
    def __init__(self):
        self.auth_service = AuthenticationService()
    
    def create_session_cookie(self, session_id: str) -> Dict:
        """Create session cookie configuration"""
        return {
            'name': 'swaccha_session',
            'value': session_id,
            'max_age': SESSION_CONFIG['session_timeout'],
            'secure': SESSION_CONFIG['secure_cookies'],
            'httponly': True,
            'samesite': 'Lax'
        }
    
    def extract_session_from_request(self, request_cookies: str) -> Optional[str]:
        """Extract session ID from request cookies"""
        if not request_cookies:
            return None
        
        # Parse cookies (simplified - in production use proper cookie parsing)
        cookies = {}
        for cookie in request_cookies.split(';'):
            if '=' in cookie:
                name, value = cookie.strip().split('=', 1)
                cookies[name] = value
        
        return cookies.get('swaccha_session')
    
    def get_current_user(self, session_id: str) -> Optional[Dict]:
        """Get current user from session"""
        if not session_id:
            return None
        
        is_valid, session_data = self.auth_service.validate_session(session_id)
        if is_valid:
            return session_data
        return None

# Global authentication service instance
auth_service = AuthenticationService()
session_manager = SessionManager()

# Helper functions for use in callbacks
def get_auth_service():
    """Get global authentication service instance"""
    return auth_service

def get_session_manager():
    """Get global session manager instance"""
    return session_manager

def require_auth(session_id: str) -> Tuple[bool, Dict]:
    """
    Decorator-like function to require authentication
    
    Args:
        session_id (str): Session identifier
        
    Returns:
        tuple: (authenticated, user_data)
    """
    return auth_service.validate_session(session_id)

def require_permission(session_id: str, permission: str) -> bool:
    """
    Check if user has specific permission
    
    Args:
        session_id (str): Session identifier
        permission (str): Required permission
        
    Returns:
        bool: Has permission
    """
    is_valid, session_data = auth_service.validate_session(session_id)
    if not is_valid:
        return False
    
    user_permissions = session_data.get('permissions', [])
    return permission in user_permissions

def get_login_redirect_url() -> str:
    """Get URL for login redirect"""
    try:
        auth_url, state = auth_service.generate_oauth_url()
        return auth_url
    except Exception as e:
        print(f"Error generating OAuth URL: {e}")
        return "/login"  # Fallback to manual login

# Export all necessary components
__all__ = [
    'AuthenticationService',
    'SessionManager', 
    'auth_service',
    'session_manager',
    'get_auth_service',
    'get_session_manager',
    'require_auth',
    'require_permission',
    'get_login_redirect_url'
]