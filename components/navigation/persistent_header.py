# components/navigation/persistent_header.py
"""
Persistent Navigation Header Component
Stays consistent across all authenticated pages
"""

from dash import html, dcc
from flask import session
from utils.theme_utils import get_theme_styles

def create_persistent_navigation_header(theme_name="dark", active_page="dashboard"):
    """
    Create a persistent navigation header that stays across all pages
    
    Args:
        theme_name (str): Current theme
        active_page (str): Currently active page for highlighting
        
    Returns:
        html.Header: Persistent navigation header
    """
    theme_styles = get_theme_styles(theme_name)
    theme = theme_styles["theme"]
    
    # Get user info from session
    user_info = session.get('user_data', {})
    user_name = user_info.get('name', 'Administrator')
    user_role = user_info.get('role', 'administrator').replace('_', ' ').title()
    user_avatar = user_info.get('picture', '/assets/img/default-avatar.png')
    
    # Get user role for access control
    user_role_raw = user_info.get('role', 'viewer')
    
    # Define all possible navigation items
    nav_items = [
        {"id": "dashboard", "href": "/dashboard", "icon": "📊", "label": "Dashboard", "access": ["viewer", "administrator", "super_admin"]},
        {"id": "upload", "href": "/upload", "icon": "📤", "label": "Upload", "access": ["administrator", "super_admin"]},
        {"id": "analytics", "href": "/data-analytics", "icon": "📈", "label": "Analytics", "access": ["viewer", "administrator", "super_admin"]},
        {"id": "reports", "href": "/reports", "icon": "📋", "label": "Reports", "access": ["viewer", "administrator", "super_admin"]},
        {"id": "reviews", "href": "/reviews", "icon": "⭐", "label": "Reviews", "access": ["administrator", "super_admin"]},
        {"id": "forecasting", "href": "/forecasting", "icon": "🔮", "label": "Forecasting", "access": ["super_admin"]},
    ]
    
    # Filter nav items based on user access
    visible_items = [item for item in nav_items if user_role_raw in item["access"]]
    
    # Theme switching options
    theme_options = [
        {"value": "dark", "label": "🌙 Dark", "icon": "🌙"},
        {"value": "light", "label": "☀️ Light", "icon": "☀️"},
        {"value": "high_contrast", "label": "🔳 High Contrast", "icon": "🔳"},
        {"value": "swaccha_green", "label": "🌿 Swaccha Green", "icon": "🌿"},
    ]
    
    return html.Header(
        id="persistent-navigation-header",
        style={
            "background": f"linear-gradient(135deg, {theme['secondary_bg']} 0%, {theme['accent_bg']} 100%)",
            "borderBottom": f"3px solid {theme['brand_primary']}",
            "padding": "0.75rem 2rem",
            "boxShadow": "0 4px 16px rgba(0, 0, 0, 0.3)",
            "position": "sticky",
            "top": "0",
            "zIndex": "1000",
            "backdropFilter": "blur(10px)",
        },
        children=[
            html.Div(
                style={
                    "maxWidth": "1600px",
                    "margin": "0 auto",
                    "display": "flex",
                    "justifyContent": "space-between",
                    "alignItems": "center",
                    "gap": "2rem",
                    "flexWrap": "wrap",
                },
                children=[
                    # Left section: Logo + Nav Items
                    html.Div(
                        style={
                            "display": "flex",
                            "alignItems": "center",
                            "gap": "2rem",
                            "flex": "1",
                        },
                        children=[
                            # Logo/Brand
                            html.Div(
                                style={
                                    "display": "flex",
                                    "alignItems": "center",
                                    "gap": "0.5rem",
                                    "fontSize": "1.2rem",
                                    "fontWeight": "800",
                                    "color": theme["text_primary"],
                                },
                                children=[
                                    html.Span("🏢"),
                                    html.Span("Swaccha Andhra"),
                                ]
                            ),
                            
                            # Navigation Items
                            html.Nav(
                                style={
                                    "display": "flex",
                                    "gap": "0.5rem",
                                    "alignItems": "center",
                                    "flexWrap": "wrap",
                                },
                                children=[
                                    html.A(
                                        href=item["href"],
                                        style={
                                            "padding": "0.6rem 1.2rem",
                                            "borderRadius": "8px",
                                            "textDecoration": "none",
                                            "fontWeight": "600",
                                            "fontSize": "0.9rem",
                                            "transition": "all 0.3s ease",
                                            "display": "flex",
                                            "alignItems": "center",
                                            "gap": "0.4rem",
                                            "border": f"2px solid {'transparent' if item['id'] != active_page else theme['brand_primary']}",
                                            "background": theme["brand_primary"] if item["id"] == active_page else "rgba(255, 255, 255, 0.1)",
                                            "color": "white" if item["id"] == active_page else theme["text_primary"],
                                            "boxShadow": f"0 4px 12px rgba(0, 0, 0, 0.2)" if item["id"] == active_page else "none",
                                        },
                                        children=[
                                            html.Span(item["icon"]),
                                            html.Span(item["label"]),
                                        ],
                                        className="nav-link",
                                        **{"data-page": item["id"]}
                                    )
                                    for item in visible_items
                                ]
                            ),
                        ]
                    ),
                    
                    # Right section: Theme Switcher + User Info
                    html.Div(
                        style={
                            "display": "flex",
                            "alignItems": "center",
                            "gap": "1rem",
                        },
                        children=[
                            # Theme Switcher
                            html.Div(
                                style={
                                    "display": "flex",
                                    "gap": "0.25rem",
                                    "padding": "0.25rem",
                                    "background": "rgba(255, 255, 255, 0.1)",
                                    "borderRadius": "8px",
                                },
                                children=[
                                    html.Button(
                                        option["icon"],
                                        id=f"theme-{option['value']}",
                                        style={
                                            "width": "32px",
                                            "height": "32px",
                                            "border": "none",
                                            "borderRadius": "6px",
                                            "cursor": "pointer",
                                            "fontSize": "0.9rem",
                                            "transition": "all 0.2s ease",
                                            "background": theme["brand_primary"] if option["value"] == theme_name else "transparent",
                                            "color": "white" if option["value"] == theme_name else theme["text_secondary"],
                                        },
                                        title=option["label"],
                                        className="theme-btn"
                                    )
                                    for option in theme_options
                                ]
                            ),
                            
                            # User Info
                            html.Div(
                                style={
                                    "display": "flex",
                                    "alignItems": "center",
                                    "gap": "0.75rem",
                                    "padding": "0.5rem 1rem",
                                    "background": "rgba(255, 255, 255, 0.1)",
                                    "borderRadius": "25px",
                                    "backdropFilter": "blur(10px)",
                                },
                                children=[
                                    html.Img(
                                        src=user_avatar,
                                        style={
                                            "width": "32px",
                                            "height": "32px",
                                            "borderRadius": "50%",
                                            "border": f"2px solid {theme['brand_primary']}",
                                            "objectFit": "cover",
                                        },
                                        alt="User Avatar"
                                    ),
                                    html.Div(
                                        style={
                                            "display": "flex",
                                            "flexDirection": "column",
                                            "lineHeight": "1.2",
                                        },
                                        children=[
                                            html.Span(
                                                user_name,
                                                style={
                                                    "fontSize": "0.85rem",
                                                    "fontWeight": "600",
                                                    "color": theme["text_primary"],
                                                }
                                            ),
                                            html.Span(
                                                user_role,
                                                style={
                                                    "fontSize": "0.7rem",
                                                    "color": theme["text_secondary"],
                                                }
                                            ),
                                        ]
                                    ),
                                    # Logout Button
                                    html.A(
                                        "🚪",
                                        href="/?logout=true",
                                        style={
                                            "padding": "0.4rem 0.8rem",
                                            "background": "rgba(220, 38, 38, 0.8)",
                                            "color": "white",
                                            "textDecoration": "none",
                                            "borderRadius": "6px",
                                            "fontSize": "0.9rem",
                                            "transition": "all 0.3s ease",
                                        },
                                        title="Logout",
                                        className="logout-btn"
                                    ),
                                ]
                            ),
                        ]
                    ),
                ]
            )
        ]
    )

