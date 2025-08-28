# layouts/reports_layout.py
"""
Reports Page Layout with Comprehensive Theme Support
Following themes.py structure with Agency, Cluster, Site, and Date filters
"""

from dash import html, dcc
from datetime import datetime, timedelta
from config.themes import THEMES, DEFAULT_THEME

def create_reports_layout(theme_name=None, user_data=None):
    """
    Create comprehensive reports page layout with filter container
    
    Args:
        theme_name (str): Current theme name
        user_data (dict): User information
        
    Returns:
        html.Div: Complete reports layout
    """
    if theme_name is None:
        theme_name = DEFAULT_THEME
    
    theme = THEMES.get(theme_name, THEMES[DEFAULT_THEME])
    
    return html.Div(
        style={
            'minHeight': '100vh',
            'backgroundColor': theme['primary_bg'],
            'color': theme['text_primary'],
            'fontFamily': 'Inter, sans-serif'
        },
        children=[
            # Page Header
            create_reports_header(theme),
            
            # Filter Container
            create_filter_container(theme),
            
            # Content Area (placeholder for now)
            create_content_area(theme)
        ]
    )

def create_reports_header(theme):
    """Create reports page header section"""
    return html.Div(
        style={
            'background': f"linear-gradient(135deg, {theme['secondary_bg']} 0%, {theme['accent_bg']} 100%)",
            'padding': '2rem',
            'borderBottom': f"1px solid {theme['border_light']}",
            'boxShadow': '0 2px 8px rgba(0, 0, 0, 0.1)'
        },
        children=[
            html.Div(
                style={
                    'maxWidth': '1200px',
                    'margin': '0 auto',
                    'display': 'flex',
                    'justifyContent': 'space-between',
                    'alignItems': 'center'
                },
                children=[
                    # Title Section
                    html.Div([
                        html.H1(
                            "📋 Reports Dashboard",
                            style={
                                'color': theme['text_primary'],
                                'fontSize': '2.5rem',
                                'fontWeight': '700',
                                'margin': '0',
                                'display': 'flex',
                                'alignItems': 'center',
                                'gap': '1rem'
                            }
                        ),
                        html.P(
                            "Generate, view, and manage comprehensive reports",
                            style={
                                'color': theme['text_secondary'],
                                'fontSize': '1.1rem',
                                'margin': '0.5rem 0 0 0',
                                'fontWeight': '400'
                            }
                        )
                    ]),
                    
                    # Status Indicator
                    html.Div([
                        html.Div(
                            "📊 Ready",
                            style={
                                'background': theme['brand_primary'],
                                'color': 'white',
                                'padding': '0.5rem 1rem',
                                'borderRadius': '20px',
                                'fontSize': '0.9rem',
                                'fontWeight': '600'
                            }
                        )
                    ])
                ]
            )
        ]
    )

