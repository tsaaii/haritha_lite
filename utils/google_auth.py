# utils/google_auth.py - SIMPLIFIED WORKING VERSION
"""
Google OAuth Authentication - SIMPLIFIED
Working version with proper imports and fallbacks
"""

import json
import os
import secrets
import requests
import urllib.parse
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple
import logging

logger = logging.getLogger(__name__)

# Check for Google Auth libraries availability
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import Flow
    GOOGLE_AUTH_AVAILABLE = True
    logger.info("✅ Google Auth libraries available")
except ImportError as e:
    GOOGLE_AUTH_AVAILABLE = False
    logger.warning(f"⚠️ Google Auth libraries not available: {e}")

class GoogleAuthManager:
    """Simple Google OAuth manager"""
    
    def __init__(self):
        self.scopes = ['openid', 'email', 'profile']
        self.sessions = {}
        self.oauth_config = self._load_oauth_config()
        self.is_configured = bool(self.oauth_config and GOOGLE_AUTH_AVAILABLE)
        
        if self.is_configured:
            logger.info("✅ Google OAuth configured and ready")
        else:
            logger.warning("⚠️ Google OAuth not available - using demo mode")
    
    def _load_oauth_config(self):
        """Load OAuth configuration"""
        try:
            if not os.path.exists("client_secrets.json"):
                return {}
            
            with open("client_secrets.json", 'r') as f:
                config = json.load(f)
            
            # Handle both web and installed app types
            config_key = 'web' if 'web' in config else 'installed'
            if config_key not in config:
                return {}
            
            oauth_section = config[config_key]
            return {
                "client_id": oauth_section["client_id"],
                "client_secret": oauth_section["client_secret"],
                "auth_uri": oauth_section.get("auth_uri", "https://accounts.google.com/o/oauth2/auth"),
                "token_uri": oauth_section.get("token_uri", "https://oauth2.googleapis.com/token"),
                "redirect_uris": oauth_section.get("redirect_uris", [])
            }
        except Exception as e:
            logger.error(f"Error loading OAuth config: {e}")
            return {}
    
    def is_available(self):
        """Check if OAuth is available"""
        return self.is_configured
    
    def get_authorization_url(self, redirect_uri="http://localhost:8050//oauth/callback"):
        """Get OAuth authorization URL"""
        if not self.is_configured:
            raise Exception("OAuth not configured")
        
        state = secrets.token_urlsafe(32)
        params = {
            'client_id': self.oauth_config['client_id'],
            'redirect_uri': redirect_uri,
            'scope': ' '.join(self.scopes),
            'response_type': 'code',
            'state': state,
            'access_type': 'offline',
            'prompt': 'consent'
        }
        
        auth_url = f"{self.oauth_config['auth_uri']}?{urllib.parse.urlencode(params)}"
        return auth_url, state
    
    def exchange_code_for_tokens(self, code, redirect_uri="http://localhost:8050//oauth/callback"):
        """Exchange code for tokens"""
        if not self.is_configured:
            return {"error": "OAuth not configured"}
        
        try:
            token_data = {
                'client_id': self.oauth_config['client_id'],
                'client_secret': self.oauth_config['client_secret'],
                'code': code,
                'grant_type': 'authorization_code',
                'redirect_uri': redirect_uri
            }
            
            response = requests.post(
                self.oauth_config['token_uri'],
                data=token_data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Token exchange failed: {response.status_code}"}
        except Exception as e:
            return {"error": f"Token exchange error: {str(e)}"}
    
    def get_user_info(self, access_token):
        """Get user info from access token"""
        try:
            response = requests.get(
                'https://www.googleapis.com/oauth2/v2/userinfo',
                headers={'Authorization': f'Bearer {access_token}'},
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Failed to get user info: {response.status_code}"}
        except Exception as e:
            return {"error": f"User info error: {str(e)}"}
    
    def authenticate_user(self, user_info):
        """Authenticate user and create session"""
        email = user_info.get('email', '').lower()
        name = user_info.get('name', '')
        
        # Import here to avoid circular imports
        try:
            from config.auth import is_user_authorized, get_user_role, get_permissions
        except ImportError:
            # Fallback for development
            def is_user_authorized(email): return True
            def get_user_role(email): return "administrator"
            def get_permissions(role): return ["view_dashboard"]
        
        if not is_user_authorized(email):
            return False, f"User {email} is not authorized", {}
        
        role = get_user_role(email)
        permissions = get_permissions(role)
        
        session_id = secrets.token_urlsafe(32)
        session_data = {
            'session_id': session_id,
            'user_id': email,
            'email': email,
            'name': name,
            'picture': user_info.get('picture', '/assets/img/default-avatar.png'),
            'role': role,
            'permissions': permissions,
            'created_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(hours=8)).isoformat(),
            'last_activity': datetime.now().isoformat(),
            'auth_method': 'google_oauth'
        }
        
        self.sessions[session_id] = session_data
        logger.info(f"✅ User authenticated: {name} ({role})")
        return True, f"Welcome, {name}!", session_data
    
    def validate_session(self, session_id):
        """Validate session"""
        if not session_id or session_id not in self.sessions:
            return False, {}
        
        session = self.sessions[session_id]
        expires_at = datetime.fromisoformat(session['expires_at'])
        if datetime.now() > expires_at:
            del self.sessions[session_id]
            return False, {}
        
        session['last_activity'] = datetime.now().isoformat()
        return True, session
    
    def logout(self, session_id):
        """Logout user"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False
    
    def get_debug_info(self):
        """Get debug information"""
        return {
            'google_auth_available': GOOGLE_AUTH_AVAILABLE,
            'oauth_configured': bool(self.oauth_config),
            'is_available': self.is_available(),
            'client_secrets_exists': os.path.exists("client_secrets.json"),
            'active_sessions': len(self.sessions),
            'config_keys': list(self.oauth_config.keys()) if self.oauth_config else []
        }

class DemoGoogleAuth:
    """Demo authentication when OAuth is not available"""
    
    def __init__(self):
        self.sessions = {}
        logger.info("📱 Using Demo OAuth mode")
    
    def is_available(self):
        return False
    
    def authenticate_user(self, user_info):
        """Demo authentication"""
        email = user_info.get('email', 'demo@swacchaap.gov.in')
        name = user_info.get('name', 'Demo Google User')
        
        session_id = f"demo_session_{secrets.token_urlsafe(16)}"
        session_data = {
            'session_id': session_id,
            'user_id': email,
            'email': email,
            'name': name,
            'picture': '/assets/img/default-avatar.png',
            'role': 'administrator',
            'permissions': ['view_dashboard', 'edit_data', 'export_reports', 'view_analytics'],
            'created_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(hours=8)).isoformat(),
            'last_activity': datetime.now().isoformat(),
            'auth_method': 'demo_google'
        }
        
        self.sessions[session_id] = session_data
        logger.info(f"✅ Demo user authenticated: {name}")
        return True, f"Welcome, {name}! (Demo Mode)", session_data
    
    def validate_session(self, session_id):
        return (session_id in self.sessions), self.sessions.get(session_id, {})
    
    def logout(self, session_id):
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False
    
    def get_debug_info(self):
        return {
            'mode': 'demo',
            'google_auth_available': False,
            'oauth_configured': False,
            'is_available': False,
            'active_sessions': len(self.sessions)
        }

# Initialize global manager
try:
    if GOOGLE_AUTH_AVAILABLE and os.path.exists("client_secrets.json"):
        _google_auth_manager = GoogleAuthManager()
        if _google_auth_manager.is_available():
            logger.info("✅ Using REAL Google OAuth")
        else:
            _google_auth_manager = DemoGoogleAuth()
    else:
        _google_auth_manager = DemoGoogleAuth()
except Exception as e:
    logger.error(f"❌ Error initializing auth manager: {e}")
    _google_auth_manager = DemoGoogleAuth()

def get_google_auth_manager():
    """Get the global auth manager"""
    return _google_auth_manager