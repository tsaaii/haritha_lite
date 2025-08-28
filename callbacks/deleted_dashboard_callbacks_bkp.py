# callbacks/dashboard_callbacks.py
"""
Dashboard Route Callbacks for Aligned Navigation
Handles theme switching, tab navigation, and logout
"""

from dash import callback, Input, Output, State, html, ctx
from dash.exceptions import PreventUpdate
from config.themes import THEMES, DEFAULT_THEME
import dash
from dash import callback, Input, Output, State, ctx
from dash.exceptions import PreventUpdate
import pandas as pd
from datetime import datetime, timedelta




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
def apply_analytics_filters(n_clicks, agency, cluster, site, start_date, end_date, theme_name):
    """Apply filters and update data display"""
    if not n_clicks:
        raise PreventUpdate
    
    # Get theme for styling
    from utils.theme_utils import get_theme_styles
    theme_styles = get_theme_styles(theme_name or 'dark')
    theme = theme_styles["theme"]
    
    # TODO: Replace with your actual data filtering logic
    # For now, showing sample filtered results
    
    # Create sample filtered display
    filtered_display = create_filtered_data_display(
        agency, cluster, site, start_date, end_date, theme
    )
    
    # Update status
    status_style = {"display": "block"}
    status_text = f"✅ Filters applied: {agency}, {cluster}, {site} ({start_date} to {end_date})"
    
    return filtered_display, status_style, status_text

@callback(
    [Output('analytics-filter-container-agency-filter', 'value'),
     Output('analytics-filter-container-cluster-filter', 'value'),
     Output('analytics-filter-container-site-filter', 'value'),
     Output('analytics-filter-container-date-filter', 'start_date'),
     Output('analytics-filter-container-date-filter', 'end_date')],
    [Input('analytics-filter-container-reset-btn', 'n_clicks')],
    prevent_initial_call=True
)
def reset_analytics_filters(n_clicks):
    """Reset all filters to default values"""
    if not n_clicks:
        raise PreventUpdate
    
    default_start_date = datetime.now() - timedelta(days=7)
    default_end_date = datetime.now()
    
    return 'all', 'all', 'all', default_start_date, default_end_date

def create_filtered_data_display(agency, cluster, site, start_date, end_date, theme):
    """Create the filtered data display component"""
    
    # Sample implementation - replace with your actual data processing
    return html.Div([
        # Filter summary
        html.Div([
            html.H4("📊 Filtered Results", style={
                "color": theme["text_primary"],
                "marginBottom": "1rem"
            }),
            html.Div([
                html.Span(f"Agency: {agency} | ", style={"color": theme["text_secondary"]}),
                html.Span(f"Cluster: {cluster} | ", style={"color": theme["text_secondary"]}),
                html.Span(f"Site: {site} | ", style={"color": theme["text_secondary"]}),
                html.Span(f"Date: {start_date} to {end_date}", style={"color": theme["text_secondary"]})
            ], style={"marginBottom": "1.5rem"})
        ]),
        
        # Sample metrics cards
        html.Div([
            create_metric_card("Total Collections", "1,247", "📦", theme),
            create_metric_card("Total Weight", "2,856 tons", "⚖️", theme),
            create_metric_card("Efficiency", "94.2%", "⚡", theme),
            create_metric_card("Active Vehicles", "23", "🚛", theme),
        ], style={
            "display": "grid",
            "gridTemplateColumns": "repeat(auto-fit, minmax(200px, 1fr))",
            "gap": "1rem",
            "marginBottom": "2rem"
        }),
        
        # Placeholder for charts/tables
        html.Div([
            html.H5("📈 Data Visualization", style={
                "color": theme["text_primary"],
                "marginBottom": "1rem"
            }),
            html.Div(
                "Charts and detailed data tables will appear here based on your filtered data",
                style={
                    "padding": "2rem",
                    "backgroundColor": theme["accent_bg"],
                    "borderRadius": "8px",
                    "textAlign": "center",
                    "color": theme["text_secondary"],
                    "border": f"2px dashed {theme['card_bg']}"
                }
            )
        ])
    ], style={
        "backgroundColor": theme["card_bg"],
        "padding": "1.5rem",
        "borderRadius": "12px",
        "border": f"2px solid {theme['accent_bg']}"
    })

