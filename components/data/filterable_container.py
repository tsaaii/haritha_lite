# components/data/filterable_container.py
"""
Filterable Data Container Component for Swaccha Andhra Dashboard
Advanced filtering capabilities with real-time search and data visualization
"""

from dash import html, dcc, callback, Input, Output, State, dash_table
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

def load_sample_waste_data():
    """Load sample waste management data for filtering"""
    try:
        # Try to load real data first
        df = pd.read_csv('waste_management_data_20250606_004558.csv')
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df['Net Weight'] = pd.to_numeric(df['Net Weight'], errors='coerce')
        df['Loaded Weight'] = pd.to_numeric(df['Loaded Weight'], errors='coerce')
        df['Empty Weight'] = pd.to_numeric(df['Empty Weight'], errors='coerce')
        df = df.dropna(subset=['Date', 'source_location'])
        
        # Add cluster info
        cluster_mapping = {
            'Nellore Municipal Corporation': ['allipuram', 'donthalli'],
            'Chittor': ['kuppam', 'palamaner', 'madanapalle'],
            'Tirupathi': ['tpty'],
            'GVMC': ['vizagsac'],
            'Kurnool': ['Kurnool'],
            'Nandyal': ['Nandyal'],
            'Ongole': ['Ongole']
        }
        
        def get_cluster(site):
            for cluster, sites in cluster_mapping.items():
                if site in sites:
                    return cluster
            return 'Other'
        
        df['Cluster'] = df['source_location'].apply(get_cluster)
        df['Status'] = df.apply(lambda x: 'Completed' if x['Net Weight'] > 0 else 'Pending', axis=1)
        df['Priority'] = df.apply(lambda x: 'High' if x['Net Weight'] > 3000 else 'Medium' if x['Net Weight'] > 1500 else 'Low', axis=1)
        
        logger.info(f"Loaded {len(df)} real waste management records")
        return df
        
    except Exception as e:
        logger.warning(f"Could not load real data: {e}, creating sample data")
        return create_sample_filterable_data()

def create_sample_filterable_data():
    """Create comprehensive sample data for filtering demonstration"""
    import random
    from datetime import datetime, timedelta
    
    # Enhanced sample data
    locations = ['Visakhapatnam', 'Vijayawada', 'Guntur', 'Nellore', 'Kurnool', 
                 'Rajahmundry', 'Tirupati', 'Kadapa', 'Anantapur', 'Chittoor']
    
    clusters = ['GVMC', 'VMC', 'GMC', 'NMC', 'KMC', 'RMC', 'TMC', 'CDMC', 'AMC', 'CMC']
    
    materials = ['Mixed Waste', 'Plastic', 'Paper', 'Organic', 'Metal', 'Glass', 'E-Waste', 'Hazardous']
    
    statuses = ['Completed', 'In Progress', 'Pending', 'Cancelled']
    
    priorities = ['High', 'Medium', 'Low', 'Critical']
    
    vehicles = [f'AP{str(i).zfill(2)}{chr(65+random.randint(0,25))}{chr(65+random.randint(0,25))}{random.randint(1000,9999)}' 
               for i in range(1, 26)]
    
    data = []
    start_date = datetime.now() - timedelta(days=30)
    
    for i in range(500):  # Generate 500 sample records
        date = start_date + timedelta(
            days=random.randint(0, 30),
            hours=random.randint(6, 20),
            minutes=random.randint(0, 59)
        )
        
        location = random.choice(locations)
        cluster = clusters[locations.index(location)]
        material = random.choice(materials)
        status = random.choice(statuses)
        priority = random.choice(priorities)
        
        empty_weight = random.randint(2000, 3500)
        loaded_weight = random.randint(5000, 12000)
        net_weight = loaded_weight - empty_weight
        
        efficiency = random.randint(70, 98)
        cost = round(net_weight * random.uniform(0.5, 2.0), 2)
        
        data.append({
            'ID': f'WM{str(i+1).zfill(4)}',
            'Date': date,
            'source_location': location,
            'Cluster': cluster,
            'Material Name': material,
            'Status': status,
            'Priority': priority,
            'Vehicle No': random.choice(vehicles),
            'Empty Weight': empty_weight,
            'Loaded Weight': loaded_weight,
            'Net Weight': net_weight,
            'Efficiency (%)': efficiency,
            'Cost (₹)': cost,
            'Operator': f'Operator {random.randint(1, 20)}',
            'Supervisor': f'Supervisor {chr(65+random.randint(0,4))}',
            'Route': f'Route {random.randint(1, 15)}',
            'Distance (km)': round(random.uniform(5, 50), 1),
            'Duration (hrs)': round(random.uniform(2, 8), 1)
        })
    
    df = pd.DataFrame(data)
    df['Week'] = df['Date'].dt.isocalendar().week
    df['Month'] = df['Date'].dt.month_name()
    df['DayOfWeek'] = df['Date'].dt.day_name()
    
    logger.info(f"Created {len(df)} sample filterable records")
    return df

