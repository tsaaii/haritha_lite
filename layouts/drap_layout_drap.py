# layouts/drap_layout_drap.py
"""
DRAP Endpoint Layouts
- Login page (with excavator loading animation)
- Dashboard page
Compatible with Dash 3.2.0 (no dangerouslySetInnerHTML)
"""

from dash import html, dcc
from config.themes import THEMES, DEFAULT_THEME


def get_drap_theme(theme_name=None):
    """Get theme configuration"""
    if theme_name is None:
        theme_name = DEFAULT_THEME
    return THEMES.get(theme_name, THEMES[DEFAULT_THEME])


def build_drap_login_layout(theme_name="dark", error_message=""):
    """
    Build the DRAP login page with excavator loading animation.
    Uses dcc.Interval + callback to hide loader after 2 seconds.
    """
    theme = get_drap_theme(theme_name)
    accent = theme.get("brand_primary", "#eb9534")
    bg = theme.get("primary_bg", "#0D1B2A")
    
    return html.Div([
        # Interval to trigger loader hide
        dcc.Interval(
            id='drap-loader-interval',
            interval=2000,
            n_intervals=0,
            max_intervals=1
        ),
        
        # ========== EXCAVATOR LOADING SCREEN ==========
        html.Div(
            id="drap-loading-screen",
            style={
                "position": "fixed",
                "top": "0",
                "left": "0",
                "width": "100%",
                "height": "100%",
                "background": f"linear-gradient(135deg, {bg} 0%, #1A1F2E 100%)",
                "display": "flex",
                "justifyContent": "center",
                "alignItems": "center",
                "zIndex": "9999",
                "opacity": "1",
                "transition": "opacity 0.8s ease"
            },
            children=[
                html.Div(
                    style={"textAlign": "center"},
                    children=[
                        # Animation container
                        html.Div(
                            style={
                                "position": "relative",
                                "width": "280px",
                                "height": "120px",
                                "margin": "0 auto 1.5rem",
                                "overflow": "hidden"
                            },
                            children=[
                                # Waste pile (left side - shrinks)
                                html.Div(
                                    "🗑️",
                                    id="drap-waste-pile",
                                    style={
                                        "position": "absolute",
                                        "left": "20px",
                                        "top": "30px",
                                        "fontSize": "3rem"
                                    }
                                ),
                                # Dust particles behind excavator
                                html.Div(
                                    id="drap-dust-particles",
                                    style={
                                        "position": "absolute",
                                        "left": "100px",
                                        "top": "50px",
                                        "fontSize": "1rem",
                                        "color": "#8B7355"
                                    },
                                    children=[
                                        html.Span("•", style={"marginRight": "2px"}),
                                        html.Span("•", style={"marginRight": "2px"}),
                                        html.Span("•"),
                                    ]
                                ),
                                # Moving excavator
                                html.Div(
                                    "🚜",
                                    id="drap-excavator-icon",
                                    style={
                                        "position": "absolute",
                                        "left": "50%",
                                        "top": "35px",
                                        "fontSize": "4rem",
                                        "transform": "translateX(-50%)",
                                        "zIndex": "10"
                                    }
                                ),
                                # Clean land (right side - grows)
                                html.Div(
                                    "🌱",
                                    id="drap-clean-land",
                                    style={
                                        "position": "absolute",
                                        "right": "20px",
                                        "top": "35px",
                                        "fontSize": "2.5rem"
                                    }
                                ),
                                # Ground/track line
                                html.Div(
                                    id="drap-track-line",
                                    style={
                                        "position": "absolute",
                                        "bottom": "15px",
                                        "left": "0",
                                        "right": "0",
                                        "height": "8px",
                                        "background": f"linear-gradient(90deg, #8B4513 0%, {accent} 50%, #228B22 100%)",
                                        "borderRadius": "4px"
                                    }
                                )
                            ]
                        ),
                        # Text
                        html.Div("Remediation in Progress", style={
                            "fontSize": "1.5rem",
                            "fontWeight": "700",
                            "color": accent,
                            "marginBottom": "0.5rem"
                        }),
                        html.Div("Loading DRAP Portal...", className="loading-text", style={
                            "fontSize": "1rem",
                            "color": "#A0AEC0"
                        }),
                        # Progress bar
                        html.Div(
                            style={
                                "width": "200px",
                                "height": "4px",
                                "backgroundColor": "#333",
                                "borderRadius": "2px",
                                "margin": "1.5rem auto 0",
                                "overflow": "hidden"
                            },
                            children=[
                                html.Div(
                                    id="drap-progress-bar",
                                    style={
                                        "height": "100%",
                                        "width": "30%",
                                        "backgroundColor": accent,
                                        "borderRadius": "2px"
                                    }
                                )
                            ]
                        )
                    ]
                )
            ]
        ),
        
        # ========== LOGIN PAGE CONTENT ==========
        html.Div(
            style={
                "minHeight": "100vh",
                "display": "flex",
                "justifyContent": "center",
                "alignItems": "center",
                "padding": "2rem",
                "backgroundColor": bg,
                "fontFamily": "'Inter', -apple-system, sans-serif"
            },
            children=[
                html.Div(
                    style={
                        "width": "100%",
                        "maxWidth": "420px",
                        "backgroundColor": theme.get("card_bg", "#1B263B"),
                        "borderRadius": "16px",
                        "border": f"2px solid {theme.get('accent_bg', '#415A77')}",
                        "boxShadow": "0 20px 60px rgba(0, 0, 0, 0.4)",
                        "padding": "2.5rem"
                    },
                    children=[
                        html.Div("🔐", style={"fontSize": "3.5rem", "textAlign": "center", "marginBottom": "1rem"}),
                        html.H2("DRAP Portal", style={
                            "color": accent,
                            "fontSize": "1.75rem",
                            "fontWeight": "700",
                            "textAlign": "center",
                            "marginBottom": "0.5rem"
                        }),
                        html.P("Sign in to access the dashboard", style={
                            "color": theme.get("text_secondary", "#778DA9"),
                            "fontSize": "0.95rem",
                            "textAlign": "center",
                            "marginBottom": "2rem"
                        }),
                        
                        html.Div(id="drap-login-error", style={"display": "none"}),
                        
                        html.Div(style={"marginBottom": "1.25rem"}, children=[
                            html.Label("Username", style={
                                "color": theme.get("text_primary", "#E0E1DD"),
                                "fontSize": "0.9rem",
                                "fontWeight": "600",
                                "display": "block",
                                "marginBottom": "0.5rem"
                            }),
                            dcc.Input(
                                id="drap-username-input",
                                type="text",
                                placeholder="Enter username",
                                style={
                                    "width": "100%",
                                    "padding": "12px 16px",
                                    "borderRadius": "8px",
                                    "border": f"2px solid {theme.get('accent_bg', '#415A77')}",
                                    "backgroundColor": bg,
                                    "color": theme.get("text_primary", "#E0E1DD"),
                                    "fontSize": "1rem",
                                    "boxSizing": "border-box"
                                }
                            )
                        ]),
                        
                        html.Div(style={"marginBottom": "1.5rem"}, children=[
                            html.Label("Password", style={
                                "color": theme.get("text_primary", "#E0E1DD"),
                                "fontSize": "0.9rem",
                                "fontWeight": "600",
                                "display": "block",
                                "marginBottom": "0.5rem"
                            }),
                            dcc.Input(
                                id="drap-password-input",
                                type="password",
                                placeholder="Enter password",
                                style={
                                    "width": "100%",
                                    "padding": "12px 16px",
                                    "borderRadius": "8px",
                                    "border": f"2px solid {theme.get('accent_bg', '#415A77')}",
                                    "backgroundColor": bg,
                                    "color": theme.get("text_primary", "#E0E1DD"),
                                    "fontSize": "1rem",
                                    "boxSizing": "border-box"
                                }
                            )
                        ]),
                        
                        html.Button("Sign In →", id="drap-login-button", style={
                            "width": "100%",
                            "padding": "14px",
                            "backgroundColor": accent,
                            "color": "#FFFFFF",
                            "border": "none",
                            "borderRadius": "8px",
                            "fontSize": "1rem",
                            "fontWeight": "600",
                            "cursor": "pointer"
                        }),
                        
                        html.Div(style={"textAlign": "center", "marginTop": "1.5rem"}, children=[
                            html.A("← Back to Main Dashboard", href="/", style={
                                "color": theme.get("text_secondary", "#778DA9"),
                                "fontSize": "0.9rem",
                                "textDecoration": "none"
                            })
                        ]),
                        
                        html.Div(style={
                            "marginTop": "1.5rem",
                            "padding": "1rem",
                            "backgroundColor": "#3182CE15",
                            "borderRadius": "8px",
                            "textAlign": "center"
                        }, children=[
                            html.P("Demo: drap_admin / drap@2024", style={
                                "color": theme.get("text_secondary", "#778DA9"),
                                "fontSize": "0.8rem",
                                "margin": "0",
                                "fontFamily": "monospace"
                            })
                        ])
                    ]
                )
            ]
        )
    ])