def create_filter_container(theme):
    """Create filter container section"""
    return html.Div(
        style={
            'backgroundColor': theme['accent_bg'],
            'padding': '1.5rem',
            'borderBottom': f"1px solid {theme['border_light']}"
        },
        children=[
            html.Div(
                style={
                    'maxWidth': '1200px',
                    'margin': '0 auto'
                },
                children=[
                    html.H3(
                        "📝 Report Filters",
                        style={
                            'color': theme['text_primary'],
                            'fontSize': '1.3rem',
                            'marginBottom': '1rem',
                            'fontWeight': '600'
                        }
                    ),
                    html.Div(
                        style={
                            'display': 'grid',
                            'gridTemplateColumns': 'repeat(auto-fit, minmax(200px, 1fr))',
                            'gap': '1rem',
                            'alignItems': 'end'
                        },
                        children=[
                            # Report Type Filter
                            html.Div([
                                html.Label(
                                    "Report Type:",
                                    style={
                                        'color': theme['text_secondary'],
                                        'fontSize': '0.9rem',
                                        'fontWeight': '500',
                                        'marginBottom': '0.5rem',
                                        'display': 'block'
                                    }
                                ),
                                dcc.Dropdown(
                                    id='reports-type-filter',
                                    options=[
                                        {'label': 'All Reports', 'value': 'all'},
                                        {'label': 'Monthly Summary', 'value': 'monthly'},
                                        {'label': 'Weekly Progress', 'value': 'weekly'},
                                        {'label': 'Daily Operations', 'value': 'daily'},
                                        {'label': 'Custom Reports', 'value': 'custom'}
                                    ],
                                    value='all',
                                    style={
                                        'backgroundColor': theme['card_bg'],
                                        'color': theme['text_primary']
                                    }
                                )
                            ]),
                            
                            # Agency Filter
                            html.Div([
                                html.Label(
                                    "Agency:",
                                    style={
                                        'color': theme['text_secondary'],
                                        'fontSize': '0.9rem',
                                        'fontWeight': '500',
                                        'marginBottom': '0.5rem',
                                        'display': 'block'
                                    }
                                ),
                                dcc.Dropdown(
                                    id='reports-agency-filter',
                                    options=[
                                        {'label': 'All Agencies', 'value': 'all'},
                                        {'label': 'Municipal Corporation', 'value': 'municipal'},
                                        {'label': 'Panchayat Raj', 'value': 'panchayat'},
                                        {'label': 'Urban Development', 'value': 'urban'}
                                    ],
                                    value='all',
                                    style={
                                        'backgroundColor': theme['card_bg'],
                                        'color': theme['text_primary']
                                    }
                                )
                            ]),
                            
                            # Date Range Filter
                            html.Div([
                                html.Label(
                                    "Date Range:",
                                    style={
                                        'color': theme['text_secondary'],
                                        'fontSize': '0.9rem',
                                        'fontWeight': '500',
                                        'marginBottom': '0.5rem',
                                        'display': 'block'
                                    }
                                ),
                                dcc.DatePickerRange(
                                    id='reports-date-filter',
                                    start_date=datetime.now() - timedelta(days=30),
                                    end_date=datetime.now(),
                                    style={
                                        'backgroundColor': theme['card_bg']
                                    }
                                )
                            ]),
                            
                            # Generate Button
                            html.Div([
                                html.Button(
                                    "📊 Generate Report",
                                    id='reports-generate-btn',
                                    style={
                                        'backgroundColor': theme['brand_primary'],
                                        'color': 'white',
                                        'border': 'none',
                                        'padding': '0.75rem 1.5rem',
                                        'borderRadius': '6px',
                                        'fontSize': '0.9rem',
                                        'fontWeight': '600',
                                        'cursor': 'pointer',
                                        'width': '100%'
                                    }
                                )
                            ])
                        ]
                    )
                ]
            )
        ]
    )

