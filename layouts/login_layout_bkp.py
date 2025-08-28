# layouts/login_layout.py
"""
Login Page Layout
Themed login interface with Google OAuth integration
"""

from dash import html, dcc
from utils.theme_utils import get_theme_styles
from components.navigation.hover_overlay import create_hover_overlay_banner


def create_login_form(theme):
    """Create the main login form"""
    return html.Div(
        className="login-form-container",
        style={
            "maxWidth": "400px",
            "margin": "0 auto",
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
                    "Choose your authentication method",
                    style={
                        "color": theme["text_secondary"],
                        "fontSize": "1rem",
                        "marginBottom": "2rem"
                    }
                )
            ]),
            
            # Google OAuth Button - Enhanced and more visible
            html.Button(
                [
                    # Google icon using Unicode
                    html.Span(
                        "🔵",  # Using blue circle as fallback
                        style={
                            "marginRight": "12px",
                            "fontSize": "1.2rem"
                        }
                    ),
                    html.Span("Continue with Google", style={"fontSize": "1rem", "fontWeight": "600"})
                ],
                id="google-login-btn",
                style={
                    "width": "100%",
                    "padding": "16px 24px",
                    "backgroundColor": "#4285f4",  # Google blue
                    "color": "white",
                    "border": "none",
                    "borderRadius": "8px",
                    "fontSize": "1rem",
                    "fontWeight": "600",
                    "cursor": "pointer",
                    "transition": "all 0.2s ease",
                    "display": "flex",
                    "alignItems": "center",
                    "justifyContent": "center",
                    "marginBottom": "1.5rem",
                    "boxShadow": "0 4px 12px rgba(66, 133, 244, 0.3)",
                    "position": "relative",
                    "overflow": "hidden"
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
                "marginBottom": "1.5rem"
            }),
            
            # Username/Password Login Section
            html.Div([
                # Username input
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
                            "border": f"2px solid {theme['border_light']}",
                            "borderRadius": "8px",
                            "fontSize": "1rem",
                            "backgroundColor": theme["card_bg"],
                            "color": theme["text_primary"],
                            "outline": "none",
                            "transition": "all 0.2s ease",
                            "marginBottom": "1rem"
                        }
                    )
                ]),
                
                # Password input
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
                            "border": f"2px solid {theme['border_light']}",
                            "borderRadius": "8px",
                            "fontSize": "1rem",
                            "backgroundColor": theme["card_bg"],
                            "color": theme["text_primary"],
                            "outline": "none",
                            "transition": "all 0.2s ease",
                            "marginBottom": "1rem"
                        }
                    )
                ]),
                
                # Login status message
                html.Div(
                    id="login-status-message",
                    style={
                        "color": theme["error"],
                        "fontSize": "0.9rem",
                        "marginBottom": "1rem",
                        "minHeight": "20px",
                        "textAlign": "center"
                    }
                ),
                
                # Username/Password Login Button
                html.Button(
                    [
                        html.Span("🔐", style={
                            "marginRight": "8px",
                            "fontSize": "1.1rem"
                        }),
                        "Sign In"
                    ],
                    id="credentials-login-btn",
                    style={
                        "width": "100%",
                        "padding": "12px 20px",
                        "backgroundColor": theme["brand_primary"],
                        "color": "white",
                        "border": "none",
                        "borderRadius": "8px",
                        "fontSize": "1rem",
                        "fontWeight": "600",
                        "cursor": "pointer",
                        "transition": "all 0.2s ease",
                        "display": "flex",
                        "alignItems": "center",
                        "justifyContent": "center",
                        "marginBottom": "1rem",
                        "boxShadow": f"0 4px 12px {theme['brand_primary']}44"
                    }
                ),
                
                # Quick login buttons for demo purposes
                html.Div([
                    html.P(
                        "Quick Login (Demo):",
                        style={
                            "color": theme["text_secondary"],
                            "fontSize": "0.8rem",
                            "marginBottom": "0.5rem"
                        }
                    ),
                    html.Div([
                        html.Button(
                            "Admin",
                            id="quick-admin-btn",
                            style={
                                "padding": "6px 12px",
                                "backgroundColor": "transparent",
                                "color": theme["text_secondary"],
                                "border": f"1px solid {theme['border_light']}",
                                "borderRadius": "4px",
                                "fontSize": "0.8rem",
                                "cursor": "pointer",
                                "margin": "0 4px"
                            }
                        ),
                        html.Button(
                            "Demo",
                            id="quick-demo-btn",
                            style={
                                "padding": "6px 12px",
                                "backgroundColor": "transparent",
                                "color": theme["text_secondary"],
                                "border": f"1px solid {theme['border_light']}",
                                "borderRadius": "4px",
                                "fontSize": "0.8rem",
                                "cursor": "pointer",
                                "margin": "0 4px"
                            }
                        ),
                        html.Button(
                            "Viewer",
                            id="quick-viewer-btn",
                            style={
                                "padding": "6px 12px",
                                "backgroundColor": "transparent",
                                "color": theme["text_secondary"],
                                "border": f"1px solid {theme['border_light']}",
                                "borderRadius": "4px",
                                "fontSize": "0.8rem",
                                "cursor": "pointer",
                                "margin": "0 4px"
                            }
                        )
                    ], style={
                        "display": "flex",
                        "justifyContent": "center",
                        "flexWrap": "wrap"
                    })
                ])
                
            ], style={"textAlign": "left"}),
            
            # Back to public button
            html.Button(
                [
                    html.Span("🔙", style={"marginRight": "8px"}),
                    "Back to Public View"
                ],
                id="back-to-public-btn",
                style={
                    "width": "100%",
                    "padding": "12px 20px",
                    "backgroundColor": "transparent",
                    "color": theme["text_secondary"],
                    "border": f"2px solid {theme['border_light']}",
                    "borderRadius": "8px",
                    "fontSize": "0.9rem",
                    "fontWeight": "500",
                    "cursor": "pointer",
                    "transition": "all 0.2s ease",
                    "display": "flex",
                    "alignItems": "center",
                    "justifyContent": "center",
                    "marginTop": "1.5rem"
                }
            )
        ]
    )


