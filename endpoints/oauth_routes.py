from flask import Blueprint, request, jsonify, session, redirect, url_for, current_app
import requests
import secrets
import logging
from urllib.parse import urlencode, parse_qs
import base64
import hashlib

# Create blueprint for OAuth routes
oauth_bp = Blueprint('oauth', __name__)

def generate_state():
    """Generate a random state parameter for OAuth security"""
    return secrets.token_urlsafe(32)

def generate_pkce_challenge():
    """Generate PKCE code verifier and challenge for OAuth2 security"""
    code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode('utf-8')).digest()
    ).decode('utf-8').rstrip('=')
    return code_verifier, code_challenge

@oauth_bp.route('/oauth/login')
def oauth_login():
    """Initiate OAuth login with Google"""
    try:
        # Check if Google OAuth is available
        if not getattr(oauth_bp, 'google_auth_available', False):
            return jsonify({'error': 'Google OAuth not available'}), 500
        
        google_auth_manager = getattr(oauth_bp, 'google_auth_manager', None)
        if not google_auth_manager:
            return jsonify({'error': 'Google OAuth not configured'}), 500
        
        # Generate OAuth URL using the auth manager
        try:
            auth_url, state = google_auth_manager.get_authorization_url()
            session['oauth_state'] = state
            
            if hasattr(oauth_bp, 'logger'):
                oauth_bp.logger.info(f"Redirecting to Google OAuth: {auth_url[:50]}...")
            
            return redirect(auth_url)
            
        except Exception as e:
            if hasattr(oauth_bp, 'logger'):
                oauth_bp.logger.error(f"Error generating OAuth URL: {e}")
            return jsonify({'error': 'Failed to generate OAuth URL'}), 500
        
    except Exception as e:
        logging.error(f"Error initiating OAuth login: {e}")
        return jsonify({'error': 'Failed to initiate OAuth login'}), 500

@oauth_bp.route('/oauth/callback')
def oauth_callback():
    """Handle OAuth callback from Google"""
    try:
        # Check if Google OAuth is available
        if not getattr(oauth_bp, 'google_auth_available', False):
            return jsonify({'error': 'Google OAuth not available'}), 500
        
        google_auth_manager = getattr(oauth_bp, 'google_auth_manager', None)
        if not google_auth_manager:
            return jsonify({'error': 'Google OAuth not configured'}), 500
        
        # Get authorization code
        code = request.args.get('code')
        state = request.args.get('state')
        error = request.args.get('error')
        
        if error:
            if hasattr(oauth_bp, 'logger'):
                oauth_bp.logger.error(f"OAuth error: {error}")
            return jsonify({'error': f'OAuth authorization failed: {error}'}), 400
        
        if not code:
            return jsonify({'error': 'No authorization code received'}), 400
        
        # Verify state parameter
        if state != session.get('oauth_state'):
            return jsonify({'error': 'Invalid state parameter'}), 400
        
        # Exchange code for tokens using the auth manager
        try:
            token_data = google_auth_manager.exchange_code_for_tokens(code)
            
            if 'error' in token_data:
                if hasattr(oauth_bp, 'logger'):
                    oauth_bp.logger.error(f"Token exchange error: {token_data['error']}")
                return jsonify({'error': 'Failed to exchange code for token'}), 500
            
            # Get user info using the auth manager
            user_info = google_auth_manager.get_user_info(token_data.get('access_token'))
            
            if 'error' in user_info:
                if hasattr(oauth_bp, 'logger'):
                    oauth_bp.logger.error(f"User info error: {user_info['error']}")
                return jsonify({'error': 'Failed to get user information'}), 500
            
            # Create session using your existing session management
            session_data = {
                'session_id': f"oauth_session_{user_info.get('id', 'unknown')}",
                'user_id': user_info.get('id'),
                'email': user_info.get('email'),
                'name': user_info.get('name'),
                'picture': user_info.get('picture'),
                'role': 'user',  # Default role, adjust based on your authorization logic
                'auth_method': 'google_oauth'
            }
            
            # Store session data
            session['swaccha_session_id'] = session_data['session_id']
            session['user_data'] = session_data
            
            # Clean up OAuth session data
            session.pop('oauth_state', None)
            
            if hasattr(oauth_bp, 'logger'):
                oauth_bp.logger.info(f"OAuth login successful for {user_info.get('email')}")
            
            # Redirect to dashboard instead of root
            return redirect('/dashboard')
            
        except Exception as e:
            if hasattr(oauth_bp, 'logger'):
                oauth_bp.logger.error(f"OAuth callback processing error: {e}")
            return jsonify({'error': 'OAuth callback processing failed'}), 500
        
    except Exception as e:
        logging.error(f"Error in OAuth callback: {e}")
        return jsonify({'error': 'OAuth callback failed'}), 500

