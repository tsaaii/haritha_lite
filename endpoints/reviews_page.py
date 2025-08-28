from flask import Blueprint, request, jsonify, session, redirect, url_for
from functools import wraps
import logging
from config.themes import THEMES, get_theme
from utils.page_builder import create_themed_page

# Create blueprint for reviews routes
reviews_bp = Blueprint('reviews', __name__)

def get_current_theme():
    """Get current theme from session or default"""
    return session.get('current_theme', 'dark')

def create_reviews_content(theme_name="dark"):
    """Create reviews-specific content"""
    theme = get_theme(theme_name)
    
    # Reviews-specific features
    features = [
        {
            "icon": "⭐",
            "title": "Customer Ratings",
            "description": "Comprehensive rating system for service quality"
        },
        {
            "icon": "💬",
            "title": "Feedback Management",
            "description": "Centralized feedback collection and analysis"
        },
        {
            "icon": "📊",
            "title": "Sentiment Analysis",
            "description": "AI-powered sentiment analysis of reviews"
        },
        {
            "icon": "🔔",
            "title": "Real-time Notifications",
            "description": "Instant alerts for new reviews and feedback"
        },
        {
            "icon": "📈",
            "title": "Performance Tracking",
            "description": "Track service improvements over time"
        },
        {
            "icon": "🎯",
            "title": "Action Items",
            "description": "Convert feedback into actionable improvements"
        }
    ]
    
    return {
        "features": features,
        "description": "Comprehensive review and feedback management system for waste collection services. Monitor customer satisfaction, track performance, and implement improvements based on public feedback.",
        "capabilities": [
            "Multi-channel feedback collection (web, mobile, phone)",
            "Real-time review monitoring and sentiment analysis",
            "Automated response templates and acknowledgments",
            "Performance tracking and improvement recommendations",
            "Integration with service quality metrics",
            "Public transparency dashboard for community engagement"
        ]
    }

def login_required(f):
    """Decorator to require login for protected routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'swaccha_session_id' not in session:
            return redirect('/oauth/login')
        return f(*args, **kwargs)
    return decorated_function

@reviews_bp.route('/reviews')
@login_required
def reviews_page():
    """Main reviews page"""
    try:
        theme_name = get_current_theme()
        content = create_reviews_content(theme_name)
        
        return create_themed_page(
            title="Reviews & Feedback",
            icon="⭐",
            theme_name=theme_name,
            content=content,
            page_type="reviews"
        )
    except Exception as e:
        logging.error(f"Error loading reviews page: {e}")
        return "Error loading reviews page", 500

@reviews_bp.route('/api/reviews', methods=['GET'])
@login_required
def get_reviews():
    """API endpoint to get reviews data"""
    try:
        # TODO: Implement reviews data retrieval logic
        # This would typically fetch from a database
        reviews_data = {
            'reviews': [],
            'total_count': 0,
            'average_rating': 0.0
        }
        return jsonify(reviews_data)
    except Exception as e:
        logging.error(f"Error fetching reviews: {e}")
        return jsonify({'error': 'Failed to fetch reviews'}), 500

@reviews_bp.route('/api/reviews', methods=['POST'])
@login_required
def create_review():
    """API endpoint to create a new review"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['rating', 'comment']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # TODO: Implement review creation logic
        # This would typically save to a database
        
        return jsonify({'message': 'Review created successfully'}), 201
    except Exception as e:
        logging.error(f"Error creating review: {e}")
        return jsonify({'error': 'Failed to create review'}), 500

@reviews_bp.route('/api/reviews/<int:review_id>', methods=['PUT'])
@login_required
def update_review(review_id):
    """API endpoint to update a review"""
    try:
        data = request.get_json()
        
        # TODO: Implement review update logic
        # Verify user owns the review before updating
        
        return jsonify({'message': 'Review updated successfully'})
    except Exception as e:
        logging.error(f"Error updating review {review_id}: {e}")
        return jsonify({'error': 'Failed to update review'}), 500

@reviews_bp.route('/api/reviews/<int:review_id>', methods=['DELETE'])
@login_required
def delete_review(review_id):
    """API endpoint to delete a review"""
    try:
        # TODO: Implement review deletion logic
        # Verify user owns the review before deleting
        
        return jsonify({'message': 'Review deleted successfully'})
    except Exception as e:
        logging.error(f"Error deleting review {review_id}: {e}")
        return jsonify({'error': 'Failed to delete review'}), 500

def register_reviews_routes(app):
    """Register reviews routes with the Flask app"""
    app.register_blueprint(reviews_bp)


def require_tab_access(tab_name):
    """
    Decorator to require specific tab access for Flask routes
    
    Args:
        tab_name (str): Name of the tab to check access for
    """
    def decorator(f):
        def wrapper(*args, **kwargs):
            from flask import session, redirect, url_for
            
            # Check if user is authenticated
            user_data = session.get('user_data', {})
            if not user_data:
                return redirect('/login')
            
            user_role = user_data.get('role', 'viewer')
            
            # Check tab access
            try:
                from config.auth import can_user_access_tab
                if not can_user_access_tab(user_role, tab_name):
                    # Redirect to dashboard with error message
                    return redirect('/dashboard?error=access_denied')
            except ImportError:
                pass  # Allow access in demo mode
            
            return f(*args, **kwargs)
        
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator