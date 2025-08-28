# layouts/unauthorized_layout.py - FIXED VERSION
"""
Unauthorized Access Layout - FIXED
Shows when user tries to access protected content without proper authorization
Auto-redirects to public layout after 5 seconds with working countdown
"""

from dash import html, dcc
from utils.theme_utils import get_theme_styles
from components.navigation.hover_overlay import create_hover_overlay_banner


def create_unauthorized_layout(theme_name="dark", redirect_message="Unauthorized access. Redirecting to public dashboard..."):
    """
    Create unauthorized access layout with auto-redirect
    
    Args:
        theme_name (str): Current theme name
        redirect_message (str): Message to display
        
    Returns:
        html.Div: Unauthorized layout with countdown and auto-redirect
    """
    theme_styles = get_theme_styles(theme_name)
    theme = theme_styles["theme"]
    
    return html.Div(
        className="unauthorized-layout",
        style=theme_styles["container_style"],
        children=[
            # Hover overlay for theme switching
            create_hover_overlay_banner(theme_name),
            
            # FIXED: Include intervals directly in this layout
            # Auto-redirect interval component (redirects after 5 seconds)
            dcc.Interval(
                id='unauthorized-redirect-timer',
                interval=5000,  # 5 seconds
                n_intervals=0,
                max_intervals=1  # Only trigger once
            ),
            
            # Countdown interval (updates every second)
            dcc.Interval(
                id='unauthorized-countdown-timer',
                interval=1000,  # 1 second
                n_intervals=0,
                max_intervals=5  # Count down from 5
            ),
            
            # Main unauthorized content
            html.Div(
                className="unauthorized-content",
                style={
                    **theme_styles["main_content_style"],
                    "display": "flex",
                    "justifyContent": "center",
                    "alignItems": "center",
                    "minHeight": "80vh",
                    "textAlign": "center"
                },
                children=[
                    # Unauthorized message card
                    html.Div(
                        style={
                            "backgroundColor": theme["card_bg"],
                            "borderRadius": "16px",
                            "border": f"3px solid {theme['error']}",
                            "boxShadow": "0 12px 40px rgba(229, 62, 62, 0.3)",
                            "padding": "3rem 2rem",
                            "maxWidth": "500px",
                            "width": "100%",
                            "position": "relative",
                            "overflow": "hidden"
                        },
                        children=[
                            # Background decoration
                            html.Div(
                                style={
                                    "position": "absolute",
                                    "top": "-50px",
                                    "right": "-50px",
                                    "width": "150px",
                                    "height": "150px",
                                    "background": f"radial-gradient(circle, {theme['error']}33 0%, transparent 70%)",
                                    "borderRadius": "50%",
                                    "pointerEvents": "none"
                                }
                            ),
                            
                            # Warning icon
                            html.Div(
                                "🚫",
                                style={
                                    "fontSize": "4rem",
                                    "marginBottom": "1.5rem",
                                    "animation": "pulse 2s infinite"
                                }
                            ),
                            
                            # Main title
                            html.H1(
                                "Access Denied",
                                style={
                                    "color": theme["error"],
                                    "fontSize": "2.5rem",
                                    "fontWeight": "900",
                                    "marginBottom": "1rem",
                                    "textShadow": "2px 2px 4px rgba(0, 0, 0, 0.3)"
                                }
                            ),
                            
                            # Subtitle
                            html.P(
                                "You are not authorized to access this dashboard section.",
                                style={
                                    "color": theme["text_secondary"],
                                    "fontSize": "1.2rem",
                                    "marginBottom": "2rem",
                                    "lineHeight": "1.6"
                                }
                            ),
                            
                            # Redirect message with countdown
                            html.Div([
                                html.P(
                                    redirect_message,
                                    style={
                                        "color": theme["text_primary"],
                                        "fontSize": "1rem",
                                        "marginBottom": "1rem",
                                        "fontWeight": "600"
                                    }
                                ),
                                
                                # FIXED: Countdown display with better styling
                                html.Div([
                                    html.Span(
                                        "Redirecting in: ",
                                        style={
                                            "color": theme["text_secondary"],
                                            "fontSize": "1rem"
                                        }
                                    ),
                                    html.Span(
                                        id="countdown-display",
                                        children="5",  # Default starting value
                                        style={
                                            "color": theme["brand_primary"],
                                            "fontSize": "2rem",
                                            "fontWeight": "900",
                                            "fontFamily": "monospace",
                                            "textShadow": "2px 2px 4px rgba(0, 0, 0, 0.3)",
                                            "padding": "0.25rem 0.5rem",
                                            "backgroundColor": theme["accent_bg"],
                                            "borderRadius": "8px",
                                            "border": f"2px solid {theme['brand_primary']}",
                                            "margin": "0 0.5rem",
                                            "display": "inline-block",
                                            "minWidth": "40px",
                                            "textAlign": "center"
                                        }
                                    ),
                                    html.Span(
                                        " seconds",
                                        style={
                                            "color": theme["text_secondary"],
                                            "fontSize": "1rem"
                                        }
                                    )
                                ], style={
                                    "marginBottom": "2rem",
                                    "padding": "1rem",
                                    "backgroundColor": theme["accent_bg"],
                                    "borderRadius": "8px",
                                    "border": f"1px solid {theme['border_light']}"
                                })
                            ]),
                            
                            # FIXED: Progress bar with animation
                            html.Div([
                                html.Div(
                                    style={
                                        "width": "100%",
                                        "height": "8px",
                                        "backgroundColor": theme["accent_bg"],
                                        "borderRadius": "4px",
                                        "overflow": "hidden",
                                        "marginBottom": "1rem",
                                        "border": f"1px solid {theme['border_light']}"
                                    },
                                    children=[
                                        html.Div(
                                            id="redirect-progress-bar",
                                            style={
                                                "height": "100%",
                                                "backgroundColor": theme["brand_primary"],
                                                "borderRadius": "3px",
                                                "width": "0%",
                                                "animation": "progressFill 5s linear forwards",
                                                "boxShadow": f"0 0 10px {theme['brand_primary']}44"
                                            }
                                        )
                                    ]
                                )
                            ]),
                            
                            # Manual redirect buttons
                            html.Div([
                                html.Button(
                                    [
                                        html.Span("🏠", style={"marginRight": "0.5rem"}),
                                        "Go to Public Dashboard Now"
                                    ],
                                    id="manual-redirect-btn",
                                    style={
                                        "backgroundColor": theme["brand_primary"],
                                        "color": "white",
                                        "border": "none",
                                        "padding": "0.75rem 1.5rem",
                                        "borderRadius": "8px",
                                        "fontSize": "1rem",
                                        "fontWeight": "600",
                                        "cursor": "pointer",
                                        "transition": "all 0.2s ease",
                                        "marginRight": "1rem",
                                        "boxShadow": f"0 4px 12px {theme['brand_primary']}44"
                                    }
                                ),
                                html.Button(
                                    [
                                        html.Span("🔐", style={"marginRight": "0.5rem"}),
                                        "Login"
                                    ],
                                    id="login-redirect-btn",
                                    style={
                                        "backgroundColor": "transparent",
                                        "color": theme["text_secondary"],
                                        "border": f"2px solid {theme['border_light']}",
                                        "padding": "0.75rem 1.5rem",
                                        "borderRadius": "8px",
                                        "fontSize": "1rem",
                                        "fontWeight": "600",
                                        "cursor": "pointer",
                                        "transition": "all 0.2s ease"
                                    }
                                )
                            ], style={
                                "display": "flex",
                                "gap": "1rem",
                                "justifyContent": "center",
                                "flexWrap": "wrap"
                            })
                        ]
                    )
                ]
            )
        ]
    )