def create_metric_card(title, value, icon, theme):
    """Create a metric card for the filtered display"""
    return html.Div([
        html.Div([
            html.Span(icon, style={"fontSize": "1.5rem", "marginRight": "0.5rem"}),
            html.Span(title, style={"fontSize": "0.9rem", "color": theme["text_secondary"]})
        ], style={"marginBottom": "0.5rem"}),
        html.Div(value, style={
            "fontSize": "1.5rem",
            "fontWeight": "700",
            "color": theme["text_primary"]
        })
    ], style={
        "backgroundColor": theme["accent_bg"],
        "padding": "1rem",
        "borderRadius": "8px",
        "border": f"1px solid {theme.get('border_light', theme['card_bg'])}",
        "textAlign": "center"
    })


# 4. Update your main.py to include the new CSS
# Add this to your app initialization:



def register_dashboard_callbacks(app):
    """Register all dashboard-specific callbacks"""
    
    # Theme switching callback
    @app.callback(
        [Output('current-theme', 'data'),
         Output('dashboard-route', 'data-theme')],  # Update data-theme attribute
        [Input('theme-dark', 'n_clicks'),
         Input('theme-light', 'n_clicks'),
         Input('theme-high_contrast', 'n_clicks'),
         Input('theme-swaccha_green', 'n_clicks')],
        [State('current-theme', 'data')],
        prevent_initial_call=True
    )
    def update_dashboard_theme(dark_clicks, light_clicks, contrast_clicks, green_clicks, current_theme):
        """Update theme for dashboard route"""
        if not ctx.triggered:
            raise PreventUpdate
            
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        theme_map = {
            'theme-dark': 'dark',
            'theme-light': 'light',
            'theme-high_contrast': 'high_contrast',
            'theme-swaccha_green': 'swaccha_green'
        }
        
        new_theme = theme_map.get(button_id, current_theme or DEFAULT_THEME)
        return new_theme, new_theme

    # Tab navigation callback
    @app.callback(
        [Output('active-tab', 'data'),
         Output('tab-content', 'children')],
        [Input('tab-dashboard', 'n_clicks'),
         Input('tab-analytics', 'n_clicks'),
         Input('tab-charts', 'n_clicks'),
         Input('tab-reports', 'n_clicks'),
         Input('tab-reviews', 'n_clicks'),
         Input('tab-forecasting', 'n_clicks'),
         Input('tab-upload', 'n_clicks')],
        [State('current-theme', 'data'),
         State('active-tab', 'data')],
        prevent_initial_call=True
    )
    def handle_tab_navigation(dash_clicks, analytics_clicks, charts_clicks, reports_clicks, 
                            reviews_clicks, forecast_clicks, upload_clicks, theme_name, current_tab):
        """Handle tab navigation and content updates"""
        if not ctx.triggered:
            raise PreventUpdate
            
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        tab_map = {
            'tab-dashboard': 'dashboard',
            'tab-analytics': 'analytics',
            'tab-charts': 'charts',
            'tab-reports': 'reports',
            'tab-reviews': 'reviews',
            'tab-forecasting': 'forecasting',
            'tab-upload': 'upload'
        }
        
        new_tab = tab_map.get(button_id, current_tab or 'dashboard')
        content = get_tab_content(new_tab, theme_name or DEFAULT_THEME)
        
        return new_tab, content

    # Logout callback
    @app.callback(
        [Output('user-authenticated', 'data'),
         Output('url', 'pathname')],
        Input('logout-btn', 'n_clicks'),
        prevent_initial_call=True
    )
    def handle_logout(n_clicks):
        """Handle user logout"""
        if n_clicks:
            return False, '/'  # Redirect to home page
        raise PreventUpdate

    # Update navigation button states based on active tab
    @app.callback(
        [Output('tab-dashboard', 'className'),
         Output('tab-analytics', 'className'),
         Output('tab-charts', 'className'),
         Output('tab-reports', 'className'),
         Output('tab-reviews', 'className'),
         Output('tab-forecasting', 'className'),
         Output('tab-upload', 'className')],
        Input('active-tab', 'data'),
        prevent_initial_call=True
    )
    def update_nav_button_states(active_tab):
        """Update navigation button active states"""
        tabs = ['dashboard', 'analytics', 'charts', 'reports', 'reviews', 'forecasting', 'upload']
        return [f"nav-tab {'active' if tab == active_tab else ''}" for tab in tabs]

    # Update theme button states
    @app.callback(
        [Output('theme-dark', 'className'),
         Output('theme-light', 'className'),
         Output('theme-high_contrast', 'className'),
         Output('theme-swaccha_green', 'className')],
        Input('current-theme', 'data'),
        prevent_initial_call=True
    )
    def update_theme_button_states(current_theme):
        """Update theme button active states"""
        themes = ['dark', 'light', 'high_contrast', 'swaccha_green']
        return [f"theme-btn {'active' if theme == current_theme else ''}" for theme in themes]

