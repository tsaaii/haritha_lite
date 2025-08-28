# components/filters/filter_container.py
"""
Responsive Filter Container Component for Swaccha Andhra Dashboard
Updated to work with dynamic CSV data - NO HARDCODED OPTIONS
"""

from dash import html, dcc
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

def create_filter_container(theme, container_id="main-filter-container"):
    """
    Create a responsive filter container with Agency, Cluster, Site, and Date filters
    
    Args:
        theme (dict): Current theme configuration
        container_id (str): Unique container ID
        
    Returns:
        html.Div: Complete filter container component
    """
    
    # ✅ NO HARDCODED OPTIONS - These will be populated by callbacks from CSV data
    # The consolidated callbacks will update these dropdowns with real data
    initial_options = [{'label': 'Loading...', 'value': 'loading'}]
    
    # Base styles for filter components
    filter_input_style = {
        "width": "100%",
        "padding": "0.75rem",
        "border": f"2px solid {theme.get('border_light', theme['accent_bg'])}",
        "borderRadius": "8px",
        "backgroundColor": theme["card_bg"],
        "color": theme["text_primary"],
        "fontSize": "0.9rem",
        "fontWeight": "500",
        "outline": "none",
        "transition": "all 0.2s ease",
        "boxShadow": "0 2px 4px rgba(0, 0, 0, 0.1)"
    }
    
    filter_label_style = {
        "color": theme["text_primary"],
        "fontSize": "0.9rem",
        "fontWeight": "600",
        "marginBottom": "0.5rem",
        "display": "block"
    }
    
    # Create the main filter container
    return html.Div(
        id=container_id,
        className="filter-container-wrapper",
        style={
            "backgroundColor": theme["card_bg"],
            "border": f"2px solid {theme.get('border_light', theme['accent_bg'])}",
            "borderRadius": "12px",
            "padding": "1.5rem",
            "marginBottom": "2rem",
            "boxShadow": "0 4px 16px rgba(0, 0, 0, 0.1)"
        },
        children=[
            # Filter Container Header
            html.Div(
                className="filter-header",
                style={
                    "marginBottom": "1.5rem",
                    "textAlign": "center",
                    "borderBottom": f"2px solid {theme['accent_bg']}",
                    "paddingBottom": "1rem"
                },
                children=[
                    html.H3("🔍 Data Filters", style={
                        "color": theme["text_primary"],
                        "fontSize": "1.5rem",
                        "fontWeight": "700",
                        "margin": "0 0 0.5rem 0"
                    }),
                    html.P("Filter waste collection data by agency, location, and time period", style={
                        "color": theme["text_secondary"],
                        "fontSize": "0.9rem",
                        "margin": "0",
                        "lineHeight": "1.4"
                    })
                ]
            ),
            
            # Responsive Filter Grid
            html.Div(
                className="filter-grid",
                style={
                    "display": "grid",
                    "gridTemplateColumns": "repeat(auto-fit, minmax(250px, 1fr))",
                    "gap": "1.5rem",
                    "marginBottom": "1.5rem"
                },
                children=[
                    # Agency Filter - Will be populated by callback
                    html.Div(
                        className="filter-item",
                        children=[
                            html.Label(
                                "🏢 Agency",
                                style=filter_label_style
                            ),
                            dcc.Dropdown(
                                id=f"{container_id}-agency-filter",
                                options=initial_options,  # Will be updated by callback
                                value='all',
                                placeholder="Select Agency...",
                                clearable=False,
                                style={
                                    "fontSize": "0.9rem"
                                },
                                className="custom-dropdown"
                            )
                        ]
                    ),
                    
                    # Cluster Filter - Will be populated by callback
                    html.Div(
                        className="filter-item",
                        children=[
                            html.Label(
                                "🗺️ Cluster",
                                style=filter_label_style
                            ),
                            dcc.Dropdown(
                                id=f"{container_id}-cluster-filter",
                                options=initial_options,  # Will be updated by callback
                                value='all',
                                placeholder="Select Cluster...",
                                clearable=False,
                                style={
                                    "fontSize": "0.9rem"
                                },
                                className="custom-dropdown"
                            )
                        ]
                    ),
                    
                    # Site Filter - Will be populated by callback
                    html.Div(
                        className="filter-item",
                        children=[
                            html.Label(
                                "📍 Site",
                                style=filter_label_style
                            ),
                            dcc.Dropdown(
                                id=f"{container_id}-site-filter",
                                options=initial_options,  # Will be updated by callback
                                value='all',
                                placeholder="Select Site...",
                                clearable=False,
                                style={
                                    "fontSize": "0.9rem"
                                },
                                className="custom-dropdown"
                            )
                        ]
                    ),
                    
                    # Date Range Filter
                    html.Div(
                        className="filter-item",
                        children=[
                            html.Label(
                                "📅 Date Range",
                                style=filter_label_style
                            ),
                            dcc.DatePickerRange(
                                id=f"{container_id}-date-filter",
                                start_date=datetime.now() - timedelta(days=7),
                                end_date=datetime.now(),
                                display_format='DD/MM/YYYY',
                                style={
                                    "width": "100%",
                                    "fontSize": "0.9rem"
                                },
                                className="custom-date-picker"
                            )
                        ]
                    )
                ]
            ),
            
            # Filter Action Buttons
            html.Div(
                className="filter-actions",
                style={
                    "display": "flex",
                    "flexWrap": "wrap",
                    "gap": "1rem",
                    "justifyContent": "center",
                    "alignItems": "center",
                    "borderTop": f"1px solid {theme['accent_bg']}",
                    "paddingTop": "1.5rem"
                },
                children=[
                    # Apply Filters Button
                    html.Button(
                        [
                            html.Span("🔍", style={"marginRight": "0.5rem"}),
                            "Apply Filters"
                        ],
                        id=f"{container_id}-apply-btn",
                        className="filter-btn primary",
                        style={
                            "backgroundColor": theme["brand_primary"],
                            "color": "white",
                            "border": "none",
                            "padding": "0.75rem 1.5rem",
                            "borderRadius": "8px",
                            "fontSize": "0.9rem",
                            "fontWeight": "600",
                            "cursor": "pointer",
                            "transition": "all 0.2s ease",
                            "display": "flex",
                            "alignItems": "center",
                            "gap": "0.5rem",
                            "boxShadow": "0 2px 8px rgba(0, 0, 0, 0.2)",
                            "minWidth": "140px",
                            "justifyContent": "center"
                        }
                    ),
                    
                    # Reset Filters Button
                    html.Button(
                        [
                            html.Span("🔄", style={"marginRight": "0.5rem"}),
                            "Reset"
                        ],
                        id=f"{container_id}-reset-btn",
                        className="filter-btn secondary",
                        style={
                            "backgroundColor": theme["accent_bg"],
                            "color": theme["text_primary"],
                            "border": f"2px solid {theme.get('border_light', theme['accent_bg'])}",
                            "padding": "0.75rem 1.5rem",
                            "borderRadius": "8px",
                            "fontSize": "0.9rem",
                            "fontWeight": "600",
                            "cursor": "pointer",
                            "transition": "all 0.2s ease",
                            "display": "flex",
                            "alignItems": "center",
                            "gap": "0.5rem",
                            "minWidth": "120px",
                            "justifyContent": "center"
                        }
                    ),
                    
                    # Export Data Button
                    html.Button(
                        [
                            html.Span("📊", style={"marginRight": "0.5rem"}),
                            "Export"
                        ],
                        id=f"{container_id}-export-btn",
                        className="filter-btn export",
                        style={
                            "backgroundColor": theme.get("success_color", "#38A169"),
                            "color": "white",
                            "border": "none",
                            "padding": "0.75rem 1.5rem",
                            "borderRadius": "8px",
                            "fontSize": "0.9rem",
                            "fontWeight": "600",
                            "cursor": "pointer",
                            "transition": "all 0.2s ease",
                            "display": "flex",
                            "alignItems": "center",
                            "gap": "0.5rem",
                            "minWidth": "120px",
                            "justifyContent": "center"
                        }
                    )
                ]
            ),
            
            # Filter Status Indicator
            html.Div(
                id=f"{container_id}-status",
                className="filter-status",
                style={
                    "marginTop": "1rem",
                    "padding": "0.75rem",
                    "backgroundColor": theme["accent_bg"],
                    "borderRadius": "8px",
                    "textAlign": "center",
                    "fontSize": "0.85rem",
                    "color": theme["text_secondary"],
                    "display": "none"  # Hidden by default, shown by callbacks
                },
                children=[
                    html.Span(id=f"{container_id}-status-text", children="Ready to filter data")
                ]
            ),
            
            # Data loading indicator
            html.Div(
                id=f"{container_id}-loading",
                style={
                    "marginTop": "1rem",
                    "padding": "0.75rem",
                    "backgroundColor": theme["accent_bg"],
                    "borderRadius": "8px",
                    "textAlign": "center",
                    "fontSize": "0.85rem",
                    "color": theme["text_secondary"],
                    "display": "block"  # Shown initially
                },
                children=[
                    html.Span("🔄 Loading filter options from CSV data...", style={
                        "color": theme["brand_primary"]
                    })
                ]
            )
        ]
    )

