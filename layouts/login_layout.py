# layouts/login_layout.py - ENHANCED Magic View with 3 Options
"""
Enhanced Magic View with 3 Options:
1. Magic View - Site selection for dashboard
2. Login Portal - Traditional username/password for /legacy/report
3. Quick Summary - Download PDF summary
"""

from dash import html, dcc
import requests

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
                                "background": "linear-gradient(135deg, #eb9534 0%, #f6ad37 50%, #eb9534 100%)",
                                "WebkitBackgroundClip": "text",
                                "WebkitTextFillColor": "transparent",
                                "backgroundClip": "text",
                                "fontSize": "1.8rem", 
                                "fontWeight": "800", 
                                "marginBottom": "0.5rem",
                                "textAlign": "center"
                            }
                        ),
                        html.P(
                            "Select a site to view its real-time dashboard",
                            style={
                                "color": "#E2E8F0", 
                                "fontSize": "1rem", 
                                "marginBottom": "2rem",
                                "textAlign": "center",
                                "fontWeight": "400"
                            }
                        )
                    ]),
                    
                    # Site Selector
                    html.Div([
                        html.Label(
                            "🏢 Choose Site Location:",
                            style={
                                "color": "#F7FAFC", 
                                "fontSize": "1rem", 
                                "fontWeight": "600", 
                                "display": "block", 
                                "marginBottom": "1rem",
                                "textShadow": "0 1px 3px rgba(0, 0, 0, 0.3)"
                            }
                        ),
                        dcc.Dropdown(
                            id="site-selector-dropdown",
                            options=dropdown_options,
                            placeholder="🔍 Select a site...",
                            style={
                                "marginBottom": "2rem",
                                "fontSize": "1rem"
                            }
                        )
                    ]),
                    
                    # Go Button with mobile optimization
                    html.Button(
                        ["🚀 Go to Dashboard"],
                        id="magic-view-go-btn",
                        style={
                            "width": "100%", 
                            "padding": "14px 24px", 
                            "background": "linear-gradient(135deg, #eb9534 0%, #f6ad37 50%, #eb9534 100%)",
                            "color": "white", 
                            "border": "none", 
                            "borderRadius": "12px",
                            "fontSize": "1.1rem", 
                            "fontWeight": "700", 
                            "cursor": "pointer",
                            "transition": "all 0.3s ease",
                            "textTransform": "uppercase",
                            "letterSpacing": "0.5px",
                            "boxShadow": "0 4px 15px rgba(235, 149, 52, 0.4)",
                            "position": "relative",
                            "minHeight": "48px"  # Touch-friendly
                        }
                    ),
                    
                    # Info with enhanced styling
                    html.P(
                        f"📍 {len(sites)} sites available • Live data",
                        style={
                            "color": "#9CA3AF", 
                            "fontSize": "0.85rem", 
                            "marginTop": "1.5rem", 
                            "textAlign": "center",
                            "fontWeight": "500",
                            "padding": "0.5rem",
                            "backgroundColor": "rgba(235, 149, 52, 0.1)",
                            "borderRadius": "6px",
                            "border": "1px solid rgba(235, 149, 52, 0.2)"
                        }
                    )
                ]
            )
        ]
    )