def create_mobile_unauthorized_layout(theme_name="dark"):
    """Create mobile-optimized unauthorized layout"""
    theme_styles = get_theme_styles(theme_name)
    theme = theme_styles["theme"]
    
    return html.Div(
        className="mobile-unauthorized-layout",
        style={
            **theme_styles["container_style"],
            "padding": "1rem"
        },
        children=[
            create_hover_overlay_banner(theme_name),
            
            # Include intervals in mobile layout too
            dcc.Interval(
                id='unauthorized-redirect-timer',
                interval=5000,  # 5 seconds
                n_intervals=0,
                max_intervals=1
            ),
            
            dcc.Interval(
                id='unauthorized-countdown-timer',
                interval=1000,  # 1 second
                n_intervals=0,
                max_intervals=5
            ),
            
            html.Div(
                style={
                    **theme_styles["main_content_style"],
                    "padding": "2rem 1rem",
                    "textAlign": "center",
                    "minHeight": "80vh",
                    "display": "flex",
                    "flexDirection": "column",
                    "justifyContent": "center"
                },
                children=[
                    # Compact unauthorized message
                    html.Div(
                        style={
                            "backgroundColor": theme["card_bg"],
                            "borderRadius": "12px",
                            "border": f"2px solid {theme['error']}",
                            "padding": "2rem 1rem",
                            "boxShadow": "0 8px 24px rgba(229, 62, 62, 0.2)"
                        },
                        children=[
                            html.Div("🚫", style={"fontSize": "3rem", "marginBottom": "1rem"}),
                            html.H2(
                                "Access Denied",
                                style={
                                    "color": theme["error"],
                                    "fontSize": "1.8rem",
                                    "marginBottom": "1rem"
                                }
                            ),
                            html.P(
                                "Unauthorized access. Redirecting...",
                                style={
                                    "color": theme["text_secondary"],
                                    "marginBottom": "1.5rem"
                                }
                            ),
                            html.Div([
                                html.Span("Redirecting in: "),
                                html.Span(
                                    id="countdown-display",
                                    children="5",
                                    style={
                                        "color": theme["brand_primary"],
                                        "fontWeight": "bold",
                                        "fontSize": "1.5rem",
                                        "fontFamily": "monospace"
                                    }
                                ),
                                html.Span(" seconds")
                            ], style={
                                "color": theme["text_primary"],
                                "marginBottom": "1.5rem"
                            }),
                            html.Button(
                                "Go to Public Dashboard",
                                id="manual-redirect-btn",
                                style={
                                    "backgroundColor": theme["brand_primary"],
                                    "color": "white",
                                    "border": "none",
                                    "padding": "0.75rem 1.5rem",
                                    "borderRadius": "8px",
                                    "cursor": "pointer",
                                    "width": "100%"
                                }
                            )
                        ]
                    )
                ]
            )
        ]
    )