def create_analytics_filter_container(theme):
    """
    Create filter container specifically for analytics page
    Uses 'analytics-filter-container' as ID to match consolidated callbacks
    """
    return create_filter_container(theme, container_id="analytics-filter-container")

def get_filter_options_from_csv():
    """
    Get filter options from CSV data - called by callbacks
    This is a helper function that the callbacks can use
    """
    try:
        from data_loader import get_cached_data, get_filter_options
        
        df = get_cached_data()
        
        if df.empty:
            logger.warning("No CSV data available for filter options")
            return {
                'agencies': [{'label': 'No Data Available', 'value': 'no_data'}],
                'clusters': [{'label': 'No Data Available', 'value': 'no_data'}],
                'sites': [{'label': 'No Data Available', 'value': 'no_data'}]
            }
        
        options = get_filter_options(df)
        logger.info(f"✅ Generated filter options from CSV: {len(options['agencies'])} agencies")
        return options
        
    except Exception as e:
        logger.error(f"❌ Error getting filter options from CSV: {e}")
        return {
            'agencies': [{'label': 'Error Loading Data', 'value': 'error'}],
            'clusters': [{'label': 'Error Loading Data', 'value': 'error'}],
            'sites': [{'label': 'Error Loading Data', 'value': 'error'}]
        }

