# layouts/site_dashboard.py - SIMPLIFIED Site Dashboard
"""
Site-specific Dashboard Layout - Simplified Version
Uses basic colors, no complex theming needed
"""

from dash import html, dcc

def build_site_dashboard_layout(theme_name="dark", site_name="Unknown Site"):
    """
    Build a simple pretty dashboard layout for the selected site
    
    Args:
        theme_name (str): Current theme name (ignored, using fixed colors)
        site_name (str): Selected site name
        
    Returns:
        html.Div: Complete site dashboard layout
    """
    
    return html.Div(
        className="site-dashboard-layout",
        style={
            "minHeight": "100vh",
            "backgroundColor": "#0A0E1A",
            "color": "#FFFFFF",
            "fontFamily": "'Inter', sans-serif"
        },
        children=[
            # Header Section
            html.Div(
                className="dashboard-header",
                style={
                    "background": "linear-gradient(135deg, #eb9534 0%, #1A1F2E 100%)",
                    "padding": "2rem 1rem",
                    "marginBottom": "2rem",
                    "borderRadius": "0 0 20px 20px",
                    "boxShadow": "0 10px 30px rgba(0, 0, 0, 0.3)"
                },
                children=[
                    html.Div(
                        style={"maxWidth": "1200px", "margin": "0 auto", "textAlign": "center"},
                        children=[
                            html.H1(
                                f"🏢 {site_name} Dashboard",
                                style={
                                    "color": "white",
                                    "fontSize": "2.5rem",
                                    "fontWeight": "800",
                                    "marginBottom": "0.5rem",
                                    "textShadow": "0 2px 4px rgba(0, 0, 0, 0.3)"
                                }
                            ),
                            html.P(
                                "Real-time operations and analytics dashboard",
                                style={
                                    "color": "rgba(255, 255, 255, 0.9)",
                                    "fontSize": "1.2rem",
                                    "marginBottom": "1rem"
                                }
                            ),
                            # Navigation back to Magic View
                            html.Button(
                                [html.Span("← "), "Back to Magic View"],
                                id="back-to-magic-view-btn",
                                style={
                                    "backgroundColor": "rgba(255, 255, 255, 0.2)",
                                    "border": "2px solid rgba(255, 255, 255, 0.3)",
                                    "color": "white",
                                    "padding": "0.8rem 1.5rem",
                                    "borderRadius": "10px",
                                    "fontSize": "1rem",
                                    "fontWeight": "600",
                                    "cursor": "pointer",
                                    "transition": "all 0.3s ease"
                                }
                            )
                        ]
                    )
                ]
            ),
            
            # Main Dashboard Content
            html.Div(
                className="dashboard-content",
                style={
                    "maxWidth": "1200px",
                    "margin": "0 auto",
                    "padding": "0 1rem"
                },
                children=[
                    # Welcome Section
                    html.Div(
                        style={
                            "backgroundColor": "#2D3748",
                            "borderRadius": "16px",
                            "padding": "2.5rem",
                            "marginBottom": "2rem",
                            "border": "2px solid #1A1F2E",
                            "boxShadow": "0 8px 25px rgba(0, 0, 0, 0.15)",
                            "textAlign": "center"
                        },
                        children=[
                            html.Div("🌟", style={"fontSize": "4rem", "marginBottom": "1rem"}),
                            html.H2(
                                f"Welcome to {site_name}",
                                style={
                                    "color": "#FFFFFF",
                                    "fontSize": "2rem",
                                    "fontWeight": "700",
                                    "marginBottom": "1rem"
                                }
                            ),
                            html.P(
                                "This is your beautiful site dashboard! Here you'll be able to view all the operational data, "
                                "analytics, and insights for this location. The dashboard will be fully integrated with the "
                                "weighbridge API to provide real-time data visualization.",
                                style={
                                    "color": "#A0AEC0",
                                    "fontSize": "1.1rem",
                                    "lineHeight": "1.6",
                                    "maxWidth": "600px",
                                    "margin": "0 auto"
                                }
                            )
                        ]
                    ),
                    
                    # Feature Cards Grid
                    html.Div(
                        className="features-grid",
                        style={
                            "display": "grid",
                            "gridTemplateColumns": "repeat(auto-fit, minmax(280px, 1fr))",
                            "gap": "1.5rem",
                            "marginBottom": "2rem"
                        },
                        children=[
                            # Card 1: Real-time Data
                            create_feature_card(
                                "📊",
                                "Real-time Monitoring",
                                "Live updates from weighbridge operations with instant data synchronization.",
                                "#eb9534"
                            ),
                            
                            # Card 2: Analytics
                            create_feature_card(
                                "📈",
                                "Advanced Analytics",
                                "Deep insights into operational patterns, trends, and performance metrics.",
                                "#38A169"
                            ),
                            
                            # Card 3: Reports
                            create_feature_card(
                                "📋",
                                "Smart Reports",
                                "Automated report generation with customizable views and export options.",
                                "#DD6B20"
                            ),
                            
                            # Card 4: Integration
                            create_feature_card(
                                "🔗",
                                "API Integration",
                                "Seamlessly connected to weighbridge systems for unified data management.",
                                "#E53E3E"
                            )
                        ]
                    ),
                    
                    # Status Section
                    html.Div(
                        style={
                            "backgroundColor": "#2D3748",
                            "borderRadius": "12px",
                            "padding": "2rem",
                            "border": "1px solid #1A1F2E",
                            "textAlign": "center",
                            "marginBottom": "3rem"
                        },
                        children=[
                            html.H3(
                                "🚀 Dashboard Status",
                                style={
                                    "color": "#FFFFFF",
                                    "fontSize": "1.5rem",
                                    "marginBottom": "1rem"
                                }
                            ),
                            html.Div(
                                style={"display": "flex", "justifyContent": "center", "gap": "2rem", "flexWrap": "wrap"},
                                children=[
                                    create_status_item("✅", "System Status", "Online"),
                                    create_status_item("📡", "API Connection", "Connected"),
                                    create_status_item("🔄", "Last Update", "Just now"),
                                    create_status_item("📍", "Location", site_name)
                                ]
                            )
                        ]
                    )
                ]
            )
        ]
    )