def create_filter_controls(theme, unique_values):
    """Create comprehensive filter controls"""
    return html.Div(
        className="filter-controls-container",
        style={
            "backgroundColor": theme["card_bg"],
            "borderRadius": "12px",
            "border": f"2px solid {theme['accent_bg']}",
            "padding": "1.5rem",
            "marginBottom": "1.5rem",
            "boxShadow": "0 4px 16px rgba(0, 0, 0, 0.2)"
        },
        children=[
            # Filter Header
            html.Div([
                html.H3(
                    "🔍 Advanced Filters",
                    style={
                        "color": theme["text_primary"],
                        "fontSize": "1.5rem",
                        "fontWeight": "700",
                        "marginBottom": "1rem",
                        "display": "flex",
                        "alignItems": "center",
                        "gap": "0.5rem"
                    }
                ),
                html.Button(
                    "Clear All Filters",
                    id="clear-all-filters-btn",
                    style={
                        "backgroundColor": theme["warning"],
                        "color": "white",
                        "border": "none",
                        "borderRadius": "6px",
                        "padding": "0.5rem 1rem",
                        "fontSize": "0.85rem",
                        "fontWeight": "600",
                        "cursor": "pointer"
                    }
                )
            ], style={
                "display": "flex",
                "justifyContent": "space-between",
                "alignItems": "center",
                "marginBottom": "1.5rem"
            }),
            
            # Filter Grid
            html.Div(
                className="filters-grid",
                style={
                    "display": "grid",
                    "gridTemplateColumns": "repeat(auto-fit, minmax(250px, 1fr))",
                    "gap": "1rem",
                    "marginBottom": "1rem"
                },
                children=[
                    # Text Search
                    create_filter_item(
                        "🔎 Search",
                        dcc.Input(
                            id="text-search-filter",
                            type="text",
                            placeholder="Search locations, vehicles, operators...",
                            style=get_input_style(theme),
                            debounce=True
                        ),
                        theme
                    ),
                    
                    # Date Range
                    create_filter_item(
                        "📅 Date Range",
                        dcc.DatePickerRange(
                            id="date-range-filter",
                            start_date=datetime.now() - timedelta(days=7),
                            end_date=datetime.now(),
                            display_format='DD/MM/YYYY',
                            style={"width": "100%"}
                        ),
                        theme
                    ),
                    
                    # Location Filter
                    create_filter_item(
                        "📍 Locations",
                        dcc.Dropdown(
                            id="location-filter",
                            options=[{"label": loc, "value": loc} for loc in unique_values.get('locations', [])],
                            value=[],
                            multi=True,
                            placeholder="Select locations...",
                            style={"color": "#000"}
                        ),
                        theme
                    ),
                    
                    # Cluster Filter
                    create_filter_item(
                        "🌐 Clusters",
                        dcc.Dropdown(
                            id="cluster-filter",
                            options=[{"label": cluster, "value": cluster} for cluster in unique_values.get('clusters', [])],
                            value=[],
                            multi=True,
                            placeholder="Select clusters...",
                            style={"color": "#000"}
                        ),
                        theme
                    ),
                    
                    # Status Filter
                    create_filter_item(
                        "🚦 Status",
                        dcc.Dropdown(
                            id="status-filter",
                            options=[{"label": status, "value": status} for status in unique_values.get('statuses', [])],
                            value=[],
                            multi=True,
                            placeholder="Select status...",
                            style={"color": "#000"}
                        ),
                        theme
                    ),
                    
                    # Priority Filter
                    create_filter_item(
                        "⚡ Priority",
                        dcc.Dropdown(
                            id="priority-filter",
                            options=[{"label": priority, "value": priority} for priority in unique_values.get('priorities', [])],
                            value=[],
                            multi=True,
                            placeholder="Select priority...",
                            style={"color": "#000"}
                        ),
                        theme
                    ),
                    
                    # Weight Range
                    create_filter_item(
                        "⚖️ Net Weight Range (kg)",
                        dcc.RangeSlider(
                            id="weight-range-filter",
                            min=0,
                            max=unique_values.get('max_weight', 10000),
                            value=[0, unique_values.get('max_weight', 10000)],
                            marks={
                                0: "0",
                                unique_values.get('max_weight', 10000)//4: f"{unique_values.get('max_weight', 10000)//4}",
                                unique_values.get('max_weight', 10000)//2: f"{unique_values.get('max_weight', 10000)//2}",
                                3*unique_values.get('max_weight', 10000)//4: f"{3*unique_values.get('max_weight', 10000)//4}",
                                unique_values.get('max_weight', 10000): f"{unique_values.get('max_weight', 10000)}"
                            },
                            tooltip={"placement": "bottom", "always_visible": True}
                        ),
                        theme
                    ),
                    
                    # Efficiency Range
                    create_filter_item(
                        "📊 Efficiency Range (%)",
                        dcc.RangeSlider(
                            id="efficiency-range-filter",
                            min=0,
                            max=100,
                            value=[0, 100],
                            marks={0: "0%", 25: "25%", 50: "50%", 75: "75%", 100: "100%"},
                            tooltip={"placement": "bottom", "always_visible": True}
                        ),
                        theme
                    )
                ]
            ),
            
            # Filter Summary
            html.Div(
                id="filter-summary",
                style={
                    "padding": "1rem",
                    "backgroundColor": theme["accent_bg"],
                    "borderRadius": "8px",
                    "border": f"1px solid {theme.get('border_light', theme['accent_bg'])}",
                    "marginTop": "1rem"
                }
            )
        ]
    )