# layouts/base_layout.py
"""
Base Layout with Persistent Header
Use this as the foundation for all authenticated pages
"""

def create_base_authenticated_layout(content, theme_name="dark", active_page="dashboard"):
    """
    Create base layout with persistent header for authenticated pages
    
    Args:
        content: The main content for the page
        theme_name (str): Current theme
        active_page (str): Currently active page
        
    Returns:
        html.Div: Complete page layout with persistent header
    """
    theme_styles = get_theme_styles(theme_name)
    theme = theme_styles["theme"]
    
    return html.Div(
        style={
            "minHeight": "100vh",
            "backgroundColor": theme["primary_bg"],
            "color": theme["text_primary"],
            "fontFamily": "'Inter', sans-serif",
        },
        children=[
            # Persistent Navigation Header
            create_persistent_navigation_header(theme_name, active_page),
            
            # Main Content Area
            html.Main(
                style={
                    "flex": "1",
                    "padding": "2rem",
                    "maxWidth": "1600px",
                    "margin": "0 auto",
                    "width": "100%",
                },
                children=content
            ),
            
            # Optional Footer
            html.Footer(
                style={
                    "padding": "1rem 2rem",
                    "background": theme["secondary_bg"],
                    "borderTop": f"1px solid {theme.get('border_light', theme['accent_bg'])}",
                    "textAlign": "center",
                    "color": theme["text_secondary"],
                    "fontSize": "0.9rem",
                },
                children=[
                    html.P("© 2025 Swaccha Andhra Corporation. All rights reserved.")
                ]
            )
        ]
    )

# Now update your Flask routes to use this base layout:

