# endpoints/charts_page.py
"""
Charts Page Endpoint
Handles /charts route with interactive visualizations and chart data
"""

from flask import session, redirect, jsonify
from config.themes import THEMES, get_theme
from utils.page_builder import create_themed_page
import random
from datetime import datetime, timedelta

def get_current_theme():
    """Get current theme from session or default"""
    return session.get('current_theme', 'dark')

def create_charts_content(theme_name="dark"):
    """Create charts-specific content"""
    theme = get_theme(theme_name)
    
    # Charts-specific features
    features = [
        {
            "icon": "📊",
            "title": "Interactive Dashboards",
            "description": "Dynamic charts with real-time data updates"
        },
        {
            "icon": "📈",
            "title": "Performance Charts",
            "description": "Line charts, bar graphs, and trend visualizations"
        },
        {
            "icon": "🥧",
            "title": "Distribution Analysis",
            "description": "Pie charts and donut charts for data distribution"
        },
        {
            "icon": "🗺️",
            "title": "Geospatial Maps",
            "description": "Heat maps and geographic data visualization"
        },
        {
            "icon": "📉",
            "title": "Comparative Analysis",
            "description": "Multi-series charts for comparison studies"
        },
        {
            "icon": "⚡",
            "title": "Real-time Updates",
            "description": "Live data streaming and automatic chart updates"
        }
    ]
    
    # Chart configurations and types
    chart_types = {
        "performance_charts": [
            "Collection Efficiency Over Time",
            "Vehicle Utilization Rates",
            "Cost Analysis Trends",
            "Waste Volume Processing"
        ],
        "distribution_charts": [
            "Waste Type Distribution",
            "District-wise Collections",
            "Vehicle Fleet Status",
            "Budget Allocation"
        ],
        "comparison_charts": [
            "Monthly Performance Comparison",
            "District vs District Analysis",
            "Year-over-Year Growth",
            "Efficiency Benchmarking"
        ]
    }
    
    return {
        "features": features,
        "chart_types": chart_types,
        "description": "Interactive chart and visualization platform for waste management data. Create custom dashboards, export reports, and share insights with stakeholders.",
        "capabilities": [
            "Real-time interactive charts with drill-down capabilities",
            "Custom dashboard creation and sharing",
            "Export charts as PNG, PDF, or SVG formats",
            "Geographic heat maps and route visualizations",
            "Automated report generation with scheduled delivery",
            "Mobile-responsive charts for field team access"
        ]
    }

def generate_chart_data():
    """Generate sample chart data for visualizations"""
    # Generate data for different chart types
    dates = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7, 0, -1)]
    
    return {
        "line_chart_data": {
            "labels": dates,
            "datasets": [
                {
                    "label": "Collection Efficiency (%)",
                    "data": [random.randint(85, 98) for _ in dates],
                    "borderColor": "#3182CE",
                    "backgroundColor": "rgba(49, 130, 206, 0.1)"
                },
                {
                    "label": "Vehicle Utilization (%)",
                    "data": [random.randint(70, 90) for _ in dates],
                    "borderColor": "#38A169",
                    "backgroundColor": "rgba(56, 161, 105, 0.1)"
                }
            ]
        },
        "bar_chart_data": {
            "labels": ["Visakhapatnam", "Vijayawada", "Guntur", "Tirupati", "Kakinada", "Anantapur"],
            "datasets": [
                {
                    "label": "Collections This Month",
                    "data": [random.randint(100, 300) for _ in range(6)],
                    "backgroundColor": ["#3182CE", "#38A169", "#DD6B20", "#9F7AEA", "#E53E3E", "#319795"]
                }
            ]
        },
        "pie_chart_data": {
            "labels": ["Organic", "Plastic", "Paper", "Metal", "Glass", "Other"],
            "datasets": [
                {
                    "data": [35, 25, 15, 10, 8, 7],
                    "backgroundColor": ["#38A169", "#3182CE", "#DD6B20", "#9F7AEA", "#E53E3E", "#319795"]
                }
            ]
        },
        "area_chart_data": {
            "labels": dates,
            "datasets": [
                {
                    "label": "Waste Processed (tonnes)",
                    "data": [random.randint(800, 1200) for _ in dates],
                    "fill": True,
                    "backgroundColor": "rgba(56, 161, 105, 0.3)",
                    "borderColor": "#38A169"
                }
            ]
        }
    }

def register_charts_routes(server):
    """Register charts-specific routes"""
    
    @server.route('/charts')
    def charts_page():
        """Charts and Visualizations Page"""
        # Check authentication
        if not session.get('swaccha_session_id'):
            return redirect('/login')
        
        theme_name = get_current_theme()
        content = create_charts_content(theme_name)
        
        return create_themed_page(
            title="Charts",
            icon="📈",
            theme_name=theme_name,
            content=content,
            page_type="charts"
        )
    
    @server.route('/charts/data')
    def charts_data():
        """Charts data API endpoint"""
        if not session.get('swaccha_session_id'):
            return {'error': 'Authentication required'}, 401
        
        data = generate_chart_data()
        return jsonify(data)
    
    @server.route('/charts/export/<chart_type>')
    def export_chart(chart_type):
        """Export chart data endpoint"""
        if not session.get('swaccha_session_id'):
            return {'error': 'Authentication required'}, 401
        
        # In a real implementation, this would generate actual chart exports
        export_info = {
            "chart_type": chart_type,
            "export_url": f"/exports/chart_{chart_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
            "generated_at": datetime.now().isoformat(),
            "status": "ready"
        }
        
        return jsonify(export_info)
    
    @server.route('/charts/realtime')
    def realtime_chart_data():
        """Real-time chart data endpoint"""
        if not session.get('swaccha_session_id'):
            return {'error': 'Authentication required'}, 401
        
        # Simulate real-time data
        realtime_data = {
            "timestamp": datetime.now().isoformat(),
            "active_collections": random.randint(15, 45),
            "vehicles_in_transit": random.randint(25, 65),
            "processing_rate": random.randint(85, 98),
            "alerts": random.randint(0, 3),
            "citizen_reports_today": random.randint(5, 20)
        }
        
        return jsonify(realtime_data)