def create_filter_item(label, component, theme):
    """Create individual filter item with label"""
    return html.Div([
        html.Label(
            label,
            style={
                "color": theme["text_secondary"],
                "fontSize": "0.9rem",
                "fontWeight": "600",
                "marginBottom": "0.5rem",
                "display": "block"
            }
        ),
        component
    ])

def get_input_style(theme):
    """Get consistent input styling"""
    return {
        "width": "100%",
        "padding": "0.5rem",
        "backgroundColor": theme["accent_bg"],
        "border": f"2px solid {theme.get('border_light', theme['accent_bg'])}",
        "borderRadius": "6px",
        "color": theme["text_primary"],
        "fontSize": "0.9rem"
    }

def create_data_table(df, theme):
    """Create enhanced data table with styling"""
    if df.empty:
        return html.Div(
            "No data available",
            style={
                "textAlign": "center",
                "padding": "2rem",
                "color": theme["text_secondary"],
                "fontSize": "1.1rem"
            }
        )
    
    # Prepare columns
    columns = []
    for col in df.columns:
        if col in ['Date']:
            columns.append({
                "name": col,
                "id": col,
                "type": "datetime",
                "format": {"specifier": "%d/%m/%Y %H:%M"}
            })
        elif col in ['Net Weight', 'Loaded Weight', 'Empty Weight']:
            columns.append({
                "name": f"{col} (kg)",
                "id": col,
                "type": "numeric",
                "format": {"specifier": ",.0f"}
            })
        elif col in ['Cost (₹)']:
            columns.append({
                "name": col,
                "id": col,
                "type": "numeric",
                "format": {"specifier": ",.2f"}
            })
        elif col in ['Efficiency (%)', 'Distance (km)', 'Duration (hrs)']:
            columns.append({
                "name": col,
                "id": col,
                "type": "numeric",
                "format": {"specifier": ".1f"}
            })
        else:
            columns.append({"name": col, "id": col})
    
    return dash_table.DataTable(
        id="filterable-data-table",
        columns=columns,
        data=df.to_dict('records'),
        page_size=20,
        sort_action="native",
        sort_mode="multi",
        filter_action="native",
        row_selectable="multi",
        selected_rows=[],
        style_table={
            "overflowX": "auto",
            "borderRadius": "8px",
            "border": f"2px solid {theme['accent_bg']}"
        },
        style_header={
            "backgroundColor": theme["brand_primary"],
            "color": "white",
            "fontWeight": "700",
            "fontSize": "0.9rem",
            "padding": "12px",
            "textAlign": "center",
            "border": "none"
        },
        style_cell={
            "backgroundColor": theme["card_bg"],
            "color": theme["text_primary"],
            "fontSize": "0.85rem",
            "padding": "8px 12px",
            "textAlign": "left",
            "border": f"1px solid {theme['accent_bg']}",
            "fontFamily": "Inter, sans-serif"
        },
        style_data_conditional=[
            {
                "if": {"row_index": "odd"},
                "backgroundColor": theme["accent_bg"]
            },
            {
                "if": {"state": "selected"},
                "backgroundColor": f"{theme['brand_primary']}33",
                "border": f"2px solid {theme['brand_primary']}"
            }
        ],
        export_format="xlsx",
        export_headers="display"
    )