def build_drap_dashboard_layout(theme_name="dark", user_data=None):
    """Build the DRAP dashboard"""
    theme = get_drap_theme(theme_name)
    user_data = user_data or {}
    username = user_data.get('username', 'User')
    accent = theme.get("brand_primary", "#eb9534")
    
    return html.Div(
        style={
            "minHeight": "100vh",
            "backgroundColor": theme.get("primary_bg", "#0D1B2A"),
            "fontFamily": "'Inter', -apple-system, sans-serif"
        },
        children=[
            html.Div(
                style={
                    "backgroundColor": theme.get("secondary_bg", "#1B263B"),
                    "borderBottom": f"2px solid {theme.get('accent_bg', '#415A77')}",
                    "padding": "1rem 2rem",
                    "display": "flex",
                    "justifyContent": "space-between",
                    "alignItems": "center"
                },
                children=[
                    html.Div(style={"display": "flex", "alignItems": "center", "gap": "1rem"}, children=[
                        html.Span("📊", style={"fontSize": "2rem"}),
                        html.H1("DRAP Dashboard", style={
                            "color": accent,
                            "fontSize": "1.5rem",
                            "fontWeight": "700",
                            "margin": "0"
                        })
                    ]),
                    html.Div(style={"display": "flex", "alignItems": "center", "gap": "1rem"}, children=[
                        html.Span(f"👤 {username}", style={
                            "color": theme.get("text_primary", "#E0E1DD"),
                            "fontSize": "0.95rem"
                        }),
                        html.A("Logout", href="/DRAP/logout", style={
                            "backgroundColor": theme.get("error", "#E53E3E"),
                            "color": "#FFFFFF",
                            "padding": "0.5rem 1.25rem",
                            "borderRadius": "6px",
                            "textDecoration": "none",
                            "fontSize": "0.9rem",
                            "fontWeight": "500"
                        })
                    ])
                ]
            ),
            
            html.Div(style={"padding": "2rem"}, children=[
                html.Div(
                    style={
                        "backgroundColor": theme.get("card_bg", "#1B263B"),
                        "borderRadius": "12px",
                        "border": f"2px solid {theme.get('success', '#38A169')}",
                        "padding": "1.5rem 2rem",
                        "marginBottom": "2rem",
                        "display": "flex",
                        "alignItems": "center",
                        "gap": "1rem"
                    },
                    children=[
                        html.Span("✅", style={"fontSize": "2rem"}),
                        html.Div([
                            html.H2(f"Welcome back, {username}!", style={
                                "color": theme.get("success", "#38A169"),
                                "fontSize": "1.25rem",
                                "fontWeight": "600",
                                "margin": "0 0 0.25rem 0"
                            }),
                            html.P("You are logged into the DRAP Portal", style={
                                "color": theme.get("text_secondary", "#778DA9"),
                                "fontSize": "0.9rem",
                                "margin": "0"
                            })
                        ])
                    ]
                ),
                
                html.Div(
                    style={
                        "display": "grid",
                        "gridTemplateColumns": "repeat(auto-fit, minmax(250px, 1fr))",
                        "gap": "1.5rem",
                        "marginBottom": "2rem"
                    },
                    children=[
                        _stat_card("Total Records", "--", "📁", theme),
                        _stat_card("Active Sites", "--", "🏗️", theme, theme.get("success")),
                        _stat_card("Pending Tasks", "--", "📋", theme, theme.get("warning")),
                        _stat_card("Completion", "--%", "📈", theme, theme.get("info")),
                    ]
                ),
                
                html.Div(
                    style={"display": "grid", "gridTemplateColumns": "2fr 1fr", "gap": "1.5rem"},
                    children=[
                        html.Div(
                            style={
                                "backgroundColor": theme.get("card_bg", "#1B263B"),
                                "borderRadius": "12px",
                                "border": f"1px solid {theme.get('accent_bg', '#415A77')}",
                                "padding": "1.5rem",
                                "minHeight": "400px"
                            },
                            children=[
                                html.H3("📊 Data Overview", style={
                                    "color": theme.get("text_primary", "#E0E1DD"),
                                    "fontSize": "1.1rem",
                                    "marginBottom": "1rem",
                                    "paddingBottom": "0.75rem",
                                    "borderBottom": f"1px solid {theme.get('accent_bg', '#415A77')}"
                                }),
                                html.Div(
                                    style={
                                        "display": "flex",
                                        "justifyContent": "center",
                                        "alignItems": "center",
                                        "height": "300px",
                                        "backgroundColor": theme.get("primary_bg"),
                                        "borderRadius": "8px",
                                        "border": f"2px dashed {theme.get('accent_bg', '#415A77')}"
                                    },
                                    children=[html.P("Data tables and charts will appear here", style={"color": theme.get("text_secondary")})]
                                )
                            ]
                        ),
                        html.Div(
                            style={
                                "backgroundColor": theme.get("card_bg", "#1B263B"),
                                "borderRadius": "12px",
                                "border": f"1px solid {theme.get('accent_bg', '#415A77')}",
                                "padding": "1.5rem"
                            },
                            children=[
                                html.H3("⚡ Quick Actions", style={
                                    "color": theme.get("text_primary", "#E0E1DD"),
                                    "fontSize": "1.1rem",
                                    "marginBottom": "1rem",
                                    "paddingBottom": "0.75rem",
                                    "borderBottom": f"1px solid {theme.get('accent_bg', '#415A77')}"
                                }),
                                html.Div(style={"display": "flex", "flexDirection": "column", "gap": "0.75rem"}, children=[
                                    _action_btn("📤 Upload Data", theme),
                                    _action_btn("📊 Generate Report", theme),
                                    _action_btn("⚙️ Settings", theme),
                                    html.A("🏠 Main Dashboard", href="/", style={
                                        "display": "block",
                                        "padding": "0.875rem",
                                        "backgroundColor": theme.get("primary_bg"),
                                        "color": theme.get("text_secondary"),
                                        "border": f"1px solid {theme.get('accent_bg')}",
                                        "borderRadius": "8px",
                                        "textDecoration": "none",
                                        "fontSize": "0.9rem"
                                    })
                                ])
                            ]
                        )
                    ]
                )
            ])
        ]
    )


