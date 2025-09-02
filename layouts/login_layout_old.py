# layouts/login_layout.py - UPDATED VERSION
"""
Login Page Layout with Traditional Username/Password Form
"""

from dash import html, dcc
from utils.theme_utils import get_theme_styles
from components.navigation.hover_overlay import create_hover_overlay_banner

def create_username_password_form(theme):
    """Create traditional username/password login form"""
    return html.Div(
        className="username-password-form",
        style={
            "maxWidth": "400px",
            "margin": "2rem auto",
            "backgroundColor": theme["card_bg"],
            "borderRadius": "16px",
            "border": f"2px solid {theme['accent_bg']}",
            "boxShadow": "0 12px 40px rgba(0, 0, 0, 0.3)",
            "padding": "2.5rem",
            "textAlign": "center"
        },
        children=[
            # Form header
            html.Div([
                html.H2(
                    "Administrator Login",
                    style={
                        "color": theme["text_primary"],
                        "fontSize": "1.8rem",
                        "fontWeight": "700",
                        "marginBottom": "0.5rem"
                    }
                ),
                html.P(
                    "Enter your credentials to access the dashboard",
                    style={
                        "color": theme["text_secondary"],
                        "fontSize": "1rem",
                        "marginBottom": "2rem"
                    }
                )
            ]),
            
            # Username field
            html.Div([
                html.Label(
                    "Username",
                    style={
                        "color": theme["text_primary"],
                        "fontSize": "0.9rem",
                        "fontWeight": "600",
                        "display": "block",
                        "textAlign": "left",
                        "marginBottom": "0.5rem"
                    }
                ),
                dcc.Input(
                    id="username-input",
                    type="text",
                    placeholder="Enter your username",
                    style={
                        "width": "100%",
                        "padding": "12px 16px",
                        "backgroundColor": theme["accent_bg"],
                        "border": f"2px solid {theme['border_light']}",
                        "borderRadius": "8px",
                        "color": theme["text_primary"],
                        "fontSize": "1rem",
                        "marginBottom": "1.5rem",
                        "outline": "none",
                        "boxSizing": "border-box"
                    }
                )
            ], style={"textAlign": "left"}),
            
            # Password field
            html.Div([
                html.Label(
                    "Password",
                    style={
                        "color": theme["text_primary"],
                        "fontSize": "0.9rem",
                        "fontWeight": "600",
                        "display": "block",
                        "textAlign": "left",
                        "marginBottom": "0.5rem"
                    }
                ),
                dcc.Input(
                    id="password-input",
                    type="password",
                    placeholder="Enter your password",
                    style={
                        "width": "100%",
                        "padding": "12px 16px",
                        "backgroundColor": theme["accent_bg"],
                        "border": f"2px solid {theme['border_light']}",
                        "borderRadius": "8px",
                        "color": theme["text_primary"],
                        "fontSize": "1rem",
                        "marginBottom": "1.5rem",
                        "outline": "none",
                        "boxSizing": "border-box"
                    }
                )
            ], style={"textAlign": "left"}),
            
            # Login button
            html.Button(
                "Login",
                id="username-password-login-btn",
                style={
                    "width": "100%",
                    "padding": "12px 24px",
                    "backgroundColor": theme["brand_primary"],
                    "color": "white",
                    "border": "none",
                    "borderRadius": "8px",
                    "fontSize": "1rem",
                    "fontWeight": "600",
                    "cursor": "pointer",
                    "transition": "all 0.2s ease",
                    "marginBottom": "1rem"
                }
            ),
            
            # Alternative login divider
            html.Div([
                html.Div(
                    style={
                        "height": "1px",
                        "backgroundColor": theme["border_light"],
                        "flex": "1"
                    }
                ),
                html.Span(
                    "OR",
                    style={
                        "color": theme["text_secondary"],
                        "fontSize": "0.9rem",
                        "padding": "0 1rem",
                        "backgroundColor": theme["card_bg"]
                    }
                ),
                html.Div(
                    style={
                        "height": "1px",
                        "backgroundColor": theme["border_light"],
                        "flex": "1"
                    }
                )
            ], style={
                "display": "flex",
                "alignItems": "center",
                "margin": "1.5rem 0"
            }),
            
            # Demo login buttons (keep existing ones)
            html.Div([
                html.Button(
                    "Demo Login",
                    id="demo-login-btn",
                    style={
                        "padding": "8px 16px",
                        "backgroundColor": theme["success"],
                        "color": "white",
                        "border": "none",
                        "borderRadius": "6px",
                        "fontSize": "0.9rem",
                        "cursor": "pointer",
                        "margin": "0.25rem"
                    }
                ),
                html.Button(
                    "Admin",
                    id="admin-account-btn", 
                    style={
                        "padding": "8px 16px",
                        "backgroundColor": theme["info"],
                        "color": "white",
                        "border": "none",
                        "borderRadius": "6px",
                        "fontSize": "0.9rem",
                        "cursor": "pointer",
                        "margin": "0.25rem"
                    }
                )
            ], style={"marginTop": "1rem"}),
            
            # Help text
            html.P(
                "Default credentials: admin / password",
                style={
                    "color": theme["text_secondary"],
                    "fontSize": "0.8rem",
                    "marginTop": "1.5rem",
                    "fontStyle": "italic"
                }
            )
        ]
    )

