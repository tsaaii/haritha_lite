# utils/simple_oauth.py - COMPLETELY NEW WORKING FILE
"""
Simple OAuth Manager - Works with or without Google OAuth libraries
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

class SimpleOAuthManager:
    """Simple OAuth manager that works with basic requests library"""
    
    def __init__(self):
        self.sessions = {}
        self.is_configured = False
        self.oauth_config = {}
        
        # Try to load configuration
        self._load_config()
        
    def _load_config(self):
        """Load OAuth configuration if available"""
        try:
            if os.path.exists("client_secrets.json"):
                with open("client_secrets.json", 'r') as f:
                    config = json.load(f)
                
                # Handle both web and installed app types
                if 'web' in config:
                    oauth_section = config['web']
                elif 'installed' in config:
                    oauth_section = config['installed']
                else:
                    logger.warning("Invalid client_secrets.json format")
                    return
                
                self.oauth_config = {
                    "client_id": oauth_section.get("client_id", ""),
                    "client_secret": oauth_section.get("client_secret", ""),
                    "auth_uri": oauth_section.get("auth_uri", "https://accounts.google.com/o/oauth2/auth"),
                    "token_uri": oauth_section.get("token_uri", "https://oauth2.googleapis.com/token"),
                    "redirect_uris": oauth_section.get("redirect_uris", [])
                }
                
                # Check if properly configured
                if self.oauth_config["client_id"] and self.oauth_config["client_secret"]:
                    self.is_configured = True
                    logger.info("✅ OAuth configuration loaded successfully")
                else:
                    logger.warning("⚠️ OAuth configuration incomplete")
            else:
                logger.info("📝 No client_secrets.json found - using demo mode")
                
        except Exception as e:
            logger.error(f"❌ Error loading OAuth config: {e}")
    
    def is_available(self):
        """Check if OAuth is properly configured"""
        return self.is_configured
    
    def get_authorization_url(self, redirect_uri="http://localhost:8050/oauth/callback"):
        """Generate OAuth authorization URL"""
        if not self.is_configured:
            raise Exception("OAuth not configured - missing or invalid client_secrets.json")
        
        state = secrets.token_urlsafe(32)
        
        params = {
            'client_id': self.oauth_config['client_id'],
            'redirect_uri': redirect_uri,
            'scope': 'openid email profile',
            'response_type': 'code',
            'state': state,
            'access_type': 'offline',
            'prompt': 'consent'
        }
        
        auth_url = f"{self.oauth_config['auth_uri']}?{urllib.parse.urlencode(params)}"
        logger.info(f"🔗 Generated OAuth URL: {auth_url[:100]}...")
        
        return auth_url, state
    
    def exchange_code_for_tokens(self, code, redirect_uri="http://localhost:8050/oauth/callback"):
        """Exchange authorization code for access token"""
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
            
            logger.info("🔄 Exchanging authorization code for tokens...")
            
            response = requests.post(
                self.oauth_config['token_uri'],
                data=token_data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=10
            )
            
            if response.status_code == 200:
                tokens = response.json()
                logger.info("✅ Token exchange successful")
                return tokens
            else:
                error_msg = f"Token exchange failed: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return {"error": error_msg}
                
        except Exception as e:
            error_msg = f"Token exchange error: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
    
    def get_user_info(self, access_token):
        """Get user information from Google"""
        try:
            logger.info("👤 Fetching user information...")
            
            response = requests.get(
                'https://www.googleapis.com/oauth2/v2/userinfo',
                headers={'Authorization': f'Bearer {access_token}'},
                timeout=10
            )
            
            if response.status_code == 200:
                user_info = response.json()
                logger.info(f"✅ User info retrieved for: {user_info.get('email', 'unknown')}")
                return user_info
            else:
                error_msg = f"Failed to get user info: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return {"error": error_msg}
                
        except Exception as e:
            error_msg = f"User info error: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
    
    def authenticate_user(self, user_info):
        """Authenticate user and create session"""
        email = user_info.get('email', '').lower()
        name = user_info.get('name', '')
        picture = user_info.get('picture', '/assets/img/default-avatar.png')
        
        logger.info(f"🔐 Authenticating user: {email}")
        
        # Check if user is authorized (import safely)
        try:
            from config.auth import is_user_authorized, get_user_role, get_permissions
        except ImportError:
            logger.warning("⚠️ Auth config not available - allowing all users for demo")
            # Fallback authorization for demo
            def is_user_authorized(email): return True
            def get_user_role(email): return "administrator"
            def get_permissions(role): return ["view_dashboard", "edit_data", "export_reports", "view_analytics"]
        
        if not is_user_authorized(email):
            logger.warning(f"❌ Unauthorized user: {email}")
            return False, f"User {email} is not authorized for this system", {}
        
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
            'expires_at': (datetime.now() + timedelta(hours=8)).isoformat(),
            'last_activity': datetime.now().isoformat(),
            'auth_method': 'google_oauth'
        }
        
        # Store session
        self.sessions[session_id] = session_data
        
        logger.info(f"✅ User authenticated: {name} ({role})")
        return True, f"Welcome, {name}!", session_data
    
    def create_demo_session(self, email="demo@swacchaap.gov.in", name="Demo Google User"):
        """Create a demo session for testing"""
        demo_user_info = {
            'email': email,
            'name': name,
            'picture': '/assets/img/default-avatar.png',
            'verified_email': True
        }
        
        return self.authenticate_user(demo_user_info)
    
    def validate_session(self, session_id):
        """Validate session"""
        if not session_id or session_id not in self.sessions:
            return False, {}
        
        session = self.sessions[session_id]
        
        # Check expiration
        expires_at = datetime.fromisoformat(session['expires_at'])
        if datetime.now() > expires_at:
            logger.info(f"🕒 Session expired: {session_id[:16]}...")
            del self.sessions[session_id]
            return False, {}
        
        # Update activity
        session['last_activity'] = datetime.now().isoformat()
        return True, session
    
    def logout(self, session_id):
        """Logout user"""
        if session_id in self.sessions:
            user_email = self.sessions[session_id].get('email', 'unknown')
            del self.sessions[session_id]
            logger.info(f"👋 User logged out: {user_email}")
            return True
        return False
    
    def get_debug_info(self):
        """Get comprehensive debug information"""
        # Check dependencies
        deps = {}
        try:
            import google.auth
            deps['google-auth'] = '✅ Available'
        except ImportError:
            deps['google-auth'] = '❌ Missing'
        
        try:
            import google_auth_oauthlib
            deps['google-auth-oauthlib'] = '✅ Available'
        except ImportError:
            deps['google-auth-oauthlib'] = '❌ Missing'
        
        try:
            import requests
            deps['requests'] = '✅ Available'
        except ImportError:
            deps['requests'] = '❌ Missing'
        
        return {
            'oauth_configured': self.is_configured,
            'is_available': self.is_available(),
            'client_secrets_exists': os.path.exists("client_secrets.json"),
            'active_sessions': len(self.sessions),
            'dependencies': deps,
            'config_keys': list(self.oauth_config.keys()) if self.oauth_config else [],
            'has_client_id': bool(self.oauth_config.get('client_id')),
            'has_client_secret': bool(self.oauth_config.get('client_secret')),
            'redirect_uri': "http://localhost:8050/oauth/callback"
        }

# Global instance
_oauth_manager = SimpleOAuthManager()

def get_oauth_manager():
    """Get the global OAuth manager"""
    return _oauth_manager