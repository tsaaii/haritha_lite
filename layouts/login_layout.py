# layouts/login_layout.py - ENHANCED with Real-time PDF Generation
"""
Enhanced Magic View with Real-time PDF Summary Generation
"""

from dash import html, dcc
import requests
from datetime import datetime

def get_sites_from_api():
    """Get sites from API with fallback"""
    try:
        response = requests.get("https://weighbridge-api-287877277037.asia-southeast1.run.app/sites", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return sorted(data.get("sites", []))
    except:
        pass
    return ["Adoni", "Bheemavaram", "Nandyal", "Yemmiganur"]

def create_magic_view_section(sites, dropdown_options):
    """Create Magic View section for site selection - Enhanced Colors"""
    
    return html.Div(
        className="option-card magic-view-card",
        style={
            "background": "linear-gradient(135deg, #2D3748 0%, #1A202C 100%)",
            "borderRadius": "20px",
            "padding": "2.5rem",
            "border": "3px solid #eb9534",
            "boxShadow": "0 15px 35px rgba(235, 149, 52, 0.3), 0 5px 15px rgba(0, 0, 0, 0.2)",
            "position": "relative",
            "overflow": "hidden"
        },
        children=[
            # Animated background glow
            html.Div(
                style={
                    "position": "absolute",
                    "top": "-50%",
                    "left": "-50%",
                    "width": "200%",
                    "height": "200%",
                    "background": "radial-gradient(circle, rgba(235, 149, 52, 0.1) 0%, transparent 70%)",
                    "animation": "pulse 3s ease-in-out infinite",
                    "zIndex": "0"
                }
            ),
            
            # Content container
            html.Div(
                style={"position": "relative", "zIndex": "1"},
                children=[
                    # Header with enhanced mobile styling
                    html.Div([
                        html.Div("✨", style={
                            "fontSize": "3rem", 
                            "marginBottom": "0.8rem",
                            "textShadow": "0 0 20px rgba(235, 149, 52, 0.6)"
                        }),
                        html.H3(
                            "Magic View", 
                            style={
                                "color": "#eb9534", 
                                "fontSize": "1.8rem", 
                                "fontWeight": "800", 
                                "marginBottom": "0.8rem",
                                "textShadow": "0 2px 4px rgba(0, 0, 0, 0.3)"
                            }
                        ),
                        html.P(
                            "Choose your destination to explore the future",
                            style={
                                "color": "#E2E8F0", 
                                "fontSize": "1rem", 
                                "marginBottom": "2rem",
                                "fontWeight": "400"
                            }
                        )
                    ], style={"textAlign": "center"}),
                    
                    # Site Selection Dropdown
                    html.Div([
                        html.Label(
                            "Select Your Site:",
                            style={
                                "color": "#FFFFFF", 
                                "fontSize": "1rem", 
                                "fontWeight": "600", 
                                "display": "block", 
                                "marginBottom": "0.8rem",
                                "textAlign": "left"
                            }
                        ),
                        dcc.Dropdown(
                            id="site-selection-dropdown",
                            options=dropdown_options,
                            placeholder="Choose a site to explore...",
                            style={
                                "marginBottom": "2rem",
                                "fontSize": "1.1rem"
                            },
                            className="custom-dropdown"
                        )
                    ]),
                    
                    # Magic Button
                    html.Button(
                        ["🚀 Enter Magic Dashboard"],
                        id="magic-view-btn",
                        disabled=True,
                        style={
                            "width": "100%", 
                            "padding": "16px 20px", 
                            "backgroundColor": "#eb9534",
                            "color": "white", 
                            "border": "none", 
                            "borderRadius": "12px",
                            "fontSize": "1.1rem", 
                            "fontWeight": "700", 
                            "cursor": "pointer",
                            "transition": "all 0.3s ease", 
                            "minHeight": "56px",
                            "textTransform": "uppercase",
                            "letterSpacing": "1px",
                            "boxShadow": "0 8px 20px rgba(235, 149, 52, 0.4)"
                        }
                    ),
                    
                    # Status
                    html.P(
                        f"🌟 {len(sites)} magical destinations available",
                        style={
                            "color": "#A0AEC0", 
                            "fontSize": "0.85rem", 
                            "marginTop": "1.5rem", 
                            "textAlign": "center",
                            "fontStyle": "italic"
                        }
                    )
                ]
            )
        ]
    )

def create_login_portal_section():
    """Create Login Portal section for traditional login - Mobile Optimized"""
    return html.Div(
        className="option-card",
        style={
            "backgroundColor": "#2D3748",
            "borderRadius": "16px",
            "padding": "2rem",
            "border": "2px solid #38A169",
            "boxShadow": "0 8px 25px rgba(56, 161, 105, 0.2)",
            "transition": "all 0.3s ease"
        },
        children=[
            # Header
            html.Div([
                html.Div("🔐", style={"fontSize": "2.5rem", "marginBottom": "0.5rem"}),
                html.H3(
                    "Login Portal", 
                    style={"color": "#38A169", "fontSize": "1.5rem", "fontWeight": "700", "marginBottom": "0.5rem"}
                ),
                html.P(
                    "Access the legacy report dashboard",
                    style={"color": "#A0AEC0", "fontSize": "0.9rem", "marginBottom": "1.5rem"}
                )
            ], style={"textAlign": "center"}),
            
            # Username Input
            html.Div([
                html.Label(
                    "Username:",
                    style={"color": "#FFFFFF", "fontSize": "0.9rem", "fontWeight": "600", "display": "block", "marginBottom": "0.5rem"}
                ),
                dcc.Input(
                    id="username-input",
                    type="text",
                    placeholder="Enter username",
                    style={
                        "width": "100%", "padding": "12px", "borderRadius": "6px",
                        "border": "1px solid #4A5568", "backgroundColor": "#374151",
                        "color": "#FFFFFF", "marginBottom": "1rem", "fontSize": "16px",
                        "minHeight": "48px"  # Touch-friendly
                    }
                )
            ]),
            
            # Password Input
            html.Div([
                html.Label(
                    "Password:",
                    style={"color": "#FFFFFF", "fontSize": "0.9rem", "fontWeight": "600", "display": "block", "marginBottom": "0.5rem"}
                ),
                dcc.Input(
                    id="password-input",
                    type="password",
                    placeholder="Enter password",
                    style={
                        "width": "100%", "padding": "12px", "borderRadius": "6px",
                        "border": "1px solid #4A5568", "backgroundColor": "#374151",
                        "color": "#FFFFFF", "marginBottom": "1.5rem", "fontSize": "16px",
                        "minHeight": "48px"  # Touch-friendly
                    }
                )
            ]),
            
            # Login Button
            html.Button(
                ["🔑 Login to Reports"],
                id="username-password-login-btn",
                style={
                    "width": "100%", "padding": "14px 20px", "backgroundColor": "#38A169",
                    "color": "white", "border": "none", "borderRadius": "8px",
                    "fontSize": "1rem", "fontWeight": "600", "cursor": "pointer",
                    "transition": "all 0.3s ease", "minHeight": "48px"
                }
            ),
            
            # Help Text
            html.P(
                "💡 For password reach out to Advitia Labs",
                style={"color": "#68748D", "fontSize": "0.8rem", "marginTop": "1rem", "textAlign": "center", "fontStyle": "italic"}
            )
        ]
    )

def create_quick_summary_section():
    """Create Quick Summary section for Real-time PDF download - Mobile Optimized"""
    return html.Div(
        className="option-card",
        style={
            "backgroundColor": "#2D3748",
            "borderRadius": "16px",
            "padding": "2rem",
            "border": "2px solid #DD6B20",
            "boxShadow": "0 8px 25px rgba(221, 107, 32, 0.2)",
            "transition": "all 0.3s ease"
        },
        children=[
            # Header
            html.Div([
                html.Div("📊", style={"fontSize": "2.5rem", "marginBottom": "0.5rem"}),
                html.H3(
                    "Quick Summary", 
                    style={"color": "#DD6B20", "fontSize": "1.5rem", "fontWeight": "700", "marginBottom": "0.5rem"}
                ),
                html.P(
                    "Download real-time PDF summary report",
                    style={"color": "#A0AEC0", "fontSize": "0.9rem", "marginBottom": "1.5rem"}
                )
            ], style={"textAlign": "center"}),
            
            # Description
            html.Div([
                html.P(
                    "Get a comprehensive summary of all operations across sites with real-time data from the weighbridge API.",
                    style={"color": "#A0AEC0", "fontSize": "0.85rem", "lineHeight": "1.4", "marginBottom": "1.5rem", "textAlign": "left"}
                ),
                
                html.Ul([
                    html.Li("✅ All sites data aggregated", style={"color": "#A0AEC0", "fontSize": "0.8rem", "marginBottom": "0.3rem"}),
                    html.Li("✅ Real-time weighbridge statistics", style={"color": "#A0AEC0", "fontSize": "0.8rem", "marginBottom": "0.3rem"}),
                    html.Li("✅ Performance metrics & alerts", style={"color": "#A0AEC0", "fontSize": "0.8rem", "marginBottom": "1rem"}),
                ], style={"paddingLeft": "1rem"})
            ]),
            
            # Real-time Download Button
            html.A(
                html.Button(
                    ["📥 Generate Live Report"],
                    id="realtime-summary-btn",
                    style={
                        "width": "100%", "padding": "14px 20px", "backgroundColor": "#DD6B20",
                        "color": "white", "border": "none", "borderRadius": "8px",
                        "fontSize": "1rem", "fontWeight": "600", "cursor": "pointer",
                        "transition": "all 0.3s ease", "minHeight": "48px"
                    }
                ),
                href="/api/legacy-project/download",  # NEW: Real-time PDF endpoint
                style={"textDecoration": "none"}
            ),  
            
            # Status with live timestamp
            html.P(
                f"🔄 Real-time data • Generated: {datetime.now().strftime('%H:%M:%S')}",
                style={"color": "#68748D", "fontSize": "0.8rem", "marginTop": "1rem", "textAlign": "center"}
            )
        ]
    )

def build_login_layout(theme_name="dark", error_message=""):
    """Enhanced Magic View with 3 options including real-time PDF"""
    
    # Get sites from API
    sites = get_sites_from_api()
    
    # Create dropdown options
    dropdown_options = [{"label": site.title(), "value": site} for site in sites]
    
    return html.Div(
        style={
            "minHeight": "100vh",
            "background": "linear-gradient(135deg, #0F172A 0%, #1E293B 50%, #334155 100%)",
            "padding": "1rem",
            "fontFamily": "'Inter', -apple-system, BlinkMacSystemFont, sans-serif"
        },
        children=[
            # Header
            html.Div(
                style={
                    "textAlign": "center",
                    "marginBottom": "3rem",
                    "paddingTop": "2rem"
                },
                children=[
                    html.H1(
                        "🌟 Swachh Andhra Pradesh",
                        style={
                            "color": "#FFFFFF",
                            "fontSize": "clamp(2rem, 5vw, 3.5rem)",
                            "fontWeight": "800",
                            "marginBottom": "0.5rem",
                            "textShadow": "0 4px 8px rgba(0, 0, 0, 0.3)"
                        }
                    ),
                    html.P(
                        "Choose your path to data excellence",
                        style={
                            "color": "#94A3B8",
                            "fontSize": "1.2rem",
                            "fontWeight": "400"
                        }
                    )
                ]
            ),
            
            # Error Message
            html.Div(
                id="error-message",
                children=[
                    html.Div(
                        "⚠️ " + error_message,
                        style={
                            "backgroundColor": "#FEE2E2",
                            "color": "#DC2626",
                            "padding": "1rem",
                            "borderRadius": "8px",
                            "marginBottom": "2rem",
                            "textAlign": "center"
                        }
                    )
                ] if error_message else [],
                style={"maxWidth": "600px", "margin": "0 auto"}
            ),
            
            # Three Options Grid
            html.Div(
                className="options-grid",
                style={
                    "display": "grid",
                    "gridTemplateColumns": "repeat(auto-fit, minmax(350px, 1fr))",
                    "gap": "2rem",
                    "maxWidth": "1400px",
                    "margin": "0 auto",
                    "padding": "0 1rem"
                },
                children=[
                    # Option 1: Magic View
                    create_magic_view_section(sites, dropdown_options),
                    
                    # Option 2: Login Portal
                    create_login_portal_section(),
                    
                    # Option 3: Quick Summary (ENHANCED)
                    create_quick_summary_section()
                ]
            )
        ]
    )