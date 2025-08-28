# main.py
"""
Enhanced Main Application with Conditional Header System
Header shows everywhere except public landing page
"""

import dash
from dash import html, dcc, callback, Input, Output
from config.themes import THEMES, DEFAULT_THEME
from utils.theme_utils import get_hover_overlay_css
from layouts.public_layout import build_public_layout
from header import render_header

# Initialize Dash app
app = dash.Dash(
    __name__, 
    suppress_callback_exceptions=True, 
    title="स्वच्छ आंध्र प्रदेश - Swaccha Andhra Dashboard",
    external_stylesheets=[
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap"
    ],
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0, user-scalable=no, maximum-scale=1.0"},
        {"name": "theme-color", "content": "#0D1B2A"},
        {"name": "apple-mobile-web-app-capable", "content": "yes"},
        {"name": "apple-mobile-web-app-status-bar-style", "content": "black-translucent"},
        {"name": "apple-mobile-web-app-title", "content": "Swaccha Andhra"},
        {"name": "description", "content": "स्वच्छ आंध्र प्रदेश - Real-time cleanliness monitoring dashboard for Andhra Pradesh"}
    ]
)

server = app.server

# Enhanced PWA configuration
app.index_string = f'''
<!DOCTYPE html>
<html lang="en">
    <head>
        {{%metas%}}
        <title>{{%title%}}</title>
        {{%favicon%}}
        {{%css%}}
        <link rel="manifest" href="/assets/manifest.json">
        <style>
            {get_hover_overlay_css()}
            
            /* Enhanced loading screen */
            .pwa-loading {{
                position: fixed; top: 0; left: 0; width: 100%; height: 100%;
                background: linear-gradient(135deg, #0D1B2A 0%, #1A1F2E 100%);
                display: flex; justify-content: center; align-items: center; 
                z-index: 9999; opacity: 1; transition: opacity 0.8s ease;
            }}
            .pwa-loading.hidden {{ opacity: 0; pointer-events: none; }}
            
            .loading-content {{
                text-align: center; color: white; animation: fadeInUp 0.8s ease;
            }}
            
            .loading-icon {{
                font-size: 4rem; margin-bottom: 1.5rem; 
                animation: bounce 2s infinite;
            }}
            
            .loading-title {{
                font-size: 2rem; font-weight: 900; margin-bottom: 0.5rem;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
            }}
            
            .loading-subtitle {{
                font-size: 1.2rem; margin-bottom: 2rem; color: #A0AEC0;
            }}
            
            .loading-progress {{
                width: 200px; height: 4px; background: #2D3748;
                border-radius: 2px; margin: 0 auto; overflow: hidden;
            }}
            
            .progress-bar {{
                height: 100%; background: linear-gradient(90deg, #3182CE, #38A169);
                border-radius: 2px; animation: loadProgress 2s ease-in-out;
            }}
            
            @keyframes fadeInUp {{
                from {{ opacity: 0; transform: translateY(30px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}
            
            @keyframes bounce {{
                0%, 20%, 50%, 80%, 100% {{ transform: translateY(0); }}
                40% {{ transform: translateY(-10px); }}
                60% {{ transform: translateY(-5px); }}
            }}
            
            @keyframes loadProgress {{
                from {{ width: 0%; }}
                to {{ width: 100%; }}
            }}
            
            /* Conditional header spacing */
            .layout-with-header .main-content {{
                padding-top: 1rem !important;
            }}
            
            .layout-without-header .main-content {{
                padding-top: 0.5rem !important;
            }}
        </style>
    </head>
    <body>
        <!-- Enhanced Loading Screen -->
        <div id="pwa-loading" class="pwa-loading">
            <div class="loading-content">
                <div class="loading-icon">🌱</div>
                <div class="loading-title">स्वच्छ आंध्र प्रदेश</div>
                <div class="loading-subtitle">Loading Dashboard...</div>
                <div class="loading-progress">
                    <div class="progress-bar"></div>
                </div>
            </div>
        </div>
        
        {{%app_entry%}}
        {{%config%}}
        {{%scripts%}}
        {{%renderer%}}
        
        <script>
            // Enhanced loading sequence
            window.addEventListener('load', function() {{
                setTimeout(() => {{
                    document.getElementById('pwa-loading').classList.add('hidden');
                }}, 1500);
            }});
            
            // Service Worker Registration
            if ('serviceWorker' in navigator) {{
                window.addEventListener('load', () => {{
                    navigator.serviceWorker.register('/assets/sw.js')
                        .then((registration) => {{
                            console.log('SW registered: ', registration);
                        }})
                        .catch((registrationError) => {{
                            console.log('SW registration failed: ', registrationError);
                        }});
                }});
            }}
        </script>
    </body>
</html>
'''

# App layout with page routing
app.layout = html.Div(
    id="app-container",
    children=[
        dcc.Store(id='current-theme', data=DEFAULT_THEME),
        dcc.Store(id='user-authenticated', data=False),
        dcc.Store(id='current-page', data='public_landing'),  # Track current page
        dcc.Location(id='url', refresh=False),
        html.Div(id="main-layout")
    ]
)

# Page routing callback
@callback(
    Output('current-page', 'data'),
    [Input('url', 'pathname')]
)
def update_current_page(pathname):
    """Determine current page based on URL"""
    if pathname is None or pathname == '/' or pathname == '':
        return 'public_landing'
    elif pathname == '/admin':
        return 'admin_dashboard' 
    elif pathname == '/analytics':
        return 'analytics_page'
    elif pathname == '/reports':
        return 'reports_page'
    else:
        return 'public_landing'  # Default fallback