def build_login_layout(theme_name="dark", error_message=""):
    """Build the complete login page layout with username/password form"""
    theme_styles = get_theme_styles(theme_name)
    theme = theme_styles["theme"]
    
    # Determine error display
    show_error = bool(error_message)
    
    return html.Div(
        className="login-layout",
        style=theme_styles["container_style"],
        children=[
            # Hover overlay for theme switching
            create_hover_overlay_banner(theme_name),
            
            # Main login content
            html.Div(
                className="login-content",
                style={
                    **theme_styles["main_content_style"],
                    "maxWidth": "800px",
                    "margin": "0 auto",
                    "paddingTop": "2rem"
                },
                children=[
                    # Back to public button
                    html.Div(
                        style={
                            "textAlign": "left",
                            "marginBottom": "2rem"
                        },
                        children=[
                            html.Button(
                                [html.Span("← "), "Back to Public Dashboard"],
                                id="back-to-public-btn",
                                style={
                                    "backgroundColor": "transparent",
                                    "border": f"2px solid {theme['border_light']}",
                                    "color": theme["text_secondary"],
                                    "padding": "0.5rem 1rem",
                                    "borderRadius": "8px",
                                    "cursor": "pointer",
                                    "fontSize": "0.9rem",
                                    "transition": "all 0.2s ease"
                                }
                            )
                        ]
                    ),
                    
                    # Error message card (conditionally displayed)
                    html.Div(
                        id="auth-status-card",
                        style={
                            "maxWidth": "400px",
                            "margin": "1rem auto",
                            "backgroundColor": theme["card_bg"],
                            "border": f"2px solid {theme['error']}",
                            "borderRadius": "12px",
                            "padding": "1.5rem",
                            "textAlign": "center",
                            "display": "block" if show_error else "none"
                        },
                        children=[
                            html.Div("❌", style={"fontSize": "2rem", "marginBottom": "1rem"}),
                            html.H3(
                                "Authentication Error",
                                style={
                                    "color": theme["error"],
                                    "fontSize": "1.2rem",
                                    "fontWeight": "700",
                                    "marginBottom": "0.5rem"
                                }
                            ),
                            html.P(
                                error_message or "",
                                style={
                                    "color": theme["text_secondary"],
                                    "fontSize": "1rem",
                                    "lineHeight": "1.5",
                                    "margin": "0"
                                }
                            )
                        ]
                    ) if show_error else html.Div(),
                    
                    # Username/Password form
                    create_username_password_form(theme)
                ]
            )
        ]
    )