# Enhanced CSS for progress bar animation and countdown effects
UNAUTHORIZED_CSS = """
@keyframes progressFill {
    from { width: 0%; }
    to { width: 100%; }
}

@keyframes pulse {
    0%, 100% { transform: scale(1); opacity: 1; }
    50% { transform: scale(1.05); opacity: 0.8; }
}

@keyframes countdownPulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.1); }
}

/* Enhanced countdown styling */
#countdown-display {
    animation: countdownPulse 1s infinite;
}

/* Logout button hover effects */
#logout-btn:hover {
    background: linear-gradient(135deg, #C53030 0%, #9B2C2C 100%) !important;
    transform: translateY(-2px) scale(1.05) !important;
    box-shadow: 0 8px 25px rgba(197, 48, 48, 0.6) !important;
}

#logout-btn:active {
    transform: translateY(0) scale(1.02) !important;
    box-shadow: 0 4px 12px rgba(197, 48, 48, 0.4) !important;
}

.unauthorized-layout .manual-redirect-btn:hover {
    background-color: var(--brand-secondary, #2C5AA0) !important;
    transform: translateY(-2px) scale(1.05) !important;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4) !important;
}

.unauthorized-layout .login-redirect-btn:hover {
    background-color: var(--accent-bg, #1A1F2E) !important;
    border-color: var(--brand-primary, #3182CE) !important;
    color: var(--brand-primary, #3182CE) !important;
    transform: translateY(-2px) !important;
}

/* Progress bar glow effect */
#redirect-progress-bar {
    transition: all 0.3s ease;
}

/* Mobile responsiveness for countdown */
@media (max-width: 768px) {
    #countdown-display {
        font-size: 1.5rem !important;
        padding: 0.5rem !important;
    }
    
    .unauthorized-layout .manual-redirect-btn,
    .unauthorized-layout .login-redirect-btn {
        width: 100% !important;
        margin: 0.5rem 0 !important;
    }
    
    /* Mobile logout button adjustments */
    #logout-btn {
        font-size: 0.8rem !important;
        padding: 0.6rem 1.2rem !important;
    }
}

/* Enhanced dashboard header responsiveness */
@media (max-width: 768px) {
    .dashboard-main-content .header-content {
        flex-direction: column !important;
        text-align: center !important;
    }
    
    .dashboard-main-content .user-info-card {
        margin-top: 1rem !important;
        min-width: auto !important;
        width: 100% !important;
    }
    
    .dashboard-main-content h1 {
        font-size: 2rem !important;
    }
    
    .dashboard-main-content .bottom-info-bar {
        flex-direction: column !important;
        gap: 0.5rem !important;
        text-align: center !important;
    }
    
    .dashboard-main-content .bottom-info-bar span {
        margin: 0 !important;
    }
}
"""

__all__ = ['create_unauthorized_layout', 'create_mobile_unauthorized_layout', 'UNAUTHORIZED_CSS']