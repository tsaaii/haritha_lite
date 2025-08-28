from flask import Blueprint, jsonify, request, session, current_app
from functools import wraps
import logging
import traceback
import sys
import os
import psutil
from datetime import datetime
import platform

# Create blueprint for debug routes
debug_bp = Blueprint('debug', __name__)

def debug_required(f):
    """Decorator to ensure debug mode is enabled"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_app.debug:
            return jsonify({'error': 'Debug mode not enabled'}), 403
        return f(*args, **kwargs)
    return decorated_function

@debug_bp.route('/debug')
@debug_required
def debug_info():
    """Main debug information page"""
    try:
        debug_data = {
            'app_info': get_app_info(),
            'system_info': get_system_info(),
            'session_info': get_session_info(),
            'environment_info': get_environment_info()
        }
        return jsonify(debug_data)
    except Exception as e:
        logging.error(f"Error getting debug info: {e}")
        return jsonify({'error': 'Failed to get debug info'}), 500

@debug_bp.route('/debug/config')
@debug_required
def debug_config():
    """Show application configuration (sanitized)"""
    try:
        config_info = {}
        
        # Sanitize sensitive configuration values
        sensitive_keys = ['SECRET_KEY', 'PASSWORD', 'TOKEN', 'CLIENT_SECRET', 'API_KEY']
        
        for key, value in current_app.config.items():
            if any(sensitive in key.upper() for sensitive in sensitive_keys):
                config_info[key] = '***HIDDEN***'
            else:
                config_info[key] = str(value)
        
        return jsonify({
            'config': config_info,
            'config_count': len(config_info)
        })
    except Exception as e:
        logging.error(f"Error getting config info: {e}")
        return jsonify({'error': 'Failed to get config info'}), 500

@debug_bp.route('/debug/routes')
@debug_required
def debug_routes():
    """Show all registered routes"""
    try:
        routes = []
        for rule in current_app.url_map.iter_rules():
            routes.append({
                'endpoint': rule.endpoint,
                'methods': list(rule.methods),
                'rule': str(rule),
                'subdomain': rule.subdomain or 'None'
            })
        
        return jsonify({
            'routes': sorted(routes, key=lambda x: x['rule']),
            'total_routes': len(routes)
        })
    except Exception as e:
        logging.error(f"Error getting routes info: {e}")
        return jsonify({'error': 'Failed to get routes info'}), 500

@debug_bp.route('/debug/session')
@debug_required
def debug_session():
    """Show current session data"""
    try:
        session_data = dict(session)
        
        # Sanitize sensitive session data
        sensitive_keys = ['password', 'token', 'secret']
        for key in list(session_data.keys()):
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                session_data[key] = '***HIDDEN***'
        
        return jsonify({
            'session': session_data,
            'session_keys': list(session_data.keys())
        })
    except Exception as e:
        logging.error(f"Error getting session info: {e}")
        return jsonify({'error': 'Failed to get session info'}), 500

@debug_bp.route('/debug/logs')
@debug_required
def debug_logs():
    """Show recent log entries"""
    try:
        # This is a simplified implementation
        # In production, you'd want to read from actual log files
        log_entries = [
            {'level': 'INFO', 'message': 'Application started', 'timestamp': datetime.utcnow().isoformat()},
            {'level': 'DEBUG', 'message': 'Debug mode enabled', 'timestamp': datetime.utcnow().isoformat()}
        ]
        
        return jsonify({
            'logs': log_entries,
            'log_count': len(log_entries)
        })
    except Exception as e:
        logging.error(f"Error getting logs: {e}")
        return jsonify({'error': 'Failed to get logs'}), 500

@debug_bp.route('/debug/memory')
@debug_required
def debug_memory():
    """Show memory usage information"""
    try:
        process = psutil.Process()
        memory_info = process.memory_info()
        
        memory_data = {
            'rss': memory_info.rss,  # Resident Set Size
            'vms': memory_info.vms,  # Virtual Memory Size
            'rss_mb': round(memory_info.rss / 1024 / 1024, 2),
            'vms_mb': round(memory_info.vms / 1024 / 1024, 2),
            'memory_percent': process.memory_percent(),
            'cpu_percent': process.cpu_percent()
        }
        
        return jsonify(memory_data)
    except Exception as e:
        logging.error(f"Error getting memory info: {e}")
        return jsonify({'error': 'Failed to get memory info'}), 500

@debug_bp.route('/debug/headers')
@debug_required
def debug_headers():
    """Show request headers"""
    try:
        headers = dict(request.headers)
        
        return jsonify({
            'headers': headers,
            'method': request.method,
            'url': request.url,
            'remote_addr': request.remote_addr,
            'user_agent': request.user_agent.string if request.user_agent else None
        })
    except Exception as e:
        logging.error(f"Error getting headers info: {e}")
        return jsonify({'error': 'Failed to get headers info'}), 500

@debug_bp.route('/debug/error-test')
@debug_required
def debug_error_test():
    """Intentionally trigger an error for testing"""
    try:
        # Simulate different types of errors based on query parameter
        error_type = request.args.get('type', 'generic')
        
        if error_type == 'division':
            result = 1 / 0
        elif error_type == 'key':
            test_dict = {}
            value = test_dict['nonexistent_key']
        elif error_type == 'index':
            test_list = []
            value = test_list[0]
        elif error_type == 'type':
            result = "string" + 5
        else:
            raise Exception("Test error for debugging purposes")
            
    except Exception as e:
        # Return the error information for debugging
        return jsonify({
            'error': str(e),
            'error_type': type(e).__name__,
            'traceback': traceback.format_exc(),
            'requested_error_type': error_type
        }), 500

@debug_bp.route('/debug/clear-session', methods=['POST'])
@debug_required
def debug_clear_session():
    """Clear the current session"""
    try:
        session.clear()
        return jsonify({'message': 'Session cleared successfully'})
    except Exception as e:
        logging.error(f"Error clearing session: {e}")
        return jsonify({'error': 'Failed to clear session'}), 500

@debug_bp.route('/debug/database-test')
@debug_required
def debug_database_test():
    """Test database connectivity"""
    try:
        # TODO: Implement actual database connection test
        # This would test your database connection and return status
        
        db_status = {
            'connected': True,  # This would be the actual test result
            'connection_info': 'Database connection test not implemented',
            'last_checked': datetime.utcnow().isoformat()
        }
        
        return jsonify(db_status)
    except Exception as e:
        logging.error(f"Error testing database: {e}")
        return jsonify({'error': 'Database test failed'}), 500

def get_app_info():
    """Get Flask application information"""
    return {
        'name': current_app.name,
        'debug': current_app.debug,
        'testing': current_app.testing,
        'instance_path': current_app.instance_path,
        'root_path': current_app.root_path,
        'blueprint_count': len(current_app.blueprints)
    }

def get_system_info():
    """Get system information"""
    return {
        'platform': platform.platform(),
        'python_version': sys.version,
        'executable': sys.executable,
        'path': sys.path[:5],  # First 5 paths only
        'working_directory': os.getcwd(),
        'process_id': os.getpid()
    }

def get_session_info():
    """Get session information (sanitized)"""
    return {
        'session_keys': list(session.keys()),
        'session_count': len(session),
        'permanent': session.permanent
    }

def get_environment_info():
    """Get environment variables (sanitized)"""
    env_vars = {}
    sensitive_env_vars = ['PASSWORD', 'SECRET', 'KEY', 'TOKEN', 'API']
    
    for key, value in os.environ.items():
        if any(sensitive in key.upper() for sensitive in sensitive_env_vars):
            env_vars[key] = '***HIDDEN***'
        else:
            env_vars[key] = value
    
    return {
        'environment_variables': env_vars,
        'env_count': len(env_vars)
    }

def register_debug_routes(app):
    """Register debug routes with the Flask app"""
    app.register_blueprint(debug_bp)