def create_filter_container_styles():
    """
    Generate CSS styles for the filter container components
    
    Returns:
        str: CSS styles for responsive design
    """
    return """
    /* Filter Container Responsive Styles */
    .filter-container-wrapper {
        width: 100%;
        max-width: 100%;
        box-sizing: border-box;
    }
    
    .filter-grid {
        width: 100%;
    }
    
    /* Mobile Optimizations */
    @media (max-width: 768px) {
        .filter-container-wrapper {
            padding: 1rem !important;
            margin: 1rem 0 !important;
        }
        
        .filter-grid {
            grid-template-columns: 1fr !important;
            gap: 1rem !important;
        }
        
        .filter-actions {
            flex-direction: column !important;
            gap: 0.75rem !important;
        }
        
        .filter-btn {
            width: 100% !important;
            min-width: unset !important;
        }
        
        .filter-header h3 {
            font-size: 1.25rem !important;
        }
    }
    
    /* Tablet Optimizations */
    @media (min-width: 769px) and (max-width: 1024px) {
        .filter-grid {
            grid-template-columns: repeat(2, 1fr) !important;
        }
    }
    
    /* Dropdown Customization */
    .custom-dropdown .Select-control {
        border-radius: 8px !important;
        border-width: 2px !important;
        min-height: 44px !important;
    }
    
    .custom-dropdown .Select-menu-outer {
        border-radius: 8px !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15) !important;
    }
    
    /* Date Picker Customization */
    .custom-date-picker .DateInput {
        border-radius: 8px !important;
        border-width: 2px !important;
    }
    
    .custom-date-picker .DateRangePickerInput {
        border-radius: 8px !important;
    }
    
    /* Button Hover Effects */
    .filter-btn:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
    }
    
    .filter-btn:active {
        transform: translateY(0) !important;
    }
    
    /* Focus States */
    .custom-dropdown .Select-control:focus,
    .custom-date-picker .DateInput_input:focus {
        outline: 2px solid #3182CE !important;
        outline-offset: 2px !important;
    }
    
    /* Loading state styles */
    .filter-container-wrapper[data-loading="true"] .custom-dropdown {
        opacity: 0.6;
        pointer-events: none;
    }
    """