def create_login_portal_section():
    """Create Login Portal section for traditional authentication - Mobile Optimized"""
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
    """Create Quick Summary section for PDF download - Mobile Optimized"""
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
                    "Download instant PDF summary report",
                    style={"color": "#A0AEC0", "fontSize": "0.9rem", "marginBottom": "1.5rem"}
                )
            ], style={"textAlign": "center"}),
            
            # Description
            html.Div([
                html.P(
                    "Get a comprehensive summary of all operations across sites with real-time data up to the last computed point in the cloud.",
                    style={"color": "#A0AEC0", "fontSize": "0.85rem", "lineHeight": "1.4", "marginBottom": "1.5rem", "textAlign": "left"}
                ),
                
                html.Ul([
                    html.Li("✅ All sites data aggregated", style={"color": "#A0AEC0", "fontSize": "0.8rem", "marginBottom": "0.3rem"}),
                    html.Li("✅ Real-time statistics", style={"color": "#A0AEC0", "fontSize": "0.8rem", "marginBottom": "0.3rem"}),
                    html.Li("✅ Performance metrics", style={"color": "#A0AEC0", "fontSize": "0.8rem", "marginBottom": "1rem"}),
                ], style={"paddingLeft": "1rem"})
            ]),
            
            # Download Button
            html.A(
                html.Button(
                    ["📥 Download Summary"],
                    style={
                        "width": "100%", "padding": "14px 20px", "backgroundColor": "#DD6B20",
                        "color": "white", "border": "none", "borderRadius": "8px",
                        "fontSize": "1rem", "fontWeight": "600", "cursor": "pointer",
                        "transition": "all 0.3s ease", "minHeight": "48px"
                    }
                ),
                href="/assets/dummy_summary.pdf",  # This will be your dummy PDF path
                download="Summary_Report.pdf",
                style={"textDecoration": "none"}
            ),
            
            # Status
            html.P(
                "📈 Last updated: Just now",
                style={"color": "#68748D", "fontSize": "0.8rem", "marginTop": "1rem", "textAlign": "center"}
            )
        ]
    )

def build_login_layout(theme_name="dark", error_message=""):
    """Enhanced Magic View with 3 options"""
    
    # Get sites data at the top level (like the working version)
    sites = get_sites_from_api()
    dropdown_options = [{"label": site, "value": site} for site in sites]
    
    return html.Div(
        className="portal-container",
        style={
            "minHeight": "100vh",
            "backgroundColor": "#0A0E1A",
            "fontFamily": "'Inter', sans-serif",
            "padding": "2rem 1rem"
        },
        children=[
            # Header
            html.Div(
                className="portal-header",
                style={"textAlign": "center", "marginBottom": "3rem"},
                children=[
                    html.H1(
                        "🎯 Haritha Dashboard Portal",
                        className="portal-title",
                        style={
                            "color": "#FFFFFF", 
                            "fontSize": "2.5rem", 
                            "fontWeight": "800", 
                            "marginBottom": "0.5rem",
                            # Mobile responsive
                            "@media (max-width: 768px)": {
                                "fontSize": "2rem"
                            }
                        }
                    ),
                    html.P(
                        "Choose your access method to continue",
                        className="portal-subtitle", 
                        style={"color": "#A0AEC0", "fontSize": "1.1rem"}
                    )
                ]
            ),
            
            # Error Message (if any)
            html.Div(
                id="error-message-display",
                children=[
                    html.Div(
                        f"⚠️ {error_message}",
                        style={
                            "backgroundColor": "#FED7D7", "color": "#9B2C2C", "padding": "1rem",
                            "borderRadius": "8px", "marginBottom": "2rem", "textAlign": "center",
                            "border": "2px solid #FC8181"
                        }
                    ) if error_message else None
                ]
            ),
            
            # Main Content - 3 Options Grid
            html.Div(
                className="main-grid",
                style={
                    "maxWidth": "1200px",
                    "margin": "0 auto",
                    "display": "grid",
                    "gridTemplateColumns": "repeat(auto-fit, minmax(320px, 1fr))",
                    "gap": "2rem",
                    "marginBottom": "2rem"
                },
                children=[
                    create_magic_view_section(sites, dropdown_options),  # Pass the data
                    create_login_portal_section(),
                    create_quick_summary_section()
                ]
            ),
            
            # Footer
            html.Div(
                style={"textAlign": "center", "marginTop": "3rem"},
                children=[
                    html.A(
                        "← Back to Home",
                        href="/",
                        style={
                            "color": "#A0AEC0", "fontSize": "1rem", "textDecoration": "none",
                            "padding": "0.8rem 1.5rem", "border": "2px solid #2D3748",
                            "borderRadius": "8px", "transition": "all 0.3s ease",
                            "display": "inline-block"
                        }
                    )
                ]
            )
        ]
    )