def get_tab_content(tab_name, theme_name):
    """
    Generate content for different tabs
    
    Args:
        tab_name (str): Name of the tab
        theme_name (str): Current theme
        
    Returns:
        html.Div: Tab content
    """
    theme = THEMES[theme_name]
    
    content_map = {
        'dashboard': {
            'title': '📊 Dashboard Overview',
            'description': 'Real-time monitoring of waste collection and management across Andhra Pradesh.',
            'features': ['Live vehicle tracking', 'Collection efficiency metrics', 'Route optimization data']
        },
        'analytics': {
            'title': '📈 Data Analytics',
            'description': 'Advanced analytics and insights from waste management data.',
            'features': ['Trend analysis', 'Predictive modeling', 'Performance metrics']
        },
        'charts': {
            'title': '📉 Charts & Visualizations',
            'description': 'Interactive charts and graphs for data visualization.',
            'features': ['Custom dashboards', 'Export capabilities', 'Real-time updates']
        },
        'reports': {
            'title': '📋 Reports',
            'description': 'Comprehensive reports and documentation.',
            'features': ['Automated reports', 'Custom filters', 'PDF exports']
        },
        'reviews': {
            'title': '⭐ Reviews & Feedback',
            'description': 'Public feedback and service reviews management.',
            'features': ['Customer ratings', 'Complaint tracking', 'Response management']
        },
        'forecasting': {
            'title': '🔮 Forecasting',
            'description': 'Predictive analytics for waste management planning.',
            'features': ['Demand forecasting', 'Resource planning', 'Capacity optimization']
        },
        'upload': {
            'title': '📤 Data Upload',
            'description': 'Upload and manage data files and documents.',
            'features': ['Bulk data import', 'File validation', 'Processing status']
        }
    }
    
    content = content_map.get(tab_name, content_map['dashboard'])
    
    return html.Div(
        style={
            "padding": "2rem",
            "backgroundColor": theme["accent_bg"],
            "border": f"2px solid {theme['card_bg']}",
            "borderRadius": "12px",
            "minHeight": "400px"
        },
        children=[
            html.H2(
                content['title'],
                style={"color": theme["text_primary"], "marginBottom": "1rem"}
            ),
            html.P(
                content['description'],
                style={"color": theme["text_secondary"], "marginBottom": "2rem", "fontSize": "1.1rem"}
            ),
            html.H3(
                "Features:",
                style={"color": theme["text_primary"], "marginBottom": "1rem"}
            ),
            html.Ul(
                children=[
                    html.Li(
                        feature,
                        style={"color": theme["text_secondary"], "marginBottom": "0.5rem"}
                    ) for feature in content['features']
                ],
                style={"paddingLeft": "1.5rem"}
            ),
            
            # Placeholder for future content
            html.Div(
                style={
                    "marginTop": "2rem",
                    "padding": "1.5rem",
                    "backgroundColor": theme["card_bg"],
                    "borderRadius": "8px",
                    "border": f"1px solid {theme['border_light']}"
                },
                children=[
                    html.P(
                        f"🚧 {content['title']} functionality is coming soon!",
                        style={
                            "color": theme["warning"],
                            "fontWeight": "600",
                            "textAlign": "center",
                            "margin": "0"
                        }
                    )
                ]
            )
        ]
    )


app = dash.Dash(
    __name__, 
    suppress_callback_exceptions=True,
    external_stylesheets=[
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap",
        "/assets/filter_styles.css"  # Add this line
    ]
)