def get_filter_callback_template():
    """
    Template for filter callbacks - updated for CSV integration
    
    Returns:
        str: Python code template for implementing filter callbacks
    """
    return '''
from dash import callback, Input, Output, State
from dash.exceptions import PreventUpdate
from data_loader import get_cached_data, filter_data, create_filtered_data_display

@callback(
    [Output('filtered-data-display', 'children'),
     Output('analytics-filter-container-status', 'style'),
     Output('analytics-filter-container-status-text', 'children')],
    [Input('analytics-filter-container-apply-btn', 'n_clicks')],
    [State('analytics-filter-container-agency-filter', 'value'),
     State('analytics-filter-container-cluster-filter', 'value'),
     State('analytics-filter-container-site-filter', 'value'),
     State('analytics-filter-container-date-filter', 'start_date'),
     State('analytics-filter-container-date-filter', 'end_date'),
     State('current-theme', 'data')],
    prevent_initial_call=True
)
def apply_filters(n_clicks, agency, cluster, site, start_date, end_date, theme_name):
    """Apply filters using real CSV data"""
    if not n_clicks:
        raise PreventUpdate
    
    # Load data from CSV
    df = get_cached_data()
    
    # Apply filters
    filtered_df = filter_data(df, agency, cluster, site, start_date, end_date)
    
    # Create display
    from utils.theme_utils import get_theme_styles
    theme_styles = get_theme_styles(theme_name or 'dark')
    theme = theme_styles["theme"]
    
    display = create_filtered_data_display(filtered_df, theme)
    
    # Update status
    status_style = {"display": "block"}
    status_text = f"✅ Applied filters: {len(filtered_df)} records found"
    
    return display, status_style, status_text

@callback(
    [Output('analytics-filter-container-agency-filter', 'options'),
     Output('analytics-filter-container-cluster-filter', 'options'),
     Output('analytics-filter-container-site-filter', 'options'),
     Output('analytics-filter-container-loading', 'style')],
    [Input('analytics-filter-container', 'id')],
    prevent_initial_call=True
)
def update_filter_options(component_id):
    """Update filter options from CSV data"""
    try:
        options = get_filter_options_from_csv()
        
        # Hide loading indicator
        loading_style = {"display": "none"}
        
        return options['agencies'], options['clusters'], options['sites'], loading_style
        
    except Exception as e:
        # Show error in loading indicator
        loading_style = {"display": "block", "color": "#ff4444"}
        
        fallback_options = [{'label': 'Error Loading Data', 'value': 'error'}]
        return fallback_options, fallback_options, fallback_options, loading_style
'''

# Export functions
__all__ = [
    'create_filter_container',
    'create_analytics_filter_container',
    'create_filter_container_styles', 
    'get_filter_callback_template',
    'get_filter_options_from_csv'
]