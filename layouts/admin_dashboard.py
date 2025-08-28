# layouts/admin_dashboard.py - ENHANCED VERSION
"""
ENHANCED: Admin Dashboard with minimal date filter and proper cascading filters
1. Compact date filter that takes less space
2. Cross-join filtering: Agency -> Cluster -> Site cascade
"""

from dash import html, dcc, callback, Output, Input, State, callback_context
import dash_ag_grid as dag
from datetime import datetime, date
import random
from flask import session, redirect, request
import os
from pathlib import Path
import pandas as pd
import json
from file_watcher import get_latest_data, get_data_timestamp
from utils.theme_utils import get_theme_styles
from components.navigation.hover_overlay import create_hover_overlay_banner
from flask import jsonify
import flask
import traceback
import logging
from dash import clientside_callback

logger = logging.getLogger(__name__)

def get_current_theme():
    """Get current theme from session or default"""
    return session.get('current_theme', 'dark')

def get_embedded_csv_data():
    """Load CSV data from data/csv_data_combined.csv using pandas"""
    try:
        # 🔥 FIXED: Check multiple possible CSV file paths
        possible_paths = [
            'data/Bethamcherla.csv'
        ]
        
        csv_path = None
        for path in possible_paths:
            if os.path.exists(path):
                csv_path = path
                break
        
        if not csv_path:
            logger.error(f"❌ No CSV file found in any of these paths: {possible_paths}")
            # 🔥 ADDED: Return sample data for testing if no CSV found
            return get_sample_data_for_testing()
        
        logger.info(f"📁 Loading CSV from: {csv_path}")
        
        # Read the CSV file using pandas with proper encoding
        try:
            df = pd.read_csv(csv_path, encoding='utf-8')
            logger.info(f"✅ Successfully loaded with UTF-8 encoding")
        except UnicodeDecodeError:
            try:
                df = pd.read_csv(csv_path, encoding='latin-1')
                logger.info(f"✅ Successfully loaded with Latin-1 encoding")
            except:
                df = pd.read_csv(csv_path, encoding='cp1252')
                logger.info(f"✅ Successfully loaded with CP1252 encoding")
        
        # 🔥 FIXED: Debug CSV structure
        logger.info(f"📋 CSV Columns detected: {list(df.columns)}")
        logger.info(f"📊 CSV Shape: {df.shape}")
        logger.info(f"📝 First few rows preview:")
        for i, row in df.head(3).iterrows():
            logger.info(f"   Row {i}: {dict(row)}")
        
        # Parse date column with DD-MM-YYYY format if it exists
        date_columns = ['date', 'Date', 'DATE', 'transaction_date', 'Date_Time']
        for date_col in date_columns:
            if date_col in df.columns:
                df['date_parsed'] = df[date_col].apply(parse_yyyy_mm_dd_date)
                logger.info(f"📅 Parsed date column '{date_col}'. Sample dates: {df[date_col].head(3).tolist()}")
                break
        
        logger.info(f"✅ Loaded {len(df)} records from CSV")
        
        # Convert DataFrame to dictionary format for JavaScript
        csv_data = df.to_dict('records')
        
        return csv_data
        
    except Exception as e:
        logger.error(f"❌ Error loading CSV data: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        # 🔥 ADDED: Return sample data if real CSV fails
        return get_sample_data_for_testing()

def get_sample_data_for_testing():
    """Generate sample data for testing when CSV is not available"""
    logger.info("🔧 Generating sample data for testing...")
    
    import random
    from datetime import datetime, timedelta
    
    agencies = ['GMADA', 'GHMC', 'Corporation A', 'Corporation B', 'Municipal Corp']
    # 🔥 ENHANCED: Create proper agency-cluster-site relationships
    agency_clusters = {
        'GMADA': ['North Zone', 'South Zone'],
        'GHMC': ['East Zone', 'West Zone'],
        'Corporation A': ['Central Zone', 'North Zone'],
        'Corporation B': ['South Zone', 'East Zone'],
        'Municipal Corp': ['West Zone', 'Central Zone']
    }
    
    cluster_sites = {
        'North Zone': ['Site Alpha', 'Site Beta'],
        'South Zone': ['Site Gamma', 'Site Delta'],
        'East Zone': ['Site Epsilon', 'Site Zeta'],
        'West Zone': ['Site Eta', 'Site Theta'],
        'Central Zone': ['Site Iota', 'Site Kappa']
    }
    
    contractors = ['Contractor ABC', 'Contractor XYZ', 'Contractor 123', 'Contractor DEF']
    machines = ['Machine M001', 'Machine M002', 'Machine M003', 'Machine M004']
    
    sample_data = []
    for i in range(100):  # Generate 100 sample records
        # Generate random date in last 30 days
        random_date = datetime.now() - timedelta(days=random.randint(0, 30))
        date_str = random_date.strftime('%d-%m-%Y')
        
        # 🔥 ENHANCED: Create realistic relationships
        agency = random.choice(agencies)
        cluster = random.choice(agency_clusters[agency])
        site = random.choice(cluster_sites[cluster])
        
        record = {
            'date': date_str,
            'agency_name': agency,  # 🔥 CHANGED: Use agency_name for consistency
            'Cluster': cluster,
            'Site': site,
            'Sub_contractor': random.choice(contractors),
            'Machines': random.choice(machines),
            'net_weight_calculated': random.randint(100, 1000),
            'Total_capacity_per_day': random.randint(500, 2000),
            'ticket_no': f'TKT{str(i+1).zfill(4)}'
        }
        sample_data.append(record)
    
    logger.info(f"🔧 Generated {len(sample_data)} sample records with proper relationships")
    return sample_data



@callback(
    Output('dashboard-subtitle', 'children'),
    [Input('start-date-input', 'date'),
     Input('end-date-input', 'date')],
    [State('csv-data-store', 'data')],
    prevent_initial_call=True
)
def update_date_filter_feedback(start_date, end_date, csv_data):
    """Provide real-time feedback about date filter selection"""
    try:
        if not csv_data:
            return "No data available"
        
        df = pd.DataFrame(csv_data)
        total_records = len(df)
        
        # Get actual date range from CSV
        if 'date' in df.columns:
            df_temp = df.copy()
            df_temp['date_parsed'] = df_temp['date'].apply(parse_date_flexible)
            valid_dates = df_temp['date_parsed'].dropna()
            
            if len(valid_dates) > 0:
                csv_start = valid_dates.min().strftime('%Y-%m-%d')
                csv_end = valid_dates.max().strftime('%Y-%m-%d')
                date_range_info = f"Data range: {csv_start} to {csv_end}"
            else:
                date_range_info = "Date parsing issues detected"
        else:
            date_range_info = "No date column found"
        
        # Build feedback message
        if start_date and end_date:
            message = f"📅 Date filter: {start_date} to {end_date} • {total_records} total records • {date_range_info} • Click 'Apply Filters' to update"
        elif start_date:
            message = f"📅 Start date: {start_date} • {total_records} total records • {date_range_info} • Click 'Apply Filters' to update"
        elif end_date:
            message = f"📅 End date: {end_date} • {total_records} total records • {date_range_info} • Click 'Apply Filters' to update"
        else:
            message = f"Real-time data from SAC monitor tool • {total_records} total records • {date_range_info}"
        
        return message
        
    except Exception as e:
        logger.error(f"❌ Error in date feedback: {str(e)}")
        return f"Error updating feedback • {len(csv_data) if csv_data else 0} records"


@callback(
    Output('apply-filters-btn', 'children'),
    [Input('start-date-input', 'date'),
     Input('end-date-input', 'date'),
     Input('agency-filter', 'value'),
     Input('cluster-filter', 'value'),
     Input('site-filter', 'value')],
    prevent_initial_call=True
)

def update_apply_button_with_debug(start_date, end_date, agencies, clusters, sites):
    """Update apply button text to show current filter state"""
    active_filters = []
    
    if agencies:
        active_filters.append(f"Agency({len(agencies)})")
    if clusters:
        active_filters.append(f"Cluster({len(clusters)})") 
    if sites:
        active_filters.append(f"Site({len(sites)})")
    if start_date:
        active_filters.append(f"Start({start_date})")
    if end_date:
        active_filters.append(f"End({end_date})")
    
    if active_filters:
        filter_text = ", ".join(active_filters)
        return [
            html.Span("🔄", style={'marginRight': '0.5rem'}),
            f"Apply Filters ({len(active_filters)} active: {filter_text})"
        ]
    else:
        return [
            html.Span("🔄", style={'marginRight': '0.5rem'}),
            "Apply Filters"
        ]


def get_filter_options_from_embedded_data():
    """Extract unique filter options from CSV data using correct column names"""
    try:
        csv_data = get_embedded_csv_data()
        
        if not csv_data:
            logger.warning("⚠️ No CSV data available, returning empty options")
            return {
                'agencies': ['No data available'],
                'clusters': ['No data available'], 
                'sites': ['No data available'],
                'sub_contractors': ['No data available'],
                'machines': ['No data available']
            }
        
        df = pd.DataFrame(csv_data)
        logger.info(f"🔍 Processing {len(df)} records to extract filter options")
        
        def get_unique_values(df, possible_column_names, default_name):
            """Get unique values from DataFrame for given possible column names"""
            for col_name in possible_column_names:
                if col_name in df.columns:
                    logger.info(f"   Found column '{col_name}' for {default_name}")
                    unique_vals = df[col_name].dropna().astype(str).str.strip()
                    unique_vals = unique_vals[unique_vals != ''].unique()
                    unique_list = sorted(list(unique_vals))
                    logger.info(f"   Extracted {len(unique_list)} unique {default_name}: {unique_list[:5]}{'...' if len(unique_list) > 5 else ''}")
                    return unique_list
            
            logger.warning(f"   No column found for {default_name} in: {possible_column_names}")
            return [f'No {default_name} data']
        
        # 🔥 FIXED: Use correct column names from your CSV structure
        agencies = get_unique_values(df, ['agency_name'], 'agency')
        clusters = get_unique_values(df, ['cluster'], 'cluster') 
        sites = get_unique_values(df, ['site_name'], 'site')
        sub_contractors = get_unique_values(df, ['transfer_party_name'], 'sub_contractor')
        machines = get_unique_values(df, ['vehicle_no'], 'vehicle')
        
        options = {
            'agencies': agencies,
            'clusters': clusters,
            'sites': sites,
            'sub_contractors': sub_contractors,
            'machines': machines
        }
        
        logger.info(f"✅ Filter options extracted successfully:")
        for key, values in options.items():
            logger.info(f"   {key}: {len(values)} options")
        
        return options
        
    except Exception as e:
        logger.error(f"❌ Error extracting filter options: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {
            'agencies': ['Error loading data'],
            'clusters': ['Error loading data'], 
            'sites': ['Error loading data'],
            'sub_contractors': ['Error loading data'],
            'machines': ['Error loading data']
        }

def parse_yyyy_mm_dd_date(date_str):
    """Parse date string in DD-MM-YYYY format"""
    if not date_str or pd.isna(date_str):
        return None
    
    try:
        # Try DD-MM-YYYY format first
        return pd.to_datetime(date_str, format='%Y-%m-%d', errors='coerce')
    except:
        try:
            # Fallback to dayfirst=True
            return pd.to_datetime(date_str, dayfirst=True, errors='coerce')
        except:
            return None

def get_processed_dataframe():
    """Get processed DataFrame for dash_ag_grid"""
    try:
        csv_data = get_embedded_csv_data()
        if not csv_data:
            logger.warning("⚠️ No CSV data available for processing")
            return pd.DataFrame()
        
        df = pd.DataFrame(csv_data)
        logger.info(f"🔄 Processing DataFrame with {len(df)} records")
        
        # Format date column
        date_columns = ['date', 'Date', 'DATE', 'transaction_date']
        for date_col in date_columns:
            if date_col in df.columns:
                df['date_formatted'] = df[date_col].apply(lambda x: x if pd.notna(x) else 'N/A')
                break
        
        # Ensure numeric columns are properly formatted
        numeric_columns = ['net_weight_calculated', 'Total_capacity_per_day', 'weight', 'capacity']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                logger.info(f"   Processed numeric column: {col}")
        
        # Sort by date if possible
        for date_col in date_columns:
            if date_col in df.columns:
                df['date_sort'] = df[date_col].apply(parse_yyyy_mm_dd_date)
                df = df.sort_values('date_sort', ascending=False, na_position='last')
                df = df.drop('date_sort', axis=1)
                break
        
        logger.info(f"✅ DataFrame processed successfully")
        return df
        
    except Exception as e:
        logger.error(f"❌ Error processing DataFrame: {str(e)}")
        return pd.DataFrame()

def create_dash_dashboard_layout(title, icon, theme_name="dark"):
    """Create dashboard layout using Dash components with dash_ag_grid"""
    theme_styles = get_theme_styles(theme_name)
    theme = theme_styles["theme"]
    
    # 🔥 FIXED: Get processed data with better error handling
    df = get_processed_dataframe()
    logger.info(f"🏗️ Creating dashboard layout with {len(df)} records")
    
    # 🔥 FIXED: Get filter options from the data with debugging
    filter_options = get_filter_options_from_embedded_data()
    logger.info(f"🔍 Filter options loaded: {[(k, len(v)) for k, v in filter_options.items()]}")
    
    # Calculate statistics
    total_records = len(df)
    total_weight = 0
    unique_contractors = 0
    unique_machines = 0
    total_capacity = 0
    
    if not df.empty:
        # Check for weight columns
        weight_columns = ['net_weight']
        for col in weight_columns:
            if col in df.columns:
                total_weight = df[col].sum()
                break
        
        # Check for contractor columns
        contractor_columns = ['Sub_contractor', 'contractor', 'Contractor']
        for col in contractor_columns:
            if col in df.columns:
                unique_contractors = df[col].nunique()
                break
        
        # Check for machine columns
        machine_columns = ['Machines', 'Machine', 'machines', 'equipment']
        for col in machine_columns:
            if col in df.columns:
                unique_machines = df[col].nunique()
                break
        
        # Check for capacity columns
        capacity_columns = ['Total_capacity_per_day', 'capacity', 'Capacity']
        for col in capacity_columns:
            if col in df.columns:
                total_capacity = df[col].sum()
                break
    
    # 🔥 FIXED: Define column definitions with better column detection
    column_defs = []
    if not df.empty:
        # Define specific columns with proper formatting
        date_columns = ['date', 'Date', 'DATE']
        for col in date_columns:
            if col in df.columns:
                column_defs.append({
                    'field': col,
                    'headerName': 'Date',
                    'width': 120,
                    'pinned': 'left',
                    'filter': 'agDateColumnFilter'
                })
                break
        
        agency_columns = ['agency_name', 'Agency', 'agency', 'AGENCY']
        for col in agency_columns:
            if col in df.columns:
                column_defs.append({
                    'field': col,
                    'headerName': 'Agency',
                    'width': 150,
                    'filter': 'agSetColumnFilter'
                })
                break
        
        cluster_columns = ['Cluster', 'cluster', 'CLUSTER']
        for col in cluster_columns:
            if col in df.columns:
                column_defs.append({
                    'field': col,
                    'headerName': 'Cluster',
                    'width': 120,
                    'filter': 'agSetColumnFilter'
                })
                break
        
        site_columns = ['Site', 'site', 'SITE', 'site_name']
        for col in site_columns:
            if col in df.columns:
                column_defs.append({
                    'field': col,
                    'headerName': 'Site',
                    'width': 120,
                    'filter': 'agSetColumnFilter'
                })
                break
        
        contractor_columns = ['Sub_contractor', 'contractor', 'Contractor']
        for col in contractor_columns:
            if col in df.columns:
                column_defs.append({
                    'field': col,
                    'headerName': 'Sub-contractor',
                    'width': 150,
                    'filter': 'agSetColumnFilter'
                })
                break
        
        machine_columns = ['Machines', 'Machine', 'machines']
        for col in machine_columns:
            if col in df.columns:
                column_defs.append({
                    'field': col,
                    'headerName': 'Machine',
                    'width': 120,
                    'filter': 'agSetColumnFilter'
                })
                break
        
        weight_columns = ['net_weight_calculated', 'weight', 'Weight']
        for col in weight_columns:
            if col in df.columns:
                column_defs.append({
                    'field': col,
                    'headerName': 'Net Weight (kg)',
                    'width': 140,
                    'filter': 'agNumberColumnFilter',
                    'valueFormatter': {'function': 'params.value ? params.value.toLocaleString() : "0"'}
                })
                break
        
        capacity_columns = ['Total_capacity_per_day', 'capacity', 'Capacity']
        for col in capacity_columns:
            if col in df.columns:
                column_defs.append({
                    'field': col,
                    'headerName': 'Capacity/Day',
                    'width': 130,
                    'filter': 'agNumberColumnFilter',
                    'valueFormatter': {'function': 'params.value ? params.value.toLocaleString() : "0"'}
                })
                break
        
        ticket_columns = ['ticket_no', 'Ticket_No', 'ticket_number']
        for col in ticket_columns:
            if col in df.columns:
                column_defs.append({
                    'field': col,
                    'headerName': 'Ticket No',
                    'width': 120,
                    'filter': 'agTextColumnFilter'
                })
                break
    
    # Navigation - get user info
    user_info = session.get('user_data', {})
    user_name = user_info.get('name', 'Administrator')
    user_role_display = user_info.get('role', 'administrator').replace('_', ' ').title()
    user_role_raw = user_info.get('role', 'viewer')
    
    # Apply role-based access control
    try:
        from config.auth import get_tab_permissions
        allowed_tabs = get_tab_permissions(user_role_raw)
    except ImportError:
        restrictive_permissions = {
            'viewer': ['dashboard', 'analytics', 'reports'],
            'administrator': ['dashboard', 'analytics', 'reports', 'reviews', 'upload'],
            'super_admin': ['dashboard', 'analytics', 'reports', 'reviews', 'upload', 'forecasting']
        }
        allowed_tabs = restrictive_permissions.get(user_role_raw, ['dashboard'])
    
    # Build navigation
    all_tabs = [
        {"id": "dashboard", "href": "/dashboard", "label": "📊 Dashboard", "active_check": "dashboard"},
        {"id": "analytics", "href": "/data-analytics", "label": "🔍 Data Analytics", "active_check": "data analytics"},
        {"id": "reports", "href": "/reports", "label": "📋 Reports", "active_check": "reports"},
        {"id": "reviews", "href": "/reviews", "label": "⭐ Reviews", "active_check": "reviews"},
        {"id": "upload", "href": "/upload", "label": "📤 Upload", "active_check": "upload"},
        {"id": "forecasting", "href": "/forecasting", "label": "🔮 Forecasting", "active_check": "forecasting"}
    ]
    
    visible_tabs = [tab for tab in all_tabs if tab["id"] in allowed_tabs]
    
    nav_buttons = []
    for tab in visible_tabs:
        active_class = "nav-tab active" if tab["active_check"] in title.lower() else "nav-tab"
        nav_buttons.append(
            html.A(
                tab["label"],
                href=tab["href"],
                className=active_class
            )
        )
    
    # Create the main layout structure
    layout = html.Div([
        # CSS and external resources
        dcc.Store(id='csv-data-store', data=df.to_dict('records') if not df.empty else []),
        dcc.Store(id='filtered-data-store', data=df.to_dict('records') if not df.empty else []),
        dcc.Store(id='filters-initialized', data=False),
        
        html.Link(
            rel="stylesheet",
            href="/assets/css/admin_dashboard_pages.css"
        ),
        html.Link(
            href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap",
            rel="stylesheet"
        ),
        
        html.Div([
            # Navigation Header
            html.Nav([
                html.Div([
                    html.Div(nav_buttons, className="nav-tabs"),
                    html.Div([
                        html.Img(src="/assets/img/default-avatar.png", alt="User Avatar", className="user-avatar"),
                        html.Div([
                            html.Div(user_name, className="user-name"),
                            html.Div(user_role_display, className="user-role")
                        ]),
                        html.A("🚪 Logout", href="/?logout=true", className="logout-btn")
                    ], className="user-info")
                ], className="nav-content")
            ], className="navigation-header"),
            
            # Main Content
            html.Main([
                html.Div([
                    # Dashboard Header
                    html.Div([
                        html.H1(f"{icon} {title}", className="dashboard-title"),
                        html.P(
                            f"Real-time data from SAC monitor tool • {total_records} total records • DD-MM-YYYY format",
                            className="dashboard-subtitle",
                            id="dashboard-subtitle"
                        )
                    ], className="dashboard-header"),
                    
                    # 🔥 UPDATED: Perfect filter alignment - Replace your existing filters section with this

                    # Filters Container with unified row alignment
                    html.Div([
                        # Filters Header
                        html.Div([
                            html.H3([
                                html.Span("🔍", style={'marginRight': '0.5rem'}),
                                "Data Filters"
                            ], className="filters-title"),
                            html.P("Filter data by selecting options below", className="filters-subtitle")
                        ], className="filters-header"),
                        
                        # 🔥 PERFECT UNIFIED ROW: All filters in one line with perfect alignment
                        html.Div([
                            # Agency Filter
                            html.Div([
                                html.Label([
                                    html.Span("🏢", style={'marginRight': '0.5rem'}),
                                    "Agency"
                                ], className="filter-label-unified"),
                                dcc.Dropdown(
                                    id='agency-filter',
                                    options=[{'label': agency, 'value': agency} for agency in filter_options['agencies']] if filter_options['agencies'] != ['No data available'] else [{'label': 'No agencies found', 'value': 'none'}],
                                    value=None,
                                    placeholder="Select Agency...",
                                    multi=True,
                                    className="filter-dropdown-unified",
                                    clearable=True,
                                    searchable=True,
                                    persistence=False,
                                    # 🔥 CRITICAL: Ensure dropdown renders properly
                                    style={'width': '100%', 'minWidth': '160px'}
                                )
                            ], className="filter-wrapper"),
                            
                            # Cluster Filter
                            html.Div([
                                html.Label([
                                    html.Span("🗂️", style={'marginRight': '0.5rem'}),
                                    "Cluster"
                                ], className="filter-label-unified"),
                                dcc.Dropdown(
                                    id='cluster-filter',
                                    options=[],
                                    value=None,
                                    placeholder="Select Agency first...",
                                    multi=True,
                                    className="filter-dropdown-unified",
                                    clearable=True,
                                    searchable=True,
                                    persistence=False,
                                    style={'width': '100%', 'minWidth': '160px'}
                                )
                            ], className="filter-wrapper"),
                            
                            # Site Filter
                            html.Div([
                                html.Label([
                                    html.Span("📍", style={'marginRight': '0.5rem'}),
                                    "Site"
                                ], className="filter-label-unified"),
                                dcc.Dropdown(
                                    id='site-filter',
                                    options=[],
                                    value=None,
                                    placeholder="Select Cluster first...",
                                    multi=True,
                                    className="filter-dropdown-unified",
                                    clearable=True,
                                    searchable=True,
                                    persistence=False,
                                    style={'width': '100%', 'minWidth': '160px'}
                                )
                            ], className="filter-wrapper"),
                            
                            # Start Date Filter
                            html.Div([
                                html.Label([
                                    html.Span("📅", style={'marginRight': '0.5rem'}),
                                    "Start Date"
                                ], className="filter-label-unified"),
                                dcc.DatePickerSingle(
                                    id='start-date-input',
                                    placeholder='Start Date',
                                    display_format='YYYY-MM-DD',
                                    className="date-picker-unified",
                                    clearable=True,
                                    with_portal=True,  # 🔥 IMPORTANT: Prevents alignment issues
                                    first_day_of_week=1,
                                    # 🔥 CRITICAL: Perfect styling match
                                    style={
                                        'width': '100%', 
                                        'minWidth': '160px',
                                        'height': '52px'
                                    }
                                )
                            ], className="filter-wrapper"),
                            
                            # End Date Filter
                            html.Div([
                                html.Label([
                                    html.Span("📅", style={'marginRight': '0.5rem'}),
                                    "End Date"
                                ], className="filter-label-unified"),
                                dcc.DatePickerSingle(
                                    id='end-date-input',
                                    placeholder='End Date',
                                    display_format='YYYY-MM-DD',
                                    className="date-picker-unified",
                                    clearable=True,
                                    with_portal=True,  # 🔥 IMPORTANT: Prevents alignment issues
                                    first_day_of_week=1,
                                    # 🔥 CRITICAL: Perfect styling match
                                    style={
                                        'width': '100%', 
                                        'minWidth': '160px',
                                        'height': '52px'
                                    }
                                )
                            ], className="filter-wrapper"),
                            
                        ], className="filters-unified-row"),
                        
                        # 🔥 DEBUG INFO (remove in production)
                        html.Div([
                            html.P(f"🔧 Debug: CSV loaded with {total_records} records", 
                                  style={
                                      'fontSize': '0.8rem', 
                                      'color': 'var(--text-secondary)', 
                                      'textAlign': 'center', 
                                      'marginTop': '1rem',
                                      'fontStyle': 'italic'
                                  })
                        ]),
                        
                        # Filter Actions
                        html.Div([
                            html.Button([
                                html.Span("🔄", style={'marginRight': '0.5rem'}),
                                "Apply Filters"
                            ], id="apply-filters-btn", className="filter-btn primary"),
                            html.Button([
                                html.Span("🧹", style={'marginRight': '0.5rem'}),
                                "Clear All"
                            ], id="clear-all-filters-btn", className="filter-btn secondary")
                        ], className="filters-actions")
                    ], className="filters-container"),
                    
                    # Quick Stats
                    html.Div([
                        html.Div([
                            html.Span("📊", className="stat-icon"),
                            html.Div("Records", className="stat-label"),
                            html.Div(f"{total_records:,}", className="stat-value", id="filtered-records")
                        ], className="stat-card"),
                        html.Div([
                            html.Span("⚖️", className="stat-icon"),
                            html.Div("Total Weight", className="stat-label"),
                            html.Div(f"{total_weight/1000:,.2f} MT", className="stat-value", id="filtered-weight")
                        ], className="stat-card"),
                        html.Div([
                            html.Span("👥", className="stat-icon"),
                            html.Div("Sub-contractors", className="stat-label"),
                            html.Div(str(unique_contractors), className="stat-value", id="filtered-contractors")
                        ], className="stat-card"),
                        html.Div([
                            html.Span("🏭", className="stat-icon"),
                            html.Div("Machines", className="stat-label"),
                            html.Div(str(unique_machines), className="stat-value", id="filtered-machines")
                        ], className="stat-card"),
                        html.Div([
                            html.Span("🔋", className="stat-icon"),
                            html.Div("Total Capacity", className="stat-label"),
                            html.Div(f"{total_capacity:,.0f}", className="stat-value", id="filtered-capacity")
                        ], className="stat-card")
                    ], className="stats-container"),
                    
                    # Data Grid Section
                    html.Div([
                        # Grid Header with Title
                        html.Div([
                            html.H2("📋 Data Management", className="grid-title")
                        ], style={'marginBottom': '1rem'}),
                        
                        # Column Selection Container
                        html.Div([
                            html.Div([
                                html.Label("Select Columns to Display:", 
                                          style={
                                              'marginBottom': '15rem', 
                                              'color': 'var(--text-primary)',
                                              'fontWeight': '600',
                                              'fontSize': '1.5rem'
                                          }),
                                dcc.Dropdown(
                                    id='column-selector',
                                    options=[{'label': c, 'value': c} for c in df.columns] if not df.empty else [],
                                    value=list(df.columns) if not df.empty else [],
                                    multi=True,
                                    placeholder="Choose columns to show on the table...",
                                    persistence=False
                                )
                            ],
                            )
                        ]),
                        
                        # Action Buttons Container
                        html.Div([
                            html.Div([
                                html.Button("🔄 Refresh", id="refresh-btn", className="grid-btn"),
                                html.Button("📊 Export CSV", id="export-btn", className="grid-btn secondary"),
                                html.Button("🧹 Clear Filters", id="clear-filters-btn", className="grid-btn secondary"),
                                html.Button("🔧 Reset Columns", id="reset-columns-btn", className="grid-btn secondary", 
                                           title="Reset column order and visibility")
                            ], className="grid-controls")
                        ], style={'marginBottom': '1rem'}),
                        
                        # ag-Grid Component
                        dag.AgGrid(
                            id='csv-grid',
                            columnDefs=column_defs,
                            rowData=df.to_dict('records') if not df.empty else [],
                            defaultColDef={
                                "filter": True,
                                "sortable": True,
                                "resizable": True,
                                "flex": 1,
                                "minWidth": 100
                            },
                            dashGridOptions={
                                "pagination": True,
                                "paginationPageSize": 50,
                                "paginationPageSizeSelector": [25, 50, 100, 200],
                                "rowSelection": "multiple",
                                "suppressRowClickSelection": True,
                                "animateRows": True,
                                "enableRangeSelection": True,
                                "suppressDragLeaveHidesColumns": True,
                                "suppressMovableColumns": False,
                                "allowDragFromColumnsToolPanel": True,
                                "sideBar": {
                                    "toolPanels": [
                                        {
                                            "id": "filters",
                                            "labelDefault": "Filters",
                                            "labelKey": "filters",
                                            "iconKey": "filter",
                                            "toolPanel": "agFiltersToolPanel"
                                        },
                                        {
                                            "id": "columns",
                                            "labelDefault": "Columns",
                                            "labelKey": "columns", 
                                            "iconKey": "columns",
                                            "toolPanel": "agColumnsToolPanel",
                                            "toolPanelParams": {
                                                "suppressValues": True,
                                                "suppressPivots": True,
                                                "suppressPivotMode": True,
                                                "suppressRowGroups": True
                                            }
                                        }
                                    ]
                                }
                            },
                            className="ag-theme-custom",
                            style={'height': '600px', 'width': '100%'}
                        )
                    ], className="grid-container")
                    
                ], className="dashboard-container")
            ], className="main-content"),
            
            # Footer
            html.Footer([
                html.P([
                    f"© 2025 Swaccha Andhra Corporation • {title}• ",
                    html.Span(id="current-time")
                ])
            ], className="footer"),
            
            # Interval component for time updates
            dcc.Interval(
                id='time-interval',
                interval=1000,  # Update every second
                n_intervals=0
            )
            
        ], className="page-container")
    ])
    
    return layout

# 🔥 ENHANCED: Cascading Filter Callbacks - Agency -> Cluster -> Site

@callback(
    [Output('cluster-filter', 'options'),
     Output('cluster-filter', 'placeholder'),
     Output('cluster-filter', 'value')],  # 🔥 ADDED: Clear value when options change
    [Input('agency-filter', 'value')],
    [State('csv-data-store', 'data')],
    prevent_initial_call=False
)
def update_cluster_options_based_on_agency(selected_agencies, csv_data):
    """Update cluster options based on selected agencies - CASCADING FILTER"""
    try:
        if not csv_data:
            return [], "No data available", None
        
        df = pd.DataFrame(csv_data)
        
        if df.empty:
            return [], "No data available", None
        
        # 🔥 ENHANCED: Filter clusters based on selected agencies
        if selected_agencies and selected_agencies != ['none']:
            logger.info(f"🔗 Filtering clusters for agencies: {selected_agencies}")
            
            # Find the agency column
            agency_col = None
            for col in ['agency_name', 'Agency', 'agency', 'AGENCY']:
                if col in df.columns:
                    agency_col = col
                    break
            
            if agency_col:
                # Filter dataframe to only include selected agencies
                filtered_df = df[df[agency_col].isin(selected_agencies)]
                logger.info(f"   Found {len(filtered_df)} records for selected agencies")
            else:
                filtered_df = df
                logger.warning("   No agency column found, using all data")
        else:
            # No agencies selected, return all clusters
            filtered_df = df
            logger.info("🔗 No agencies selected, showing all clusters")
        
        # Get unique clusters from filtered data
        cluster_col = None
        for col in ['Cluster', 'cluster', 'CLUSTER']:
            if col in filtered_df.columns:
                cluster_col = col
                break
        
        if cluster_col:
            unique_clusters = filtered_df[cluster_col].dropna().astype(str).str.strip()
            unique_clusters = unique_clusters[unique_clusters != ''].unique()
            cluster_options = [{'label': cluster, 'value': cluster} for cluster in sorted(unique_clusters)]
            
            placeholder = f"Select Cluster... ({len(cluster_options)} available)"
            logger.info(f"   Updated cluster options: {len(cluster_options)} clusters available")
            
            return cluster_options, placeholder, None  # 🔥 CLEAR: Reset cluster selection
        else:
            logger.warning("   No cluster column found")
            return [], "No cluster data found", None
            
    except Exception as e:
        logger.error(f"❌ Error updating cluster options: {str(e)}")
        return [], "Error loading clusters", None

@callback(
    [Output('site-filter', 'options'),
     Output('site-filter', 'placeholder'),
     Output('site-filter', 'value')],  # 🔥 ADDED: Clear value when options change
    [Input('agency-filter', 'value'),
     Input('cluster-filter', 'value')],
    [State('csv-data-store', 'data')],
    prevent_initial_call=False
)
def update_site_options_based_on_agency_and_cluster(selected_agencies, selected_clusters, csv_data):
    """Update site options based on selected agencies and clusters - CASCADING FILTER"""
    try:
        if not csv_data:
            return [], "No data available", None
        
        df = pd.DataFrame(csv_data)
        
        if df.empty:
            return [], "No data available", None
        
        # 🔥 ENHANCED: Filter sites based on both agencies and clusters
        filtered_df = df.copy()
        
        # First filter by agencies if selected
        if selected_agencies and selected_agencies != ['none']:
            agency_col = None
            for col in ['agency_name', 'Agency', 'agency', 'AGENCY']:
                if col in df.columns:
                    agency_col = col
                    break
            
            if agency_col:
                filtered_df = filtered_df[filtered_df[agency_col].isin(selected_agencies)]
                logger.info(f"🔗 Filtered by agencies: {len(filtered_df)} records remaining")
        
        # Then filter by clusters if selected
        if selected_clusters and selected_clusters != ['none']:
            cluster_col = None
            for col in ['Cluster', 'cluster', 'CLUSTER']:
                if col in filtered_df.columns:
                    cluster_col = col
                    break
            
            if cluster_col:
                filtered_df = filtered_df[filtered_df[cluster_col].isin(selected_clusters)]
                logger.info(f"🔗 Filtered by clusters: {len(filtered_df)} records remaining")
        
        # Get unique sites from filtered data
        site_col = None
        for col in ['Site', 'site', 'SITE', 'site_name']:
            if col in filtered_df.columns:
                site_col = col
                break
        
        if site_col:
            unique_sites = filtered_df[site_col].dropna().astype(str).str.strip()
            unique_sites = unique_sites[unique_sites != ''].unique()
            site_options = [{'label': site, 'value': site} for site in sorted(unique_sites)]
            
            if selected_agencies or selected_clusters:
                placeholder = f"Select Site... ({len(site_options)} available)"
            else:
                placeholder = "Select Agency/Cluster first..."
                
            logger.info(f"   Updated site options: {len(site_options)} sites available")
            
            return site_options, placeholder, None  # 🔥 CLEAR: Reset site selection
        else:
            logger.warning("   No site column found")
            return [], "No site data found", None
            
    except Exception as e:
        logger.error(f"❌ Error updating site options: {str(e)}")
        return [], "Error loading sites", None


def parse_date_flexible(date_str):
    """
    Enhanced date parsing function that handles multiple formats including your CSV format
    """
    if not date_str or pd.isna(date_str):
        return None
    
    # Convert to string if not already
    date_str = str(date_str).strip()
    
    # List of possible date formats to try (based on your CSV data)
    date_formats = [
        '%Y-%m-%d',      # YYYY-MM-DD (common)
        '%d-%m-%Y',      # DD-MM-YYYY  
        '%d/%m/%Y',      # DD/MM/YYYY
        '%m/%d/%Y',      # MM/DD/YYYY
        '%Y/%m/%d',      # YYYY/MM/DD
        '%d.%m.%Y',      # DD.MM.YYYY
        '%Y.%m.%d',      # YYYY.MM.DD
        '%d %m %Y',      # DD MM YYYY (space separated)
        '%Y %m %d',      # YYYY MM DD (space separated)
    ]
    
    for fmt in date_formats:
        try:
            parsed_date = pd.to_datetime(date_str, format=fmt, errors='raise')
            return parsed_date
        except:
            continue
    
    # If all specific formats fail, try pandas' flexible parsing
    try:
        return pd.to_datetime(date_str, dayfirst=True, errors='coerce')
    except:
        return None

def debug_date_data(df):
    """
    Debug function to understand date data structure from your CSV
    """
    logger.info("🔍 DEBUG: Analyzing date data from CSV...")
    
    # Based on your CSV structure, look for 'date' column specifically
    date_columns = ['date', 'Date', 'DATE', 'transaction_date', 'Date_Time', 'cloud_upload_timestamp']
    found_date_col = None
    
    for col in date_columns:
        if col in df.columns:
            found_date_col = col
            logger.info(f"📅 Found date column: '{found_date_col}'")
            break
    
    if found_date_col:
        # Sample some date values
        sample_dates = df[found_date_col].dropna().head(10).tolist()
        logger.info(f"📋 Sample date values from '{found_date_col}': {sample_dates}")
        
        # Try to parse sample dates
        parsed_samples = []
        for date_val in sample_dates:
            parsed = parse_date_flexible(date_val)
            parsed_samples.append(f"{date_val} -> {parsed}")
        
        logger.info(f"🔄 Parsed samples: {parsed_samples}")
        
        # Check date range
        df_temp = df.copy()
        df_temp['date_parsed'] = df_temp[found_date_col].apply(parse_date_flexible)
        valid_dates = df_temp['date_parsed'].dropna()
        
        if len(valid_dates) > 0:
            min_date = valid_dates.min()
            max_date = valid_dates.max()
            logger.info(f"📊 Date range in CSV: {min_date} to {max_date}")
            logger.info(f"✅ Successfully parsed {len(valid_dates)}/{len(df)} dates")
            return found_date_col, min_date, max_date
        else:
            logger.warning("⚠️ No dates could be parsed!")
            return found_date_col, None, None
    else:
        logger.warning("❌ No date column found!")
        logger.info(f"Available columns: {list(df.columns)}")
        return None, None, None

# 🔥 FIXED: Updated filter callback with correct State parameters and comprehensive debugging
@callback(
    [Output('filtered-data-store', 'data'),
     Output('filtered-records', 'children'),
     Output('filtered-weight', 'children'),
     Output('filtered-contractors', 'children'),
     Output('filtered-machines', 'children'),
     Output('filtered-capacity', 'children')],
    [Input('apply-filters-btn', 'n_clicks'),
     Input('clear-all-filters-btn', 'n_clicks')],
    [State('agency-filter', 'value'),
     State('cluster-filter', 'value'),
     State('site-filter', 'value'),
     State('start-date-input', 'date'),  # 🔥 FIXED: Changed from 'value' to 'date'
     State('end-date-input', 'date'),    # 🔥 FIXED: Changed from 'value' to 'date'
     State('csv-data-store', 'data')],
    prevent_initial_call=True
)

def update_filtered_data(apply_clicks, clear_clicks, selected_agencies, selected_clusters, 
                        selected_sites, start_date, end_date, csv_data):
    """Update filtered data and statistics based on filter selections"""


    try:
        ctx = callback_context
        df = pd.DataFrame(csv_data)
        
        if df.empty:
            logger.warning("⚠️ Empty DataFrame in filter callback")
            return [], "0", "0.0 MT", "0", "0", "0"
        
        logger.info(f"🔄 FILTER DEBUG: Processing {len(df)} initial records")
        logger.info(f"📊 Filters: agencies={selected_agencies}, clusters={selected_clusters}, sites={selected_sites}")
        logger.info(f"📅 Date filter: START={start_date} (type: {type(start_date)}) END={end_date} (type: {type(end_date)})")
        
        # Debug date data first
        date_col, min_date, max_date = debug_date_data(df)
        
        # If clear button was clicked, return original data
        if ctx.triggered and ctx.triggered[0]['prop_id'] == 'clear-all-filters-btn.n_clicks':
            logger.info("🧹 Clearing all filters, returning original data")
            # Skip all filtering and go to stats calculation
            
        else:
            logger.info("🔍 Applying filters...")
            original_count = len(df)
            
            # Apply Agency filter (using your CSV structure)
            if selected_agencies and selected_agencies != ['none']:
                # Your CSV has 'agency_name' column
                if 'agency_name' in df.columns:
                    before_count = len(df)
                    df = df[df['agency_name'].isin(selected_agencies)]
                    logger.info(f"   🏢 Agency filter: {before_count} -> {len(df)} records")
                else:
                    logger.warning("   ❌ 'agency_name' column not found in CSV!")
            
            # Apply Cluster filter (using your CSV structure)
            if selected_clusters and selected_clusters != ['none']:
                # Your CSV has 'cluster' column
                if 'cluster' in df.columns:
                    before_count = len(df)
                    df = df[df['cluster'].isin(selected_clusters)]
                    logger.info(f"   🗂️ Cluster filter: {before_count} -> {len(df)} records")
                else:
                    logger.warning("   ❌ 'cluster' column not found in CSV!")
            
            # Apply Site filter (using your CSV structure)  
            if selected_sites and selected_sites != ['none']:
                # Your CSV has 'site_name' column
                if 'site_name' in df.columns:
                    before_count = len(df)
                    df = df[df['site_name'].isin(selected_sites)]
                    logger.info(f"   📍 Site filter: {before_count} -> {len(df)} records")
                else:
                    logger.warning("   ❌ 'site_name' column not found in CSV!")
            
            # 🔥 ENHANCED: Apply Date filter with comprehensive debugging
            if start_date or end_date:
                logger.info(f"📅 Applying date filter: {start_date} to {end_date}")
                
                if date_col and date_col in df.columns:
                    logger.info(f"📅 Using date column: '{date_col}'")
                    before_count = len(df)
                    
                    # Parse dates in the dataframe
                    df['date_parsed'] = df[date_col].apply(parse_date_flexible)
                    
                    # Debug parsed dates
                    valid_dates = df['date_parsed'].dropna()
                    invalid_dates = df['date_parsed'].isna().sum()
                    logger.info(f"📊 Date parsing: {len(valid_dates)} valid, {invalid_dates} invalid")
                    
                    if len(valid_dates) > 0:
                        logger.info(f"📅 Date range in filtered data: {valid_dates.min()} to {valid_dates.max()}")
                    
                    # Convert filter dates to pandas datetime
                    start_dt = None
                    end_dt = None
                    
                    if start_date:
                        try:
                            start_dt = pd.to_datetime(start_date)
                            logger.info(f"📅 Start date converted: {start_date} -> {start_dt}")
                        except Exception as e:
                            logger.error(f"❌ Error converting start date: {e}")
                    
                    if end_date:
                        try:
                            end_dt = pd.to_datetime(end_date)
                            logger.info(f"📅 End date converted: {end_date} -> {end_dt}")
                        except Exception as e:
                            logger.error(f"❌ Error converting end date: {e}")
                    
                    # Apply date filters step by step
                    date_mask = pd.Series([True] * len(df))  # Start with all True
                    
                    # Only keep rows with valid parsed dates
                    date_mask = date_mask & df['date_parsed'].notna()
                    valid_count = date_mask.sum()
                    logger.info(f"📅 Records with valid dates: {valid_count}")
                    
                    if start_dt is not None:
                        start_mask = df['date_parsed'] >= start_dt
                        date_mask = date_mask & start_mask
                        after_start = date_mask.sum()
                        logger.info(f"📅 After start date filter ({start_dt}): {after_start} records")
                    
                    if end_dt is not None:
                        end_mask = df['date_parsed'] <= end_dt
                        date_mask = date_mask & end_mask
                        after_end = date_mask.sum()
                        logger.info(f"📅 After end date filter ({end_dt}): {after_end} records")
                    
                    # Apply the final date mask
                    df = df[date_mask]
                    
                    # Clean up temporary column
                    df = df.drop('date_parsed', axis=1, errors='ignore')
                    
                    logger.info(f"📅 Date filter result: {before_count} -> {len(df)} records")
                    
                    if len(df) == 0:
                        logger.warning("⚠️ Date filter resulted in 0 records! This might be expected if date range is outside data range.")
                        
                else:
                    logger.warning(f"❌ No usable date column found for filtering!")
            
            logger.info(f"✅ Final filter result: {original_count} -> {len(df)} records")
        
        # Calculate filtered statistics using your CSV column names
        total_records = len(df)
        
        # Calculate weight with conversion to MT (using your CSV structure)
        total_weight = 0
        if 'net_weight_calculated' in df.columns:
            total_weight = df['net_weight_calculated'].fillna(0).sum()
            logger.info(f"⚖️ Weight calculation using 'net_weight_calculated': {total_weight} kg = {total_weight/1000:.2f} MT")
        elif 'net_weight' in df.columns:
            total_weight = df['net_weight'].fillna(0).sum()
            logger.info(f"⚖️ Weight calculation using 'net_weight': {total_weight} kg = {total_weight/1000:.2f} MT")
        
        # Calculate contractors (using your CSV structure)
        unique_contractors = 0
        if 'transfer_party_name' in df.columns:
            unique_contractors = df['transfer_party_name'].dropna().nunique()
            logger.info(f"👥 Contractors from 'transfer_party_name': {unique_contractors}")
        
        # Calculate machines/vehicles (using your CSV structure)
        unique_machines = 0
        if 'vehicle_no' in df.columns:
            unique_machines = df['vehicle_no'].dropna().nunique()
            logger.info(f"🚛 Vehicles from 'vehicle_no': {unique_machines}")
        
        # Calculate capacity (may not be in your CSV structure)
        total_capacity = 0
        capacity_cols = ['Total_capacity_per_day', 'capacity', 'Capacity']
        for col in capacity_cols:
            if col in df.columns:
                total_capacity = df[col].fillna(0).sum()
                logger.info(f"🔋 Capacity from column '{col}': {total_capacity}")
                break
        
        filtered_data = df.to_dict('records')
        
        logger.info(f"✅ FINAL STATS: {total_records} records, {total_weight/1000:.2f} MT, {unique_contractors} contractors, {unique_machines} vehicles")
        
        return (
            filtered_data,
            f"{total_records:,}",
            f"{total_weight/1000:,.2f} MT",
            str(unique_contractors),
            str(unique_machines),
            f"{total_capacity:,.0f}"
        )
        
    except Exception as e:
        logger.error(f"❌ Error in enhanced filter callback: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return [], "Error", "Error", "Error", "Error", "Error"

@callback(
    Output('csv-grid', 'rowData'),
    Input('filtered-data-store', 'data'),
    prevent_initial_call=True
)
def update_grid_with_filtered_data(filtered_data):
    """Update the ag-Grid with filtered data"""
    return filtered_data if filtered_data else []

def clear_all_filters(n_clicks):
    """Clear all filter selections when clear button is clicked"""
    if n_clicks:
        logger.info("🧹 Clearing all filter values")
        return None, None, None, None, None
    return None, None, None, None, None

@callback(
    Output('refresh-btn', 'children'),
    Input('refresh-btn', 'n_clicks'),
    prevent_initial_call=True
)
def refresh_data_feedback(n_clicks):
    """Provide visual feedback when refresh button is clicked"""
    if n_clicks:
        return "🔄 Refreshed!"
    return "🔄 Refresh"

@callback(
    Output('csv-grid', 'columnDefs'),
    Input('column-selector', 'value'),
    prevent_initial_call=True
)
def update_grid_columns(selected_columns):
    """Update grid columns based on dropdown selection"""
    if not selected_columns:
        df = get_processed_dataframe()
        return [{'field': c, 'filter': True, 'sortable': True, 'resizable': True} for c in df.columns]
    
    # Create column definitions for selected columns
    column_mapping = {
        'date': {'headerName': 'Date', 'width': 120, 'pinned': 'left', 'filter': 'agDateColumnFilter'},
        'agency_name': {'headerName': 'Agency', 'width': 150, 'filter': 'agSetColumnFilter'},
        'Agency': {'headerName': 'Agency', 'width': 150, 'filter': 'agSetColumnFilter'},
        'Cluster': {'headerName': 'Cluster', 'width': 120, 'filter': 'agSetColumnFilter'},
        'Site': {'headerName': 'Site', 'width': 120, 'filter': 'agSetColumnFilter'},
        'Sub_contractor': {'headerName': 'Sub-contractor', 'width': 150, 'filter': 'agSetColumnFilter'},
        'Machines': {'headerName': 'Machine', 'width': 120, 'filter': 'agSetColumnFilter'},
        'net_weight_calculated': {
            'headerName': 'Net Weight (kg)',
            'width': 140,
            'filter': 'agNumberColumnFilter',
            'valueFormatter': {'function': 'params.value ? params.value.toLocaleString() : "0"'}
        },
        'Total_capacity_per_day': {
            'headerName': 'Capacity/Day',
            'width': 130,
            'filter': 'agNumberColumnFilter',
            'valueFormatter': {'function': 'params.value ? params.value.toLocaleString() : "0"'}
        },
        'ticket_no': {'headerName': 'Ticket No', 'width': 120, 'filter': 'agTextColumnFilter'}
    }
    
    column_defs = []
    for col in selected_columns:
        base_def = {'field': col, 'filter': True, 'sortable': True, 'resizable': True}
        if col in column_mapping:
            base_def.update(column_mapping[col])
        column_defs.append(base_def)
    
    return column_defs

@callback(
    [Output('column-selector', 'value'), Output('csv-grid', 'dashGridOptions')],
    Input('reset-columns-btn', 'n_clicks'),
    prevent_initial_call=True
)
def reset_columns(n_clicks):
    """Reset column order and visibility to default"""
    if n_clicks:
        df = get_processed_dataframe()
        default_columns = list(df.columns) if not df.empty else []
        
        default_options = {
            "pagination": True,
            "paginationPageSize": 50,
            "paginationPageSizeSelector": [25, 50, 100, 200],
            "rowSelection": "multiple",
            "suppressRowClickSelection": True,
            "animateRows": True,
            "enableRangeSelection": True,
            "suppressDragLeaveHidesColumns": True,
            "suppressMovableColumns": False,
            "allowDragFromColumnsToolPanel": True,
            "sideBar": {
                "toolPanels": [
                    {
                        "id": "filters",
                        "labelDefault": "Filters",
                        "labelKey": "filters",
                        "iconKey": "filter",
                        "toolPanel": "agFiltersToolPanel"
                    },
                    {
                        "id": "columns",
                        "labelDefault": "Columns",
                        "labelKey": "columns", 
                        "iconKey": "columns",
                        "toolPanel": "agColumnsToolPanel",
                        "toolPanelParams": {
                            "suppressValues": True,
                            "suppressPivots": True,
                            "suppressPivotMode": True,
                            "suppressRowGroups": True
                        }
                    }
                ]
            }
        }
        
        return default_columns, default_options
    return [], {}

@callback(
    Output('current-time', 'children'),
    Input('time-interval', 'n_intervals')
)
def update_time(n_intervals):
    """Update current time display"""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

@callback(
    Output('csv-grid', 'exportDataAsCsv'),
    Input('export-btn', 'n_clicks'),
    prevent_initial_call=True
)
def export_csv(n_clicks):
    """Export current grid data to CSV when export button is clicked"""
    if n_clicks:
        return True
    return False

def build_enhanced_dashboard(theme_name="dark", user_data=None, active_tab="tab-dashboard"):
    """Build the enhanced dashboard layout with properly connected filters"""
    if not user_data:
        user_data = {
            "name": "Administrator",
            "email": "admin@swacchaandhra.gov.in",
            "role": "administrator",
            "picture": "/assets/img/default-avatar.png",
            "auth_method": "demo"
        }
    
    page_titles = {
        "tab-dashboard": "Dashboard",
        "tab-analytics": "Data Analytics", 
        "tab-reports": "Reports",
        "tab-reviews": "Reviews",
        "tab-upload": "Upload",
        "tab-forecasting": "Forecasting"
    }
    
    page_icons = {
        "tab-dashboard": "📊",
        "tab-analytics": "🔍",
        "tab-reports": "📋", 
        "tab-reviews": "⭐",
        "tab-upload": "📤",
        "tab-forecasting": "🔮"
    }
    
    title = page_titles.get(active_tab, "Dashboard")
    icon = page_icons.get(active_tab, "📊")
    
    return create_dash_dashboard_layout(title, icon, theme_name)

def register_enhanced_csv_routes(server):
    """Register enhanced CSV data routes with dash_ag_grid integration"""
    
    @server.route('/api/csv-data-enhanced')
    def get_enhanced_csv_data():
        """Enhanced API endpoint to get CSV data for dash_ag_grid"""
        if not session.get('swaccha_session_id'):
            return {'error': 'Authentication required'}, 401
        
        try:
            df = get_processed_dataframe()
            
            if df.empty:
                return flask.jsonify({
                    'error': 'No CSV data available',
                    'message': 'CSV file not found or empty'
                })
            
            # Calculate basic statistics
            total_records = len(df)
            total_weight = 0
            if 'net_weight_calculated' in df.columns:
                total_weight = df['net_weight'].fillna(0).sum()
            
            unique_contractors = 0
            if 'Sub_contractor' in df.columns:
                unique_contractors = df['Sub_contractor'].dropna().nunique()
            
            unique_machines = 0
            if 'Machines' in df.columns:
                unique_machines = df['Machines'].dropna().nunique()
            
            total_capacity = 0
            if 'Total_capacity_per_day' in df.columns:
                total_capacity = df['Total_capacity_per_day'].fillna(0).sum()
            
            response_data = {
                'success': True,
                'total_records': total_records,
                'total_weight': f"{total_weight/1000:,.2f} MT",
                'unique_contractors': unique_contractors,
                'unique_machines': unique_machines,
                'total_capacity': f"{total_capacity:,.0f}",
                'records': df.to_dict('records'),
                'columns_detected': {
                    'date_column': 'date',
                    'weight_column': 'net_weight_calculated',
                    'contractor_column': 'Sub_contractor',
                    'machine_column': 'Machines',
                    'capacity_column': 'Total_capacity_per_day'
                }
            }
            
            logger.info(f"✅ Enhanced CSV API: {total_records} records loaded for dash_ag_grid")
            
            return flask.jsonify(response_data)
            
        except Exception as e:
            logger.error(f"❌ Error in enhanced CSV API: {e}")
            return flask.jsonify({
                'error': 'Error processing CSV data',
                'message': str(e)
            }), 500

def register_dashboard_flask_routes(server):
    """Register dashboard page routes with dash_ag_grid integration"""
    pass

def ensure_upload_directory(server):
    """Create upload directory if it doesn't exist"""
    upload_path = "/tmp/uploads"
    os.makedirs(upload_path, exist_ok=True)
    return upload_path

def configure_upload_settings(server):
    """Configure upload settings"""
    server.config.update({
        'UPLOAD_FOLDER': '/tmp/uploads',
        'MAX_CONTENT_LENGTH': 50 * 1024 * 1024,
        'UPLOAD_EXTENSIONS': {'.pdf', '.csv', '.xlsx', '.xls'},
        'SECRET_KEY': os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production-' + str(hash(os.getcwd())))
    })

def generate_sample_data():
    """Generate sample data for dashboard components"""
    return {
        "last_updated": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "total_collections": random.randint(1500, 2500),
        "efficiency_score": random.randint(85, 98),
        "active_vehicles": random.randint(45, 75)
    }

# Export all the functions that main.py expects
__all__ = [
    'build_enhanced_dashboard',
    'register_enhanced_csv_routes',
    'register_dashboard_flask_routes',
    'get_current_theme',
    'ensure_upload_directory',
    'configure_upload_settings',
    'get_embedded_csv_data',
    'get_filter_options_from_embedded_data',
    'generate_sample_data',
    'get_processed_dataframe'
]