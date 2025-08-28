# components/navigation/hover_overlay.py
"""
Hover Overlay Navigation Component
Creates the hoverable banner for admin access
"""

from dash import html
from config.themes import THEMES
from components.navigation.theme_switcher import create_theme_switcher

def create_hover_trigger():
    """Create invisible hover trigger area at top of screen"""
    return html.Div(
        id="hover-trigger-area",
        style={
            "position": "fixed",
            "top": "0",
            "left": "0", 
            "right": "0",
            "height": "30px",
            "zIndex": "10002",
            "backgroundColor": "transparent",
            "cursor": "pointer"
        }
    )

def create_admin_login_button(theme):
    """Create admin login button"""
    return html.Button(
        [html.Span("🔐", style={"marginRight": "0.5rem"}), "User Login"],
        id="admin-login-btn",
        style={
            "background": f"linear-gradient(135deg, {theme['success']} 0%, {theme['info']} 100%)",
            "border": "none",
            "color": "white",
            "fontSize": "1rem",
            "fontWeight": "700",
            "padding": "0.8rem 1.5rem",
            "borderRadius": "10px",
            "cursor": "pointer",
            "transition": "all 0.2s ease",
            "boxShadow": "0 4px 16px rgba(0, 0, 0, 0.3)",
            "textTransform": "uppercase",
            "letterSpacing": "0.5px"
        }
    )

def create_divider(theme):
    """Create visual divider"""
    return html.Div(
        style={
            "width": "2px",
            "height": "50px",
            "backgroundColor": theme["border_light"],
            "margin": "0 1rem"
        }
    )

def create_dynamic_auth_button(theme, is_authenticated=False, user_data=None):
    """Create dynamic authentication button (login or logout)"""
    if is_authenticated and user_data:
        # Show logout button with user info
        return html.Div(
            style={
                "display": "flex",
                "alignItems": "center",
                "gap": "1rem"
            },
            children=[
                # User info section
                html.Div(
                    style={
                        "display": "flex",
                        "alignItems": "center",
                        "gap": "0.75rem",
                        "padding": "0.5rem 1rem",
                        "backgroundColor": theme["accent_bg"],
                        "borderRadius": "8px",
                        "border": f"2px solid {theme['brand_primary']}"
                    },
                    children=[
                        # User avatar
                        html.Img(
                            src=user_data.get('picture', '/assets/img/default-avatar.png'),
                            alt=f"{user_data.get('name', 'User')} Avatar",
                            style={
                                "width": "28px",
                                "height": "28px",
                                "borderRadius": "50%",
                                "border": f"2px solid {theme['brand_primary']}",
                                "objectFit": "cover"
                            }
                        ),
                        # User name
                        html.Div([
                            html.Div(
                                user_data.get('name', 'User'),
                                style={
                                    "fontSize": "0.85rem",
                                    "fontWeight": "600",
                                    "color": theme["text_primary"],
                                    "lineHeight": "1.2",
                                    "whiteSpace": "nowrap"
                                }
                            ),
                            html.Div(
                                user_data.get('role', 'user').replace('_', ' ').title(),
                                style={
                                    "fontSize": "0.7rem",
                                    "color": theme["text_secondary"],
                                    "lineHeight": "1.2"
                                }
                            )
                        ])
                    ]
                ),
                
                # Logout button
                html.Button(
                    [html.Span("🚪", style={"marginRight": "0.5rem"}), "Logout"],
                    id="overlay-logout-btn",
                    style={
                        "background": f"linear-gradient(135deg, {theme['error']} 0%, #C53030 100%)",
                        "border": "none",
                        "color": "white",
                        "fontSize": "0.95rem",
                        "fontWeight": "700",
                        "padding": "0.8rem 1.5rem",
                        "borderRadius": "10px",
                        "cursor": "pointer",
                        "transition": "all 0.2s ease",
                        "boxShadow": "0 4px 16px rgba(0, 0, 0, 0.3)",
                        "textTransform": "uppercase",
                        "letterSpacing": "0.5px"
                    }
                )
            ]
        )
    else:
        # Show login button
        return html.Button(
            [html.Span("🔐", style={"marginRight": "0.5rem"}), "User Login"],
            id="admin-login-btn",
            style={
                "background": f"linear-gradient(135deg, {theme['success']} 0%, {theme['info']} 100%)",
                "border": "none",
                "color": "white",
                "fontSize": "1rem",
                "fontWeight": "700",
                "padding": "0.8rem 1.5rem",
                "borderRadius": "10px",
                "cursor": "pointer",
                "transition": "all 0.2s ease",
                "boxShadow": "0 4px 16px rgba(0, 0, 0, 0.3)",
                "textTransform": "uppercase",
                "letterSpacing": "0.5px"
            }
        )

