# footer.py
from dash import html
import datetime

def render_footer():
    """
    Render responsive footer following minimal text and high contrast principles
    Optimized for all screen sizes with PWA indicators
    """
    return html.Div(
        className="app-footer",
        id="app-footer",
        style={
            "backgroundColor": "#0D1B2A",
            "color": "#FFFFFF",
            "padding": "0.75rem 2rem",
            "textAlign": "center",
            "fontSize": "0.9rem",
            "position": "fixed",
            "bottom": "0",
            "width": "100%",
            "zIndex": "1000",
            "borderTop": "2px solid #2D3748",
            "boxShadow": "0 -2px 10px rgba(0, 0, 0, 0.2)"
        },
        children=[
            html.Div(
                className="footer-content",
                id="footer-content",
                style={
                    "display": "flex",
                    "justifyContent": "space-between",
                    "alignItems": "center",
                    "maxWidth": "1200px",
                    "margin": "0 auto"
                },
                children=[
                    # Left side - Copyright
                    html.Div(
                        className="footer-left",
                        id="footer-left",
                        children=[
                            html.Span(
                                "© 2025 Swaccha Andhra Corporation",
                                style={
                                    "fontWeight": "500",
                                    "color": "#A0AEC0"
                                }
                            )
                        ]
                    ),
                    
                    # Center - Device indicators (hidden on mobile)
                    html.Div(
                        className="footer-center",
                        id="footer-center",
                        style={
                            "display": "flex",
                            "gap": "1rem",
                            "alignItems": "center"
                        },
                        children=[
                            create_device_indicator("📱", "Mobile Ready"),
                            create_device_indicator("💻", "Web Optimized"),
                            create_device_indicator("📺", "TV Compatible")
                        ]
                    ),
                    
                    # Right side - PWA status
                    html.Div(
                        className="footer-right",
                        id="footer-right",
                        children=[
                            html.Div(
                                id="pwa-status",
                                children=[
                                    html.Span(
                                        "⚡",
                                        style={
                                            "marginRight": "0.5rem",
                                            "color": "#68D391"
                                        }
                                    ),
                                    html.Span(
                                        "PWA Ready",
                                        style={
                                            "fontWeight": "600",
                                            "color": "#68D391",
                                            "fontSize": "0.8rem"
                                        }
                                    )
                                ],
                                style={
                                    "display": "flex",
                                    "alignItems": "center"
                                }
                            )
                        ]
                    )
                ]
            )
        ]
    )

def create_device_indicator(icon, label):
    """Create device compatibility indicators"""
    return html.Div(
        style={
            "display": "flex",
            "alignItems": "center",
            "fontSize": "0.8rem",
            "color": "#A0AEC0"
        },
        children=[
            html.Span(
                icon,
                style={
                    "marginRight": "0.25rem",
                    "fontSize": "1rem"
                }
            ),
            html.Span(label)
        ]
    )

def render_mobile_footer():
    """
    Render mobile-optimized footer with essential info only
    """
    return html.Div(
        className="app-footer mobile-footer",
        style={
            "backgroundColor": "#0D1B2A",
            "color": "#FFFFFF",
            "padding": "0.5rem 1rem",
            "textAlign": "center",
            "fontSize": "0.8rem",
            "position": "fixed",
            "bottom": "0",
            "width": "100%",
            "zIndex": "1000",
            "borderTop": "2px solid #2D3748"
        },
        children=[
            html.Div(
                style={
                    "display": "flex",
                    "justifyContent": "space-between",
                    "alignItems": "center"
                },
                children=[
                    html.Span(
                        "© 2025 Swaccha AP",
                        style={
                            "color": "#A0AEC0",
                            "fontSize": "0.7rem"
                        }
                    ),
                    html.Div([
                        html.Span("⚡", style={"color": "#68D391", "marginRight": "0.25rem"}),
                        html.Span("PWA", style={"color": "#68D391", "fontSize": "0.7rem", "fontWeight": "600"})
                    ], style={"display": "flex", "alignItems": "center"})
                ]
            )
        ]
    )

