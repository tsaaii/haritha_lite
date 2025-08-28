# utils/dashboard_styles.py
"""
Dashboard Route Styling with Theme Integration
Provides utilities for applying themed styles to dashboard route
"""

from config.themes import THEMES, DEFAULT_THEME

def get_dashboard_html_wrapper(theme_name=None):
    """
    Get HTML wrapper with theme data attribute for dashboard route
    
    Args:
        theme_name (str): Current theme name
        
    Returns:
        dict: HTML wrapper properties
    """
    if theme_name is None:
        theme_name = DEFAULT_THEME
        
    return {
        "className": "dashboard-route",
        "data-theme": theme_name,
        "style": {
            "minHeight": "100vh",
            "backgroundColor": THEMES[theme_name]["primary_bg"],
            "color": THEMES[theme_name]["text_primary"],
            "fontFamily": "'Inter', sans-serif"
        }
    }

def create_aligned_navigation_header(theme_name, user_data=None, active_tab="dashboard"):
    """
    Create aligned navigation header for dashboard route
    
    Args:
        theme_name (str): Current theme name
        user_data (dict): User information
        active_tab (str): Currently active tab
        
    Returns:
        html.Div: Aligned navigation header component
    """
    from dash import html
    
    # Default user data if none provided
    if not user_data:
        user_data = {
            "name": "Administrator",
            "email": "admin@swacchaandhra.gov.in", 
            "role": "Super Admin",
            "picture": "/assets/img/default-avatar.png"
        }
    
    # Navigation buttons data
    nav_buttons = [
        {"id": "nav-dashboard", "icon": "📊", "label": "Dashboard", "active": active_tab == "dashboard"},
        {"id": "nav-analytics", "icon": "📈", "label": "Data Analytics", "active": active_tab == "analytics"},
        {"id": "nav-charts", "icon": "📉", "label": "Charts", "active": active_tab == "charts"},
        {"id": "nav-reports", "icon": "📋", "label": "Reports", "active": active_tab == "reports"},
        {"id": "nav-reviews", "icon": "⭐", "label": "Reviews", "active": active_tab == "reviews"},
        {"id": "nav-forecasting", "icon": "🔮", "label": "Forecasting", "active": active_tab == "forecasting"},
        {"id": "nav-upload", "icon": "📤", "label": "Upload", "active": active_tab == "upload"}
    ]
    
    # Theme buttons data
    theme_buttons = [
        {"id": "theme-dark", "icon": "🌙", "theme": "dark", "title": "Dark Mode"},
        {"id": "theme-light", "icon": "☀️", "theme": "light", "title": "Light Mode"},
        {"id": "theme-high_contrast", "icon": "🔳", "theme": "high_contrast", "title": "High Contrast"},
        {"id": "theme-swaccha_green", "icon": "🌿", "theme": "swaccha_green", "title": "Swaccha Green"}
    ]
    
    return html.Div(
        className="navigation-header",
        children=[
            html.Div(
                className="nav-content",
                children=[
                    # Left Section - Navigation Buttons
                    html.Div(
                        className="nav-tabs",
                        children=[
                            html.A(
                                children=[
                                    html.Span(btn["icon"], style={"marginRight": "0.5rem"}),
                                    btn["label"]
                                ],
                                id=btn["id"],
                                className=f"nav-tab {'active' if btn['active'] else ''}",
                                href=f"/{btn['id'].replace('nav-', '')}",
                                **{"data-tab": btn["id"].replace("nav-", "")}
                            ) for btn in nav_buttons
                        ]
                    ),
                    
                    # Center Section - User Info & Avatar
                    html.Div(
                        className="user-info",
                        children=[
                            html.Img(
                                src=user_data.get("picture", "/assets/img/default-avatar.png"),
                                alt=f"{user_data.get('name', 'User')} Avatar",
                                className="user-avatar"
                            ),
                            html.Div(
                                className="user-details",
                                children=[
                                    html.Div(
                                        user_data.get("name", "Administrator"),
                                        className="user-name"
                                    ),
                                    html.Div(
                                        user_data.get("role", "Super Admin"),
                                        className="user-role"
                                    )
                                ]
                            )
                        ]
                    ),
                    
                    # Right Section - Theme Switcher & Logout
                    html.Div(
                        className="right-controls",
                        children=[
                            # Theme Switcher
                            html.Div(
                                className="theme-switcher",
                                children=[
                                    html.Button(
                                        btn["icon"],
                                        id=btn["id"],
                                        className=f"theme-btn {'active' if theme_name == btn['theme'] else ''}",
                                        title=btn["title"],
                                        **{"data-theme": btn["theme"]}
                                    ) for btn in theme_buttons
                                ]
                            ),
                            
                            # Logout Button
                            html.Button(
                                children=[
                                    html.Span("🚪", style={"marginRight": "0.5rem"}),
                                    "Logout"
                                ],
                                id="logout-btn",
                                className="logout-btn"
                            )
                        ]
                    )
                ]
            )
        ]
    )