def create_content_area(theme):
    """Create main content area"""
    return html.Div(
        style={
            'maxWidth': '1200px',
            'margin': '0 auto',
            'padding': '2rem'
        },
        children=[
            # Welcome Section
            html.Div(
                style={
                    'background': f"linear-gradient(135deg, {theme['accent_bg']} 0%, {theme['card_bg']} 100%)",
                    'padding': '2rem',
                    'borderRadius': '12px',
                    'marginBottom': '2rem',
                    'border': f"1px solid {theme['border_light']}",
                    'textAlign': 'center'
                },
                children=[
                    html.H2(
                        "👋 Hi! Welcome to Reports",
                        style={
                            'color': theme['text_primary'],
                            'fontSize': '1.8rem',
                            'fontWeight': '600',
                            'marginBottom': '1rem'
                        }
                    ),
                    html.P(
                        "Your comprehensive reports dashboard is ready. Use the filters above to generate detailed reports on waste management activities.",
                        style={
                            'color': theme['text_secondary'],
                            'fontSize': '1.1rem',
                            'lineHeight': '1.6',
                            'maxWidth': '600px',
                            'margin': '0 auto'
                        }
                    )
                ]
            ),
            
            # Reports Grid
            html.Div(
                style={
                    'display': 'grid',
                    'gridTemplateColumns': 'repeat(auto-fit, minmax(300px, 1fr))',
                    'gap': '1.5rem',
                    'marginBottom': '2rem'
                },
                children=[
                    create_report_card(
                        "📊 Summary Reports",
                        "Comprehensive overview of operations",
                        ["Monthly collections summary", "Performance metrics", "Efficiency indicators"],
                        theme
                    ),
                    create_report_card(
                        "📈 Trend Analysis",
                        "Historical data and patterns",
                        ["Quarterly trends", "Year-over-year comparison", "Seasonal variations"],
                        theme
                    ),
                    create_report_card(
                        "🎯 Compliance Reports",
                        "Regulatory and compliance tracking",
                        ["Environmental compliance", "Safety standards", "Quality metrics"],
                        theme
                    )
                ]
            ),
            
            # Available Reports List
            html.Div(
                style={
                    'backgroundColor': theme['card_bg'],
                    'padding': '2rem',
                    'borderRadius': '12px',
                    'border': f"1px solid {theme['border_light']}"
                },
                children=[
                    html.H3(
                        "📋 Available Reports",
                        style={
                            'color': theme['text_primary'],
                            'marginBottom': '1.5rem',
                            'fontSize': '1.4rem',
                            'fontWeight': '600'
                        }
                    ),
                    html.Div(
                        style={
                            'display': 'grid',
                            'gridTemplateColumns': 'repeat(auto-fit, minmax(250px, 1fr))',
                            'gap': '1rem'
                        },
                        children=[
                            create_report_item("Daily Operations Report", "Today's activities and metrics", "Updated 2 hours ago", theme),
                            create_report_item("Weekly Summary", "7-day performance overview", "Updated yesterday", theme),
                            create_report_item("Monthly Dashboard", "Comprehensive monthly analysis", "Updated 3 days ago", theme),
                            create_report_item("Quarterly Review", "Strategic performance review", "Updated last week", theme)
                        ]
                    )
                ]
            )
        ]
    )

def create_report_card(title, description, features, theme):
    """Create a report category card component"""
    return html.Div(
        style={
            'backgroundColor': theme['card_bg'],
            'padding': '1.5rem',
            'borderRadius': '12px',
            'border': f"1px solid {theme['border_light']}",
            'boxShadow': '0 2px 4px rgba(0, 0, 0, 0.1)'
        },
        children=[
            html.H4(
                title,
                style={
                    'color': theme['text_primary'],
                    'fontSize': '1.2rem',
                    'fontWeight': '600',
                    'marginBottom': '0.5rem'
                }
            ),
            html.P(
                description,
                style={
                    'color': theme['text_secondary'],
                    'fontSize': '0.9rem',
                    'marginBottom': '1rem',
                    'lineHeight': '1.4'
                }
            ),
            html.Div([
                html.P(
                    f"• {feature}",
                    style={
                        'color': theme['text_primary'],
                        'fontSize': '0.85rem',
                        'margin': '0.25rem 0',
                        'fontWeight': '400'
                    }
                ) for feature in features
            ])
        ]
    )

def create_report_item(title, description, last_updated, theme):
    """Create a report item component"""
    return html.Div(
        style={
            'backgroundColor': theme['accent_bg'],
            'padding': '1rem',
            'borderRadius': '8px',
            'border': f"1px solid {theme['border_light']}",
            'cursor': 'pointer',
            'transition': 'transform 0.2s ease'
        },
        children=[
            html.H5(
                title,
                style={
                    'color': theme['text_primary'],
                    'fontSize': '1rem',
                    'fontWeight': '600',
                    'marginBottom': '0.5rem'
                }
            ),
            html.P(
                description,
                style={
                    'color': theme['text_secondary'],
                    'fontSize': '0.85rem',
                    'marginBottom': '0.5rem',
                    'lineHeight': '1.3'
                }
            ),
            html.P(
                last_updated,
                style={
                    'color': theme['brand_primary'],
                    'fontSize': '0.75rem',
                    'fontWeight': '500',
                    'margin': '0'
                }
            )
        ]
    )