def exchange_code_for_token(provider, code):
    """Exchange authorization code for access token"""
    try:
        token_configs = {
            'google': {
                'token_url': 'https://oauth2.googleapis.com/token',
                'client_id': current_app.config.get('GOOGLE_CLIENT_ID'),
                'client_secret': current_app.config.get('GOOGLE_CLIENT_SECRET')
            },
            'github': {
                'token_url': 'https://github.com/login/oauth/access_token',
                'client_id': current_app.config.get('GITHUB_CLIENT_ID'),
                'client_secret': current_app.config.get('GITHUB_CLIENT_SECRET')
            },
            'microsoft': {
                'token_url': 'https://login.microsoftonline.com/common/oauth2/v2.0/token',
                'client_id': current_app.config.get('MICROSOFT_CLIENT_ID'),
                'client_secret': current_app.config.get('MICROSOFT_CLIENT_SECRET')
            }
        }
        
        config = token_configs.get(provider)
        if not config:
            return None
        
        token_data = {
            'client_id': config['client_id'],
            'client_secret': config['client_secret'],
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': url_for('oauth.oauth_callback', provider=provider, _external=True)
        }
        
        # Add PKCE verifier if available
        if 'oauth_code_verifier' in session:
            token_data['code_verifier'] = session['oauth_code_verifier']
        
        headers = {'Accept': 'application/json'}
        
        response = requests.post(config['token_url'], data=token_data, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            logging.error(f"Token exchange failed: {response.text}")
            return None
            
    except Exception as e:
        logging.error(f"Error exchanging code for token: {e}")
        return None

def get_user_info(provider, access_token):
    """Get user information from OAuth provider"""
    try:
        user_info_configs = {
            'google': {
                'user_info_url': 'https://www.googleapis.com/oauth2/v2/userinfo'
            },
            'github': {
                'user_info_url': 'https://api.github.com/user'
            },
            'microsoft': {
                'user_info_url': 'https://graph.microsoft.com/v1.0/me'
            }
        }
        
        config = user_info_configs.get(provider)
        if not config:
            return None
        
        headers = {'Authorization': f'Bearer {access_token}'}
        
        response = requests.get(config['user_info_url'], headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            logging.error(f"Failed to get user info: {response.text}")
            return None
            
    except Exception as e:
        logging.error(f"Error getting user info: {e}")
        return None

@oauth_bp.route('/oauth/logout')
def oauth_logout():
    """Logout user and clear session"""
    try:
        # Get session ID before clearing
        session_id = session.get('swaccha_session_id')
        
        # Use auth manager logout if available
        google_auth_manager = getattr(oauth_bp, 'google_auth_manager', None)
        if google_auth_manager and session_id:
            try:
                google_auth_manager.logout(session_id)
            except Exception as e:
                if hasattr(oauth_bp, 'logger'):
                    oauth_bp.logger.warning(f"Auth manager logout error: {e}")
        
        # Clear all session data
        session.clear()
        
        if hasattr(oauth_bp, 'logger'):
            oauth_bp.logger.info("User logged out successfully")
        
        # Redirect to home page with logout parameter
        return redirect('/?logout=true')
        
    except Exception as e:
        logging.error(f"Error during logout: {e}")
        return jsonify({'error': 'Logout failed'}), 500

@oauth_bp.route('/api/oauth/user')
def get_current_user():
    """Get current user information"""
    try:
        if 'swaccha_session_id' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        
        user_data = session.get('user_data', {})
        
        return jsonify({
            'authenticated': True,
            'user': user_data
        })
        
    except Exception as e:
        logging.error(f"Error getting current user: {e}")
        return jsonify({'error': 'Failed to get user info'}), 500

@oauth_bp.route('/api/oauth/status')
def oauth_status():
    """Get OAuth service status"""
    try:
        google_auth_available = getattr(oauth_bp, 'google_auth_available', False)
        google_auth_manager = getattr(oauth_bp, 'google_auth_manager', None)
        
        status = {
            'google_oauth_available': google_auth_available,
            'google_oauth_configured': google_auth_manager is not None,
            'authenticated': 'swaccha_session_id' in session
        }
        
        if google_auth_manager and hasattr(google_auth_manager, 'is_available'):
            status['google_oauth_ready'] = google_auth_manager.is_available()
        
        return jsonify(status)
        
    except Exception as e:
        logging.error(f"Error getting OAuth status: {e}")
        return jsonify({'error': 'Failed to get OAuth status'}), 500

def register_oauth_routes(app, google_auth_manager=None, google_auth_available=False, logger=None):
    """Register OAuth routes with the Flask app"""
    
    # Store the auth manager and logger in the blueprint for use in routes
    oauth_bp.google_auth_manager = google_auth_manager
    oauth_bp.google_auth_available = google_auth_available
    oauth_bp.logger = logger or logging.getLogger(__name__)
    
    app.register_blueprint(oauth_bp)