def get_dashboard_route_callbacks():
    """
    Get callback functions for dashboard route navigation
    
    Returns:
        list: List of callback decorators and functions
    """
    from dash import callback, Input, Output, State
    from dash.exceptions import PreventUpdate
    import dash
    
    callbacks = []
    
    # Theme switching callback
    @callback(
        Output('current-theme', 'data'),
        [Input(f'theme-{theme}', 'n_clicks') for theme in ['dark', 'light', 'high_contrast', 'swaccha_green']],
        prevent_initial_call=True
    )
    def update_theme(*args):
        """Update theme based on button clicks"""
        ctx = dash.callback_context
        if not ctx.triggered:
            raise PreventUpdate
            
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        theme_map = {
            'theme-dark': 'dark',
            'theme-light': 'light',
            'theme-high_contrast': 'high_contrast', 
            'theme-swaccha_green': 'swaccha_green'
        }
        
        return theme_map.get(button_id, DEFAULT_THEME)
    
    callbacks.append(update_theme)
    
    # Navigation callback
    @callback(
        Output('url', 'pathname'),
        [Input(f'nav-{page}', 'n_clicks') for page in ['dashboard', 'analytics', 'charts', 'reports', 'reviews', 'forecasting', 'upload']],
        prevent_initial_call=True
    )
    def handle_navigation(*args):
        """Handle navigation between pages"""
        ctx = dash.callback_context
        if not ctx.triggered:
            raise PreventUpdate
            
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        page = button_id.replace('nav-', '')
        return f'/{page}'
    
    callbacks.append(handle_navigation)
    
    # Logout callback  
    @callback(
        Output('user-authenticated', 'data'),
        Input('logout-btn', 'n_clicks'),
        prevent_initial_call=True
    )
    def handle_logout(n_clicks):
        """Handle user logout"""
        if n_clicks:
            return False
        raise PreventUpdate
    
    callbacks.append(handle_logout)
    
    return callbacks

def inject_dashboard_css():
    """
    Inject dashboard route CSS into the app
    
    Returns:
        str: CSS content for dashboard route
    """
    css_file_path = "assets/dashboard_route.css"
    
    # CSS is automatically loaded by Dash from assets folder
    # This function can be used to dynamically inject CSS if needed
    return f"""
    <link rel="stylesheet" href="/{css_file_path}">
    """

# Example usage in your dashboard layout
def create_enhanced_dashboard_layout(theme_name="dark", user_data=None, active_tab="dashboard"):
    """
    Create enhanced dashboard layout with aligned navigation
    
    Args:
        theme_name (str): Current theme name
        user_data (dict): User information
        active_tab (str): Currently active tab
        
    Returns:
        html.Div: Complete dashboard layout
    """
    from dash import html
    
    wrapper_props = get_dashboard_html_wrapper(theme_name)
    
    return html.Div(
        **wrapper_props,
        children=[
            # Aligned Navigation Header
            create_aligned_navigation_header(theme_name, user_data, active_tab),
            
            # Main Content Area
            html.Div(
                id="dashboard-content",
                style={
                    "flex": "1",
                    "padding": "2rem",
                    "backgroundColor": THEMES[theme_name]["primary_bg"]
                },
                children=[
                    # Your dashboard content goes here
                    html.H1("Dashboard Content", style={"color": THEMES[theme_name]["text_primary"]}),
                    html.P("Your dashboard components will be rendered here.", 
                           style={"color": THEMES[theme_name]["text_secondary"]})
                ]
            )
        ]
    )

# CSS Integration with existing theme system
def get_theme_css_variables(theme_name):
    """
    Generate CSS variables for the current theme
    
    Args:
        theme_name (str): Current theme name
        
    Returns:
        str: CSS variables string
    """
    theme = THEMES.get(theme_name, THEMES[DEFAULT_THEME])
    
    css_vars = f"""
    [data-theme="{theme_name}"] {{
        --primary-bg: {theme['primary_bg']};
        --secondary-bg: {theme['secondary_bg']};
        --accent-bg: {theme['accent_bg']};
        --card-bg: {theme['card_bg']};
        --text-primary: {theme['text_primary']};
        --text-secondary: {theme['text_secondary']};
        --border-light: {theme['border_light']};
        --border-medium: {theme['border_medium']};
        --brand-primary: {theme['brand_primary']};
        --success: {theme['success']};
        --warning: {theme['warning']};
        --error: {theme['error']};
        --info: {theme['info']};
    }}
    """
    
    return css_vars