def render_tv_footer():
    """
    Render TV-optimized footer with larger text and spacing
    """
    current_time = datetime.datetime.now()
    
    return html.Div(
        className="app-footer tv-footer",
        style={
            "backgroundColor": "#0D1B2A",
            "color": "#FFFFFF",
            "padding": "1.5rem 3rem",
            "textAlign": "center",
            "fontSize": "1.2rem",
            "position": "fixed",
            "bottom": "0",
            "width": "100%",
            "zIndex": "1000",
            "borderTop": "3px solid #3182CE",
            "boxShadow": "0 -4px 20px rgba(0, 0, 0, 0.3)"
        },
        children=[
            html.Div(
                style={
                    "display": "flex",
                    "justifyContent": "space-between",
                    "alignItems": "center",
                    "maxWidth": "1400px",
                    "margin": "0 auto"
                },
                children=[
                    # Left - Enhanced copyright for TV
                    html.Div([
                        html.Div(
                            "© 2025 Swaccha Andhra Corporation",
                            style={
                                "fontWeight": "600",
                                "color": "#FFFFFF",
                                "fontSize": "1.1rem"
                            }
                        ),
                        html.Div(
                            "स्वच्छता • पारदर्शिता • प्रगति",
                            style={
                                "fontWeight": "400",
                                "color": "#A0AEC0",
                                "fontSize": "0.9rem",
                                "marginTop": "0.25rem"
                            }
                        )
                    ]),
                    
                    # Center - Large device indicators
                    html.Div(
                        style={
                            "display": "flex",
                            "gap": "2rem",
                            "alignItems": "center"
                        },
                        children=[
                            create_tv_device_indicator("📱", "Mobile Ready", "#68D391"),
                            create_tv_device_indicator("💻", "Web Dashboard", "#3182CE"),
                            create_tv_device_indicator("📺", "TV Display", "#DD6B20"),
                            create_tv_device_indicator("⚡", "PWA Enabled", "#9F7AEA")
                        ]
                    ),
                    
                    # Right - System info for TV
                    html.Div([
                        html.Div(
                            "LIVE DASHBOARD",
                            style={
                                "fontWeight": "800",
                                "color": "#68D391",
                                "fontSize": "1rem",
                                "textAlign": "right"
                            }
                        ),
                        html.Div(
                            f"Updated: {current_time.strftime('%H:%M:%S')}",
                            style={
                                "fontWeight": "400",
                                "color": "#A0AEC0",
                                "fontSize": "0.9rem",
                                "marginTop": "0.25rem",
                                "fontFamily": "monospace"
                            }
                        )
                    ])
                ]
            )
        ]
    )

def create_tv_device_indicator(icon, label, color):
    """Create large device indicators for TV viewing"""
    return html.Div(
        style={
            "display": "flex",
            "flexDirection": "column",
            "alignItems": "center",
            "padding": "0.5rem",
            "backgroundColor": "#1A1F2E",
            "borderRadius": "8px",
            "border": f"2px solid {color}",
            "minWidth": "100px"
        },
        children=[
            html.Div(
                icon,
                style={
                    "fontSize": "1.5rem",
                    "marginBottom": "0.25rem"
                }
            ),
            html.Div(
                label,
                style={
                    "fontSize": "0.8rem",
                    "fontWeight": "600",
                    "color": color,
                    "textAlign": "center",
                    "lineHeight": "1.1"
                }
            )
        ]
    )

def render_status_footer():
    """
    Render footer with system status for monitoring dashboards
    """
    current_time = datetime.datetime.now()
    
    status_items = [
        {"label": "Data Sync", "status": "Active", "color": "#38A169"},
        {"label": "API", "status": "Online", "color": "#3182CE"},
        {"label": "Mobile", "status": "Connected", "color": "#68D391"},
        {"label": "Reports", "status": "Ready", "color": "#DD6B20"}
    ]
    
    return html.Div(
        className="app-footer status-footer",
        style={
            "backgroundColor": "#0D1B2A",
            "color": "#FFFFFF",
            "padding": "1rem 2rem",
            "position": "fixed",
            "bottom": "0",
            "width": "100%",
            "zIndex": "1000",
            "borderTop": "2px solid #2D3748",
            "boxShadow": "0 -2px 10px rgba(0, 0, 0, 0.2)"
        },
        children=[
            html.Div(
                style={
                    "display": "flex",
                    "justifyContent": "space-between",
                    "alignItems": "center",
                    "maxWidth": "1200px",
                    "margin": "0 auto",
                    "flexWrap": "wrap",
                    "gap": "1rem"
                },
                children=[
                    # System status indicators
                    html.Div(
                        style={
                            "display": "flex",
                            "gap": "1.5rem",
                            "flexWrap": "wrap"
                        },
                        children=[
                            create_status_item(item["label"], item["status"], item["color"])
                            for item in status_items
                        ]
                    ),
                    
                    # Last updated timestamp
                    html.Div(
                        f"Last Updated: {current_time.strftime('%H:%M:%S')}",
                        style={
                            "fontSize": "0.9rem",
                            "color": "#A0AEC0",
                            "fontFamily": "monospace",
                            "fontWeight": "500"
                        }
                    )
                ]
            )
        ]
    )

def create_status_item(label, status, color):
    """Create individual status items"""
    return html.Div(
        style={
            "display": "flex",
            "alignItems": "center",
            "fontSize": "0.8rem"
        },
        children=[
            html.Span(
                "●",
                style={
                    "color": color,
                    "fontSize": "1rem",
                    "marginRight": "0.5rem"
                }
            ),
            html.Span(
                f"{label}: ",
                style={
                    "color": "#A0AEC0",
                    "fontWeight": "400"
                }
            ),
            html.Span(
                status,
                style={
                    "color": color,
                    "fontWeight": "600"
                }
            )
        ]
    )