# Theme switching callback
@callback(
    Output('current-theme', 'data'),
    [
        Input('theme-dark', 'n_clicks'),
        Input('theme-light', 'n_clicks'),
        Input('theme-high_contrast', 'n_clicks'),
        Input('theme-swaccha_green', 'n_clicks')
    ],
    prevent_initial_call=True
)
def update_theme(dark_clicks, light_clicks, contrast_clicks, green_clicks):
    """Handle theme switching from overlay banner"""
    ctx = dash.callback_context
    
    if not ctx.triggered:
        return DEFAULT_THEME
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    theme_map = {
        'theme-dark': 'dark',
        'theme-light': 'light', 
        'theme-high_contrast': 'high_contrast',
        'theme-swaccha_green': 'swaccha_green'
    }
    
    new_theme = theme_map.get(button_id, DEFAULT_THEME)
    return new_theme

# Main layout callback with conditional header
@callback(
    Output('main-layout', 'children'),
    [
        Input('current-theme', 'data'),
        Input('user-authenticated', 'data'),
        Input('current-page', 'data')
    ]
)
def update_main_layout(theme_name, is_authenticated, current_page):
    """
    Update main layout with conditional header based on current page
    
    Args:
        theme_name (str): Current theme
        is_authenticated (bool): User authentication status
        current_page (str): Current page identifier
        
    Returns:
        html.Div: Appropriate layout with or without header
    """
    # Determine if header should be shown
    show_header = current_page != 'public_landing'
    
    # Build layout based on page
    if current_page == 'public_landing':
        # Public landing - no header, just hover overlay
        layout_content = build_public_layout(theme_name)
        layout_class = "layout-without-header"
    
    elif current_page == 'admin_dashboard':
        # Admin dashboard - with header
        layout_content = build_admin_layout(theme_name, is_authenticated)
        layout_class = "layout-with-header"
    
    elif current_page == 'analytics_page':
        # Analytics page - with header
        layout_content = build_analytics_layout(theme_name)
        layout_class = "layout-with-header"
    
    elif current_page == 'reports_page':
        # Reports page - with header
        layout_content = build_reports_layout(theme_name)
        layout_class = "layout-with-header"
    
    else:
        # Default to public landing
        layout_content = build_public_layout(theme_name)
        layout_class = "layout-without-header"
    
    # Return layout with conditional header
    return html.Div(
        className=f"app-layout {layout_class}",
        children=[
            # Conditional header
            render_header() if show_header else None,
            # Main content
            layout_content
        ]
    )

# Navigation callbacks - enhanced with page routing
@callback(
    [Output('user-authenticated', 'data'),
     Output('url', 'pathname')],
    [
        Input('admin-login-btn', 'n_clicks'),
        Input('nav-overview', 'n_clicks'),
        Input('nav-analytics', 'n_clicks'),
        Input('nav-reports', 'n_clicks')
    ],
    prevent_initial_call=True
)
def handle_navigation(login_clicks, overview_clicks, analytics_clicks, reports_clicks):
    """
    Handle navigation and authentication with page routing
    """
    ctx = dash.callback_context
    
    if not ctx.triggered:
        return False, '/'
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id == 'admin-login-btn':
        # Navigate to admin page (with authentication in future)
        return True, '/admin'  # For now, just navigate
    
    elif button_id == 'nav-overview':
        # Navigate to overview (public landing)
        return False, '/'
    
    elif button_id == 'nav-analytics':
        # Navigate to analytics page
        return False, '/analytics'
    
    elif button_id == 'nav-reports':
        # Navigate to reports page
        return False, '/reports'
    
    return False, '/'

# Placeholder layout functions (implement these based on your needs)
def build_admin_layout(theme_name, is_authenticated):
    """Build admin dashboard layout (placeholder)"""
    from utils.theme_utils import get_theme_styles
    from components.navigation.hover_overlay import create_hover_overlay_banner
    
    theme_styles = get_theme_styles(theme_name)
    
    return html.Div(
        style=theme_styles["container_style"],
        children=[
            create_hover_overlay_banner(theme_name),
            html.Div(
                style=theme_styles["main_content_style"],
                children=[
                    html.H1("🔐 Admin Dashboard", 
                           style={"color": theme_styles["theme"]["text_primary"]}),
                    html.P("Admin functionality coming soon...",
                           style={"color": theme_styles["theme"]["text_secondary"]})
                ]
            )
        ]
    )

def build_analytics_layout(theme_name):
    """Build analytics page layout (placeholder)"""
    from utils.theme_utils import get_theme_styles
    from components.navigation.hover_overlay import create_hover_overlay_banner
    
    theme_styles = get_theme_styles(theme_name)
    
    return html.Div(
        style=theme_styles["container_style"],
        children=[
            create_hover_overlay_banner(theme_name),
            html.Div(
                style=theme_styles["main_content_style"],
                children=[
                    html.H1("📈 Analytics Dashboard", 
                           style={"color": theme_styles["theme"]["text_primary"]}),
                    html.P("Advanced analytics coming soon...",
                           style={"color": theme_styles["theme"]["text_secondary"]})
                ]
            )
        ]
    )

def build_reports_layout(theme_name):
    """Build reports page layout (placeholder)"""
    from utils.theme_utils import get_theme_styles
    from components.navigation.hover_overlay import create_hover_overlay_banner
    
    theme_styles = get_theme_styles(theme_name)
    
    return html.Div(
        style=theme_styles["container_style"],
        children=[
            create_hover_overlay_banner(theme_name),
            html.Div(
                style=theme_styles["main_content_style"],
                children=[
                    html.H1("📋 Reports Dashboard", 
                           style={"color": theme_styles["theme"]["text_primary"]}),
                    html.P("Detailed reports coming soon...",
                           style={"color": theme_styles["theme"]["text_secondary"]})
                ]
            )
        ]
    )

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8050)

# Export for testing and deployment
__all__ = ['app', 'server']