def create_hover_overlay_banner(current_theme="dark", is_authenticated=False, user_data=None):
    """
    Create complete hover overlay banner with dynamic login/logout
    """
    theme = THEMES[current_theme]
    
    return html.Div([
        # Invisible hover trigger area
        create_hover_trigger(),
        
        # The actual overlay banner
        html.Div(
            id="overlay-banner",
            className="overlay-banner",
            style={
                "position": "fixed",
                "top": "0",
                "left": "0",
                "right": "0",
                "zIndex": "10001",
                "backgroundColor": f"{theme['secondary_bg']}ee",
                "backdropFilter": "blur(10px)",
                "border": f"3px solid {theme['brand_primary']}",
                "borderTop": "none",
                "borderRadius": "0 0 12px 12px",
                "boxShadow": "0 8px 32px rgba(0, 0, 0, 0.5)",
                "transform": "translateY(-100%)",
                "transition": "transform 0.4s cubic-bezier(0.4, 0, 0.2, 1)",
                "padding": "1rem 2rem 1.5rem 2rem",
                "display": "flex",
                "justifyContent": "space-between",
                "alignItems": "center",
                "opacity": "0",
                "pointerEvents": "none"
            },
            children=[
                # Left - App name
                html.Div(
                    style={
                        "display": "flex",
                        "alignItems": "center",
                        "gap": "1rem"
                    },
                    children=[
                        html.Div([
                            html.Span("Built by Advitia Labs", style={
                                "fontSize": "1.1rem", 
                                "fontWeight": "700",
                                "color": theme["text_primary"]
                            })
                        ], style={"display": "flex", "alignItems": "center"})
                    ]
                ),
                
                # Center - Theme switcher
                create_theme_switcher(current_theme),
                
                # Right - Dynamic auth button
                html.Div(
                    style={
                        "display": "flex",
                        "gap": "1rem",
                        "alignItems": "center"
                    },
                    children=[
                        create_divider(theme),
                        create_dynamic_auth_button(theme, is_authenticated, user_data)
                    ]
                )
            ]
        )
    ])

def create_simple_hover_overlay_banner(current_theme="dark"):
    """
    Create simplified hover overlay banner with only theme switcher and login
    Alternative version without navigation buttons
    
    Args:
        current_theme (str): Currently active theme
        
    Returns:
        html.Div: Simplified hover overlay component
    """
    theme = THEMES[current_theme]
    
    return html.Div([
        # Invisible hover trigger area
        create_hover_trigger(),
        
        # The actual overlay banner - simplified
        html.Div(
            id="overlay-banner",
            className="overlay-banner",
            style={
                "position": "fixed",
                "top": "0",
                "left": "0",
                "right": "0",
                "zIndex": "10001",
                "backgroundColor": f"{theme['secondary_bg']}ee",  # Semi-transparent
                "backdropFilter": "blur(10px)",
                "border": f"3px solid {theme['brand_primary']}",
                "borderTop": "none",
                "borderRadius": "0 0 12px 12px",
                "boxShadow": "0 8px 32px rgba(0, 0, 0, 0.5)",
                "transform": "translateY(-100%)",
                "transition": "transform 0.4s cubic-bezier(0.4, 0, 0.2, 1)",
                "padding": "1rem 2rem 1.5rem 2rem",
                "display": "flex",
                "justifyContent": "center",  # Center the content
                "alignItems": "center",
                "opacity": "0",
                "pointerEvents": "none"
            },
            children=[
                # Centered content - Only theme switcher and login
                html.Div(
                    style={
                        "display": "flex",
                        "gap": "1rem",
                        "alignItems": "center",
                        "justifyContent": "center"
                    },
                    children=[
                        create_theme_switcher(current_theme),
                        create_divider(theme),
                        create_admin_login_button(theme)
                    ]
                )
            ]
        )
    ])

def create_compact_hover_overlay(current_theme="dark"):
    """
    Create a more compact version of the hover overlay
    Useful for smaller screens or simpler layouts
    """
    theme = THEMES[current_theme]
    
    return html.Div([
        create_hover_trigger(),
        html.Div(
            id="compact-overlay-banner",
            style={
                "position": "fixed",
                "top": "0",
                "left": "0",
                "right": "0",
                "zIndex": "10001",
                "backgroundColor": f"{theme['secondary_bg']}dd",
                "border": f"2px solid {theme['brand_primary']}",
                "borderTop": "none",
                "transform": "translateY(-100%)",
                "transition": "transform 0.3s ease",
                "padding": "1rem",
                "display": "flex",
                "justifyContent": "center",
                "alignItems": "center",
                "gap": "1rem",
                "opacity": "0",
                "pointerEvents": "none"
            },
            children=[
                create_theme_switcher(current_theme),
                create_admin_login_button(theme)
            ]
        )
    ])