def create_login_layout(theme_name="dark"):
    """Create complete themed login layout"""
    theme_styles = get_theme_styles(theme_name)
    theme = theme_styles["theme"]
    
    return html.Div(
        className="login-layout",
        style={
            **theme_styles["container_style"],
            "minHeight": "100vh",
            "background": f"linear-gradient(135deg, {theme['primary_bg']} 0%, {theme['secondary_bg']} 100%)",
            "position": "relative",
            "overflow": "hidden"
        },
        children=[
            # Hover overlay banner
            create_hover_overlay_banner(theme_name),
            
            # Background effects
            html.Div(
                className="background-effects",
                style={
                    "position": "absolute",
                    "top": "0",
                    "left": "0",
                    "width": "100%",
                    "height": "100%",
                    "pointerEvents": "none",
                    "opacity": "0.1"
                }
            ),
            
            # Main content
            html.Div(
                className="login-content",
                style={
                    "position": "relative",
                    "zIndex": "2",
                    "display": "flex",
                    "alignItems": "center",
                    "justifyContent": "center",
                    "minHeight": "100vh",
                    "padding": "2rem 1rem"
                },
                children=[
                    create_login_form(theme)
                ]
            )
        ]
    )


def create_auth_status_card(theme, message_type="info", title="", message=""):
    """Create authentication status card for feedback"""
    color_map = {
        "success": theme["success"],
        "error": theme["error"],
        "warning": theme["warning"],
        "info": theme["info"]
    }
    
    icon_map = {
        "success": "✅",
        "error": "❌", 
        "warning": "⚠️",
        "info": "ℹ️"
    }
    
    color = color_map.get(message_type, theme["info"])
    icon = icon_map.get(message_type, "ℹ️")
    
    return html.Div(
        id="auth-status-card",
        style={
            "maxWidth": "400px",
            "margin": "1rem auto",
            "backgroundColor": theme["card_bg"],
            "border": f"2px solid {color}",
            "borderRadius": "12px",
            "padding": "1.5rem",
            "textAlign": "center",
            "display": "none"  # Hidden by default
        },
        children=[
            html.Div(icon, style={"fontSize": "2rem", "marginBottom": "1rem"}),
            html.H3(
                title,
                style={
                    "color": color,
                    "fontSize": "1.2rem",
                    "fontWeight": "700",
                    "marginBottom": "0.5rem"
                }
            ),
            html.P(
                message,
                style={
                    "color": theme["text_secondary"],
                    "fontSize": "1rem",
                    "lineHeight": "1.5",
                    "margin": "0"
                }
            )
        ]
    )

def build_login_layout(theme_name="dark", error_message=""):
    """
    Build the complete login page layout
    
    Args:
        theme_name (str): Current theme name
        error_message (str): Error message to display
        
    Returns:
        html.Div: Complete login layout
    """
    theme_styles = get_theme_styles(theme_name)
    theme = theme_styles["theme"]
    
    # Determine error display
    show_error = bool(error_message)
    error_card_style = {"display": "block" if show_error else "none"}
    
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
                            **error_card_style
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
                    
                    # Login form
                    create_login_form(theme)
                ]
            )
        ]
    )

def create_mobile_login_layout(theme_name="dark"):
    """Create mobile-optimized login layout"""
    theme_styles = get_theme_styles(theme_name)
    theme = theme_styles["theme"]
    
    return html.Div(
        className="mobile-login-layout",
        style={
            **theme_styles["container_style"],
            "padding": "1rem"
        },
        children=[
            create_hover_overlay_banner(theme_name),
            html.Div(
                style={
                    **theme_styles["main_content_style"],
                    "padding": "1rem"
                },
                children=[
                    # Compact hero for mobile
                    html.Div(
                        style={
                            "textAlign": "center",
                            "marginBottom": "2rem"
                        },
                        children=[
                            html.H1(
                                "Admin Login",
                                style={
                                    "color": theme["text_primary"],
                                    "fontSize": "1.8rem",
                                    "marginBottom": "0.5rem"
                                }
                            ),
                            html.P(
                                "Secure access required",
                                style={
                                    "color": theme["text_secondary"],
                                    "fontSize": "1rem"
                                }
                            )
                        ]
                    ),
                    
                    # Mobile-optimized form
                    create_login_form(theme)
                ]
            )
        ]
    )