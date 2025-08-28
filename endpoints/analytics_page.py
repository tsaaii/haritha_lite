# endpoints/analytics_page.py
"""
Analytics Page Endpoint
Handles /analytics and /data-analytics routes with advanced analytics features
"""

from flask import session, redirect, jsonify
from config.themes import THEMES, get_theme
from utils.page_builder import create_themed_page
import random
from datetime import datetime, timedelta

def get_current_theme():
    """Get current theme from session or default"""
    return session.get('current_theme', 'dark')

def create_analytics_content(theme_name="dark"):
    """Create analytics-specific content"""
    theme = get_theme(theme_name)
    
    # Analytics-specific features
    features = [
        {
            "icon": "📈",
            "title": "Trend Analysis",
            "description": "Historical data analysis and trend identification"
        },
        {
            "icon": "🤖",
            "title": "Predictive Analytics",
            "description": "ML-powered forecasting and predictions"
        },
        {
            "icon": "📊",
            "title": "Performance Dashboards",
            "description": "Interactive charts and visualizations"
        },
        {
            "icon": "🎯",
            "title": "KPI Tracking",
            "description": "Key performance indicators monitoring"
        },
        {
            "icon": "📉",
            "title": "Cost Analysis",
            "description": "Financial performance and cost optimization"
        },
        {
            "icon": "🔍",
            "title": "Deep Insights",
            "description": "Advanced data mining and pattern recognition"
        }
    ]
    
    # Sample analytics metrics
    analytics_data = {
        "efficiency_trends": {
            "current_month": "94.2%",
            "previous_month": "91.8%",
            "improvement": "+2.4%"
        },
        "collection_patterns": {
            "peak_hours": "6:00 AM - 10:00 AM",
            "optimal_routes": "127 active routes",
            "avg_collection_time": "2.3 hours"
        },
        "predictive_insights": {
            "next_week_demand": "15% increase expected",
            "maintenance_alerts": "3 vehicles due for service",
            "capacity_forecast": "98% utilization predicted"
        }
    }
    
    return {
        "features": features,
        "analytics_data": analytics_data,
        "description": "Advanced analytics platform for waste management optimization. Leverage data-driven insights to improve operational efficiency and make informed decisions.",
        "capabilities": [
            "Machine learning-powered predictive analytics",
            "Real-time performance monitoring and alerting",
            "Historical trend analysis and pattern recognition",
            "Cost optimization and budget forecasting",
            "Route efficiency analysis and optimization recommendations",
            "Citizen satisfaction analytics and feedback insights"
        ]
    }

def generate_sample_analytics_data():
    """Generate sample analytics data for API endpoints"""
    # Generate sample time series data
    dates = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(30, 0, -1)]
    
    return {
        "collection_efficiency": [
            {"date": date, "efficiency": random.randint(85, 98)} 
            for date in dates
        ],
        "waste_volume": [
            {"date": date, "volume": random.randint(800, 1200)} 
            for date in dates
        ],
        "cost_analysis": [
            {"date": date, "cost": random.randint(45000, 75000)} 
            for date in dates
        ],
        "vehicle_utilization": [
            {"vehicle_id": f"AP-{i:02d}", "utilization": random.randint(70, 95)} 
            for i in range(1, 21)
        ],
        "district_performance": [
            {
                "district": district,
                "collections": random.randint(50, 150),
                "efficiency": random.randint(80, 98)
            }
            for district in ["Visakhapatnam", "Vijayawada", "Guntur", "Tirupati", "Kakinada", "Anantapur"]
        ]
    }

def register_analytics_routes(server):
    """Register analytics-specific routes"""
    
    @server.route('/analytics')
    @server.route('/data-analytics')
    def analytics_page():
        """Analytics Page"""
        # Check authentication
        if not session.get('swaccha_session_id'):
            return redirect('/login')
        
        theme_name = get_current_theme()
        content = create_analytics_content(theme_name)
        
        return create_themed_page(
            title="Data Analytics",
            icon="📈",
            theme_name=theme_name,
            content=content,
            page_type="analytics"
        )
    
    @server.route('/analytics/data')
    def analytics_data():
        """Analytics data API endpoint"""
        if not session.get('swaccha_session_id'):
            return {'error': 'Authentication required'}, 401
        
        data = generate_sample_analytics_data()
        return jsonify(data)
    
    @server.route('/analytics/trends')
    def analytics_trends():
        """Analytics trends API endpoint"""
        if not session.get('swaccha_session_id'):
            return {'error': 'Authentication required'}, 401
        
        trends = {
            "weekly_trends": {
                "collections": {"trend": "increasing", "percentage": 8.2},
                "efficiency": {"trend": "stable", "percentage": 1.1},
                "costs": {"trend": "decreasing", "percentage": -3.5}
            },
            "monthly_insights": {
                "best_performing_district": "Visakhapatnam",
                "improvement_needed": "Anantapur",
                "overall_satisfaction": 4.6
            },
            "predictions": {
                "next_month_collections": 15240,
                "expected_efficiency": 96.2,
                "projected_savings": "₹2.8 lakhs"
            }
        }
        
        return jsonify(trends)