def create_feature_card(icon, title, description, accent_color):
    """Create a feature card with consistent styling"""
    return html.Div(
        style={
            "backgroundColor": "#2D3748",
            "borderRadius": "12px",
            "padding": "1.5rem",
            "border": f"2px solid {accent_color}20",
            "boxShadow": "0 4px 15px rgba(0, 0, 0, 0.1)",
            "transition": "all 0.3s ease",
            "position": "relative",
            "overflow": "hidden"
        },
        children=[
            # Accent line
            html.Div(
                style={
                    "position": "absolute",
                    "top": "0",
                    "left": "0",
                    "right": "0",
                    "height": "4px",
                    "background": accent_color
                }
            ),
            html.Div(icon, style={"fontSize": "2.5rem", "marginBottom": "1rem"}),
            html.H4(
                title,
                style={
                    "color": "#FFFFFF",
                    "fontSize": "1.3rem",
                    "fontWeight": "600",
                    "marginBottom": "0.5rem"
                }
            ),
            html.P(
                description,
                style={
                    "color": "#A0AEC0",
                    "fontSize": "0.95rem",
                    "lineHeight": "1.5",
                    "margin": "0"
                }
            )
        ]
    )

def create_status_item(icon, label, value):
    """Create a status item with icon, label, and value"""
    return html.Div(
        style={"textAlign": "center"},
        children=[
            html.Div(icon, style={"fontSize": "1.5rem", "marginBottom": "0.5rem"}),
            html.Div(label, style={
                "color": "#A0AEC0", 
                "fontSize": "0.8rem",
                "fontWeight": "500"
            }),
            html.Div(value, style={
                "color": "#FFFFFF", 
                "fontSize": "1rem",
                "fontWeight": "600"
            })
        ]
    )