# layouts/upload_layout.py - SIMPLIFIED VERSION
def create_upload_page_content(theme_name="dark"):
    """Create just the content for upload page (header will be added by base layout)"""
    theme_styles = get_theme_styles(theme_name)
    theme = theme_styles["theme"]
    
    # Just return the content, not the full HTML
    return [
        html.Div(
            style={
                "display": "flex",
                "justifyContent": "center",
                "alignItems": "center",
                "minHeight": "70vh",
                "padding": "2rem",
            },
            children=[
                html.Div(
                    style={
                        "textAlign": "center",
                        "maxWidth": "600px",
                        "padding": "3rem 2rem",
                        "background": theme["card_bg"],
                        "borderRadius": "20px",
                        "boxShadow": "0 20px 60px rgba(0, 0, 0, 0.3)",
                        "border": f"2px solid {theme['brand_primary']}",
                        "animation": "fadeInUp 0.8s ease-out",
                    },
                    children=[
                        html.Div(
                            "👋",
                            style={
                                "fontSize": "5rem",
                                "marginBottom": "1rem",
                                "animation": "wave 2.5s ease-in-out infinite",
                            }
                        ),
                        html.H1(
                            "Hi Sai!",
                            style={
                                "fontSize": "3.5rem",
                                "fontWeight": "900",
                                "color": theme["text_primary"],
                                "marginBottom": "1rem",
                                "background": f"linear-gradient(45deg, {theme['brand_primary']}, {theme.get('brand_primary', '#3182CE')})",
                                "WebkitBackgroundClip": "text",
                                "WebkitTextFillColor": "transparent",
                            }
                        ),
                        html.P(
                            "Welcome to your personalized upload center!",
                            style={
                                "fontSize": "1.3rem",
                                "color": theme["text_secondary"],
                                "marginBottom": "2rem",
                            }
                        ),
                        html.Div(
                            style={"display": "flex", "gap": "1rem", "justifyContent": "center"},
                            children=[
                                html.Button(
                                    "📁 Start Uploading",
                                    style={
                                        "padding": "1rem 2rem",
                                        "background": theme["brand_primary"],
                                        "color": "white",
                                        "border": "none",
                                        "borderRadius": "12px",
                                        "fontWeight": "600",
                                        "cursor": "pointer",
                                        "transition": "all 0.3s ease",
                                    }
                                )
                            ]
                        )
                    ]
                )
            ]
        )
    ]

# In your main Flask routes (layouts/admin_dashboard.py):

@server.route('/upload')
def admin_upload():
    """Upload Page with persistent header"""
    has_access, redirect_response = check_tab_access('upload')
    if not has_access:
        return redirect_response
    
    theme = get_current_theme()
    
    # Use the base layout with upload content
    from layouts.base_layout import create_base_authenticated_layout
    from layouts.upload_layout import create_upload_page_content
    
    layout = create_base_authenticated_layout(
        content=create_upload_page_content(theme),
        theme_name=theme,
        active_page="upload"
    )
    
    # Convert Dash layout to HTML
    return f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Upload - Swaccha Andhra Dashboard</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
        <style>
            @keyframes wave {{
                0%, 100% {{ transform: rotate(0deg); }}
                25% {{ transform: rotate(-15deg); }}
                75% {{ transform: rotate(15deg); }}
            }}
            @keyframes fadeInUp {{
                from {{ opacity: 0; transform: translateY(30px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}
            .nav-link:hover {{
                background: rgba(255, 255, 255, 0.2) !important;
                transform: translateY(-2px);
            }}
            .theme-btn:hover {{
                background: {theme_styles["theme"]["brand_primary"]} !important;
                color: white !important;
            }}
            .logout-btn:hover {{
                background: rgba(220, 38, 38, 1) !important;
                transform: translateY(-2px);
            }}
        </style>
    </head>
    <body>
        <!-- This will be rendered by your Dash components -->
        <!-- The layout structure will be consistent across all pages -->
        <div id="upload-page-root"></div>
    </body>
    </html>
    '''

# Apply this same pattern to all your other routes:
@server.route('/dashboard')
def admin_dashboard():
    # Dashboard content with persistent header
    pass

@server.route('/data-analytics') 
def admin_data_analytics():
    # Analytics content with persistent header
    pass

@server.route('/reports')
def admin_reports():
    # Reports content with persistent header
    pass

# Add CSS for smooth animations
PERSISTENT_HEADER_CSS = '''
<style>
.nav-link:hover {
    background: rgba(255, 255, 255, 0.2) !important;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.theme-btn:hover {
    transform: scale(1.1);
}

.logout-btn:hover {
    background: rgba(220, 38, 38, 1) !important;
    transform: translateY(-2px);
}

@media (max-width: 768px) {
    #persistent-navigation-header > div {
        flex-direction: column;
        gap: 1rem;
    }
    
    nav {
        justify-content: center;
        width: 100%;
    }
}
</style>
'''