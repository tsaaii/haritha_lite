# layouts/analytics_layout.py
"""
Analytics Page Layout with Comprehensive Theme Support
Following themes.py structure with Agency, Cluster, Site, and Date filters
"""

from dash import html, dcc
from datetime import datetime, timedelta
from config.themes import THEMES, DEFAULT_THEME

def create_analytics_layout(theme_name=None, user_data=None):
    """
    Create comprehensive analytics page layout with filter container
    
    Args:
        theme_name (str): Current theme name
        user_data (dict): User information
        
    Returns:
        html.Div: Complete analytics layout
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
            create_analytics_header(theme),
            
            # Filter Container
            create_filter_container(theme),
            
            # Content Area (placeholder for now)
            create_content_area(theme)
        ]
    )

def create_analytics_header(theme):
    """Create analytics page header section"""
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
                            "📈 Analytics Dashboard",
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
                            "Real-time data analytics and insights",
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
                            "🟢 Live Data",
                            style={
                                'background': theme['success'],
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
                        "🔍 Data Filters",
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
                                    id='analytics-agency-filter',
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
                            
                            # Cluster Filter
                            html.Div([
                                html.Label(
                                    "Cluster:",
                                    style={
                                        'color': theme['text_secondary'],
                                        'fontSize': '0.9rem',
                                        'fontWeight': '500',
                                        'marginBottom': '0.5rem',
                                        'display': 'block'
                                    }
                                ),
                                dcc.Dropdown(
                                    id='analytics-cluster-filter',
                                    options=[
                                        {'label': 'All Clusters', 'value': 'all'},
                                        {'label': 'North Region', 'value': 'north'},
                                        {'label': 'South Region', 'value': 'south'},
                                        {'label': 'Central Region', 'value': 'central'}
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
                                    id='analytics-date-filter',
                                    start_date=datetime.now() - timedelta(days=30),
                                    end_date=datetime.now(),
                                    style={
                                        'backgroundColor': theme['card_bg']
                                    }
                                )
                            ]),
                            
                            # Apply Button
                            html.Div([
                                html.Button(
                                    "📊 Apply Filters",
                                    id='analytics-apply-filters',
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
                        "👋 Hi! Welcome to Analytics",
                        style={
                            'color': theme['text_primary'],
                            'fontSize': '1.8rem',
                            'fontWeight': '600',
                            'marginBottom': '1rem'
                        }
                    ),
                    html.P(
                        "Your comprehensive analytics dashboard is ready. Use the filters above to explore waste management data, trends, and insights.",
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
            
            # Analytics Cards Grid
            html.Div(
                style={
                    'display': 'grid',
                    'gridTemplateColumns': 'repeat(auto-fit, minmax(300px, 1fr))',
                    'gap': '1.5rem',
                    'marginBottom': '2rem'
                },
                children=[
                    create_analytics_card(
                        "📊 Data Overview",
                        "Real-time waste collection and processing metrics",
                        ["Active sites: 142", "Daily collections: 1,250 tons", "Processing efficiency: 94%"],
                        theme
                    ),
                    create_analytics_card(
                        "📈 Trends",
                        "Weekly and monthly performance trends",
                        ["Collection up 12%", "Processing efficiency +3%", "Customer satisfaction: 4.8/5"],
                        theme
                    ),
                    create_analytics_card(
                        "🎯 Targets",
                        "Progress toward sustainability goals",
                        ["Recycling rate: 76%", "Waste reduction: 18%", "Carbon footprint: -15%"],
                        theme
                    )
                ]
            ),
            
            # Data Table Placeholder
            html.Div(
                style={
                    'backgroundColor': theme['card_bg'],
                    'padding': '2rem',
                    'borderRadius': '12px',
                    'border': f"1px solid {theme['border_light']}",
                    'textAlign': 'center'
                },
                children=[
                    html.H3(
                        "📋 Data Table",
                        style={
                            'color': theme['text_primary'],
                            'marginBottom': '1rem'
                        }
                    ),
                    html.P(
                        "Interactive data table will appear here when filters are applied",
                        style={
                            'color': theme['text_secondary'],
                            'fontSize': '1rem'
                        }
                    )
                ]
            )
        ]
    )

def create_analytics_card(title, description, metrics, theme):
    """Create an analytics card component"""
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
                    metric,
                    style={
                        'color': theme['success'] if any(char in metric for char in ['+', '↑']) else theme['text_primary'],
                        'fontSize': '0.9rem',
                        'margin': '0.25rem 0',
                        'fontWeight': '500'
                    }
                ) for metric in metrics
            ])
        ]
    )