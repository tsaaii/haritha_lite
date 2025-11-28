# endpoints/drap_routes_drap.py
"""
DRAP Endpoint Flask Routes
Blueprint for /DRAP URL endpoint with hardcoded authentication
"""

from flask import Blueprint, session, redirect, request, jsonify
import logging

logger = logging.getLogger(__name__)

# Create Flask Blueprint for DRAP
drap_bp = Blueprint('drap', __name__, url_prefix='/DRAP')

# Hardcoded credentials
DRAP_CREDENTIALS = {
    "username": "drap_admin",
    "password": "drap@2024"
}


def validate_drap_credentials(username, password):
    """Validate DRAP login credentials"""
    return (
        username == DRAP_CREDENTIALS["username"] and 
        password == DRAP_CREDENTIALS["password"]
    )


def register_drap_routes(server):
    """Register DRAP Flask routes with the server"""
    
    # Register the blueprint
    server.register_blueprint(drap_bp)
    
    logger.info("✅ DRAP Blueprint registered at /DRAP")
    print("✅ DRAP Endpoint registered:")
    print("   - Login: http://localhost:8050/DRAP")
    print("   - Credentials: drap_admin / drap@2024")


@drap_bp.route('/api/login', methods=['POST'])
def drap_api_login():
    """API endpoint for DRAP login validation"""
    data = request.get_json() or {}
    username = data.get('username', '')
    password = data.get('password', '')
    
    if validate_drap_credentials(username, password):
        session['drap_authenticated'] = True
        session['drap_user'] = username
        logger.info(f"DRAP login successful: {username}")
        return jsonify({
            "success": True,
            "message": "Authentication successful",
            "redirect": "/DRAP/dashboard"
        })
    else:
        logger.warning(f"DRAP login failed: {username}")
        return jsonify({
            "success": False,
            "message": "Invalid credentials"
        }), 401


@drap_bp.route('/logout')
def drap_logout():
    """Logout endpoint for DRAP"""
    session.pop('drap_authenticated', None)
    session.pop('drap_user', None)
    logger.info("DRAP user logged out")
    return redirect('/DRAP')


@drap_bp.route('/api/status')
def drap_status():
    """DRAP status API endpoint"""
    return jsonify({
        "status": "active",
        "endpoint": "/DRAP",
        "authenticated": session.get('drap_authenticated', False),
        "user": session.get('drap_user', None)
    })


@drap_bp.route('/health')
def drap_health():
    """Health check endpoint"""
    return jsonify({
        "healthy": True,
        "service": "DRAP",
        "version": "1.0.0"
    })