def create_summary_charts(df, theme):
    """Create summary visualization charts"""
    if df.empty:
        return html.Div("No data for charts", style={"color": theme["text_secondary"]})
    
    return html.Div([
        # Charts grid
        html.Div(
            style={
                "display": "grid",
                "gridTemplateColumns": "repeat(auto-fit, minmax(400px, 1fr))",
                "gap": "1.5rem",
                "marginBottom": "2rem"
            },
            children=[
                # Status distribution
                create_chart_container(
                    create_status_pie_chart(df, theme),
                    "📊 Status Distribution",
                    theme
                ),
                
                # Daily trends
                create_chart_container(
                    create_daily_trend_chart(df, theme),
                    "📈 Daily Collection Trends",
                    theme
                ),
                
                # Location performance
                create_chart_container(
                    create_location_bar_chart(df, theme),
                    "🏙️ Location Performance",
                    theme
                ),
                
                # Priority analysis
                create_chart_container(
                    create_priority_chart(df, theme),
                    "⚡ Priority Analysis",
                    theme
                )
            ]
        )
    ])

def create_chart_container(chart, title, theme):
    """Create styled container for charts"""
    return html.Div([
        html.H4(
            title,
            style={
                "color": theme["text_primary"],
                "fontSize": "1.1rem",
                "fontWeight": "600",
                "marginBottom": "1rem",
                "textAlign": "center"
            }
        ),
        chart
    ], style={
        "backgroundColor": theme["card_bg"],
        "borderRadius": "12px",
        "border": f"2px solid {theme['accent_bg']}",
        "padding": "1.5rem",
        "boxShadow": "0 4px 16px rgba(0, 0, 0, 0.1)"
    })

def create_status_pie_chart(df, theme):
    """Create status distribution pie chart"""
    status_counts = df['Status'].value_counts()
    
    fig = go.Figure(data=[go.Pie(
        labels=status_counts.index,
        values=status_counts.values,
        hole=0.4,
        marker_colors=[theme["success"], theme["warning"], theme["error"], theme["info"]]
    )])
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': theme['text_primary'], 'size': 12},
        margin=dict(l=20, r=20, t=20, b=20),
        height=300,
        showlegend=True,
        legend=dict(x=0, y=1)
    )
    
    return dcc.Graph(figure=fig, config={'displayModeBar': False})

def create_daily_trend_chart(df, theme):
    """Create daily collection trend chart"""
    daily_data = df.groupby(df['Date'].dt.date)['Net Weight'].sum().reset_index()
    
    fig = go.Figure(data=[go.Scatter(
        x=daily_data['Date'],
        y=daily_data['Net Weight'],
        mode='lines+markers',
        line=dict(color=theme['brand_primary'], width=3),
        marker=dict(size=6, color=theme['brand_primary']),
        fill='tonexty',
        fillcolor=f"rgba{tuple(list(px.colors.hex_to_rgb(theme['brand_primary'])) + [0.2])}"
    )])
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': theme['text_primary']},
        xaxis={'title': 'Date', 'color': theme['text_secondary']},
        yaxis={'title': 'Net Weight (kg)', 'color': theme['text_secondary']},
        margin=dict(l=50, r=20, t=20, b=50),
        height=300,
        showlegend=False
    )
    
    return dcc.Graph(figure=fig, config={'displayModeBar': False})

def create_location_bar_chart(df, theme):
    """Create location performance bar chart"""
    location_data = df.groupby('source_location')['Net Weight'].sum().sort_values(ascending=True).tail(10)
    
    fig = go.Figure(data=[go.Bar(
        y=location_data.index,
        x=location_data.values,
        orientation='h',
        marker_color=theme['brand_primary'],
        text=[f"{val:,.0f} kg" for val in location_data.values],
        textposition='auto'
    )])
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': theme['text_primary']},
        xaxis={'title': 'Total Net Weight (kg)', 'color': theme['text_secondary']},
        yaxis={'title': 'Location', 'color': theme['text_secondary']},
        margin=dict(l=150, r=20, t=20, b=50),
        height=300,
        showlegend=False
    )
    
    return dcc.Graph(figure=fig, config={'displayModeBar': False})