def _stat_card(title, value, icon, theme, color=None):
    return html.Div(
        style={
            "backgroundColor": theme.get("card_bg", "#1B263B"),
            "borderRadius": "12px",
            "border": f"1px solid {theme.get('accent_bg', '#415A77')}",
            "padding": "1.5rem"
        },
        children=[
            html.Div(style={"display": "flex", "justifyContent": "space-between", "alignItems": "center"}, children=[
                html.Div([
                    html.P(title, style={"color": theme.get("text_secondary"), "fontSize": "0.85rem", "margin": "0 0 0.5rem 0"}),
                    html.H3(value, style={"color": color or theme.get("text_primary"), "fontSize": "2rem", "fontWeight": "700", "margin": "0"})
                ]),
                html.Span(icon, style={"fontSize": "2.5rem", "opacity": "0.7"})
            ])
        ]
    )


def _action_btn(text, theme):
    return html.Button(text, style={
        "width": "100%",
        "padding": "0.875rem",
        "backgroundColor": theme.get("accent_bg", "#415A77"),
        "color": theme.get("text_primary", "#E0E1DD"),
        "border": "none",
        "borderRadius": "8px",
        "fontSize": "0.9rem",
        "fontWeight": "500",
        "cursor": "pointer",
        "textAlign": "left"
    })