def create_priority_chart(df, theme):
    """Create priority analysis chart"""
    priority_data = df.groupby('Priority').agg({
        'Net Weight': 'sum',
        'ID': 'count'
    }).reset_index()
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='Total Weight',
        x=priority_data['Priority'],
        y=priority_data['Net Weight'],
        yaxis='y',
        marker_color=theme['brand_primary']
    ))
    
    fig.add_trace(go.Scatter(
        name='Count',
        x=priority_data['Priority'],
        y=priority_data['ID'],
        yaxis='y2',
        mode='lines+markers',
        line=dict(color=theme['warning'], width=3),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': theme['text_primary']},
        xaxis={'title': 'Priority Level', 'color': theme['text_secondary']},
        yaxis={'title': 'Total Weight (kg)', 'color': theme['text_secondary'], 'side': 'left'},
        yaxis2={'title': 'Count', 'color': theme['text_secondary'], 'side': 'right', 'overlaying': 'y'},
        margin=dict(l=50, r=50, t=20, b=50),
        height=300,
        legend=dict(x=0.02, y=0.98)
    )
    
    return dcc.Graph(figure=fig, config={'displayModeBar': False})

def create_filterable_container(theme, container_id="filterable-container"):
    """
    Create the main filterable container component
    
    Args:
        theme (dict): Theme configuration
        container_id (str): Unique container ID
        
    Returns:
        html.Div: Complete filterable container
    """
    # Load data and get unique values
    df = load_sample_waste_data()
    
    unique_values = {
        'locations': sorted(df['source_location'].unique()) if 'source_location' in df.columns else [],
        'clusters': sorted(df['Cluster'].unique()) if 'Cluster' in df.columns else [],
        'statuses': sorted(df['Status'].unique()) if 'Status' in df.columns else [],
        'priorities': sorted(df['Priority'].unique()) if 'Priority' in df.columns else [],
        'max_weight': int(df['Net Weight'].max()) if 'Net Weight' in df.columns else 10000
    }
    
    return html.Div(
        id=container_id,
        className="filterable-container-main",
        style={
            "margin": "2rem 0",
            "padding": "0"
        },
        children=[
            # Container Header
            html.Div([
                html.H2(
                    "📋 Advanced Data Analytics & Filtering",
                    style={
                        "color": theme["text_primary"],
                        "fontSize": "2rem",
                        "fontWeight": "800",
                        "marginBottom": "0.5rem"
                    }
                ),
                html.P(
                    "Filter, analyze, and export waste management data with advanced controls and real-time visualizations.",
                    style={
                        "color": theme["text_secondary"],
                        "fontSize": "1.1rem",
                        "marginBottom": "2rem",
                        "lineHeight": "1.5"
                    }
                )
            ]),
            
            # Filter Controls
            create_filter_controls(theme, unique_values),
            
            # Data Summary Stats
            html.Div(
                id="filtered-data-summary",
                style={
                    "marginBottom": "1.5rem"
                }
            ),
            
            # Summary Charts
            html.Div(
                id="filtered-data-charts",
                children=[create_summary_charts(df, theme)]
            ),
            
            # Data Table Section
            html.Div([
                html.Div([
                    html.H3(
                        "📊 Filtered Data Table",
                        style={
                            "color": theme["text_primary"],
                            "fontSize": "1.5rem",
                            "fontWeight": "700",
                            "marginBottom": "1rem"
                        }
                    ),
                    html.Button(
                        "📤 Export Filtered Data",
                        id="export-filtered-data-btn",
                        style={
                            "backgroundColor": theme["success"],
                            "color": "white",
                            "border": "none",
                            "borderRadius": "6px",
                            "padding": "0.75rem 1.5rem",
                            "fontSize": "0.9rem",
                            "fontWeight": "600",
                            "cursor": "pointer",
                            "boxShadow": "0 2px 8px rgba(0, 0, 0, 0.2)"
                        }
                    )
                ], style={
                    "display": "flex",
                    "justifyContent": "space-between",
                    "alignItems": "center",
                    "marginBottom": "1rem"
                }),
                
                # Data Table Container
                html.Div(
                    id="filtered-data-table-container",
                    children=[create_data_table(df, theme)]
                )
            ], style={
                "backgroundColor": theme["card_bg"],
                "borderRadius": "12px",
                "border": f"2px solid {theme['accent_bg']}",
                "padding": "1.5rem",
                "boxShadow": "0 4px 16px rgba(0, 0, 0, 0.2)"
            })
        ]
    )