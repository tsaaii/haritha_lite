# data_loader.py
"""
Fixed CSV Data Loader for Waste Management Dashboard
Integrates properly with consolidated callbacks
"""

import pandas as pd
import logging
from dash import html, dash_table, dcc
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os

logger = logging.getLogger(__name__)

# Global data storage
_cached_data = None

def load_csv_data():
    """
    Load CSV data from file or browser API
    Returns a DataFrame with waste management data
    """
    try:
        # Try to load from uploaded file first
        csv_files = []
        
        # Check common CSV file locations
        possible_paths = [
            'waste_management_data_updated.csv',
            'data/waste_management_data_updated.csv', 
            '/tmp/uploads/waste_management_data_updated.csv',
            '/tmp/uploads/dash_/uploads/waste_management_data_updated.csv'
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                csv_files.append(path)
        
        if csv_files:
            # Load the first found CSV file
            csv_path = csv_files[0]
            logger.info(f"Loading CSV from: {csv_path}")
            
            # Try different encodings
            encodings = ['utf-8', 'latin-1', 'cp1252']
            df = None
            
            for encoding in encodings:
                try:
                    df = pd.read_csv(csv_path, encoding=encoding)
                    logger.info(f"✅ Successfully loaded CSV with {encoding} encoding")
                    break
                except UnicodeDecodeError:
                    logger.warning(f"Failed to load with {encoding} encoding, trying next...")
                    continue
                except Exception as e:
                    logger.error(f"Error loading with {encoding}: {e}")
                    continue
            
            if df is None:
                logger.error("Failed to load CSV with any encoding")
                return get_sample_data()
            
            # Ensure Date column is datetime
            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            
            # Add derived columns
            if 'weight' in df.columns:
                df['weight_tons'] = df['weight'] / 1000
            
            # Clean data - remove rows with missing essential columns
            essential_columns = ['agency', 'cluster', 'site']
            for col in essential_columns:
                if col in df.columns:
                    df = df.dropna(subset=[col])
                    # Convert to string and clean
                    df[col] = df[col].astype(str).str.strip().str.lower()
            
            logger.info(f"Successfully loaded and cleaned {len(df)} records from {csv_path}")
            return df
        
        else:
            # No CSV file found, return sample data
            logger.warning("No CSV file found, using sample data")
            return get_sample_data()
        
    except Exception as e:
        logger.error(f"Error loading CSV data: {e}")
        return get_sample_data()

def get_sample_data():
    """Return sample data if CSV file is not available"""
    sample_data = [
        {"Date": "2025-05-23", "agency": "madanapalle", "site": "madanapalle", "cluster": "MM", 
         "weight": 11540, "vehicle": "AP39VB2709", "time": "03:37:22 PM", "waste_type": "MSW", "trip_no": 34},
        {"Date": "2025-05-23", "agency": "madanapalle", "site": "madanapalle", "cluster": "MM", 
         "weight": 17350, "vehicle": "AP39UN2025", "time": "03:20:54 PM", "waste_type": "MSW", "trip_no": 33},
        {"Date": "2025-05-23", "agency": "madanapalle", "site": "madanapalle", "cluster": "MM", 
         "weight": 12610, "vehicle": "AP39VB2709", "time": "03:10:13 PM", "waste_type": "MSW", "trip_no": 32},
        {"Date": "2025-06-05", "agency": "donthalli", "site": "donthalli", "cluster": "NMC", 
         "weight": 23390, "vehicle": "AP04UB0825", "time": "07:42:41 PM", "waste_type": "MSW", "trip_no": 229},
        {"Date": "2025-06-05", "agency": "donthalli", "site": "donthalli", "cluster": "NMC", 
         "weight": 19570, "vehicle": "AP39VB4518", "time": "07:33:40 PM", "waste_type": "MSW", "trip_no": 228},
        {"Date": "2025-06-04", "agency": "madanapalle", "site": "madanapalle", "cluster": "MM", 
         "weight": 7940, "vehicle": "AP39UM8487", "time": "04:27:11 PM", "waste_type": "MSW", "trip_no": 200},
        {"Date": "2025-06-04", "agency": "visakhapatnam", "site": "visakhapatnam", "cluster": "VMRC", 
         "weight": 15620, "vehicle": "AP39UC5432", "time": "02:15:30 PM", "waste_type": "MSW", "trip_no": 201},
        {"Date": "2025-06-03", "agency": "hyderabad", "site": "hyderabad", "cluster": "GHMC", 
         "weight": 28760, "vehicle": "TS09FC8765", "time": "09:45:15 AM", "waste_type": "MSW", "trip_no": 156},
        {"Date": "2025-06-03", "agency": "tirupati", "site": "tirupati", "cluster": "TTD", 
         "weight": 13240, "vehicle": "AP07RB2398", "time": "11:30:45 AM", "waste_type": "MSW", "trip_no": 89},
        {"Date": "2025-06-02", "agency": "guntur", "site": "guntur", "cluster": "GMC", 
         "weight": 21580, "vehicle": "AP16DB9087", "time": "06:20:12 PM", "waste_type": "MSW", "trip_no": 134}
    ]
    
    df = pd.DataFrame(sample_data)
    df['Date'] = pd.to_datetime(df['Date'])
    df['weight_tons'] = df['weight'] / 1000
    
    logger.info(f"Using sample data with {len(df)} records")
    return df

def get_cached_data():
    """Get cached data or load fresh"""
    global _cached_data
    if _cached_data is None:
        _cached_data = load_csv_data()
    return _cached_data

def get_global_data():
    """Alias for get_cached_data() - used by consolidated callbacks"""
    return get_cached_data()

def refresh_cached_data():
    """Force refresh of cached data"""
    global _cached_data
    _cached_data = load_csv_data()
    return _cached_data

def get_filter_options(df):
    """Get filter options from dataframe - with debug logging"""
    try:
        if df.empty:
            return {
                'agencies': [{'label': 'All Agencies', 'value': 'all'}],
                'sites': [{'label': 'All Sites', 'value': 'all'}],
                'clusters': [{'label': 'All Clusters', 'value': 'all'}]
            }
        
        # Debug: Show what's actually in each column
        logger.info(f"🔍 Checking columns for filter options...")
        
        agencies = []
        sites = []
        clusters = []
        
        if 'agency' in df.columns:
            agencies = sorted(df['agency'].dropna().unique())
            logger.info(f"📊 Found in 'agency' column: {agencies}")
        else:
            logger.warning("❌ No 'agency' column found!")
            
        if 'site' in df.columns:
            sites = sorted(df['site'].dropna().unique())
            logger.info(f"📍 Found in 'site' column: {sites}")
        else:
            logger.warning("❌ No 'site' column found!")
            
        if 'cluster' in df.columns:
            clusters = sorted(df['cluster'].dropna().unique())
            logger.info(f"🗺️ Found in 'cluster' column: {clusters}")
        else:
            logger.warning("❌ No 'cluster' column found!")
        
        logger.info(f"✅ Final filter options: {len(agencies)} agencies, {len(clusters)} clusters, {len(sites)} sites")
        
        return {
            'agencies': [{'label': 'All Agencies', 'value': 'all'}] + 
                       [{'label': agency.title(), 'value': agency} for agency in agencies],
            'sites': [{'label': 'All Sites', 'value': 'all'}] + 
                    [{'label': site.title(), 'value': site} for site in sites],
            'clusters': [{'label': 'All Clusters', 'value': 'all'}] + 
                       [{'label': cluster.title(), 'value': cluster} for cluster in clusters]
        }
    except Exception as e:
        logger.error(f"Error generating filter options: {e}")
        return {
            'agencies': [{'label': 'All Agencies', 'value': 'all'}],
            'sites': [{'label': 'All Sites', 'value': 'all'}],
            'clusters': [{'label': 'All Clusters', 'value': 'all'}]
        }

def get_dynamic_filter_options(df):
    """Alias for get_filter_options() - maintains compatibility"""
    return get_filter_options(df)

def filter_data(df, agency='all', cluster='all', site='all', start_date=None, end_date=None):
    """
    Apply filters to dataframe using your CSV columns directly
    """
    if df.empty:
        return df
    
    try:
        filtered_df = df.copy()
        
        # Apply agency filter using 'agency' column
        if agency and agency != 'all' and 'agency' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['agency'] == agency]
        
        # Apply cluster filter using 'cluster' column
        if cluster and cluster != 'all' and 'cluster' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['cluster'] == cluster]
        
        # Apply site filter using 'site' column
        if site and site != 'all' and 'site' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['site'] == site]
        
        # Apply date filters
        if 'Date' in filtered_df.columns:
            if start_date:
                if isinstance(start_date, str):
                    start_date = pd.to_datetime(start_date)
                filtered_df = filtered_df[pd.to_datetime(filtered_df['Date']) >= start_date]
            
            if end_date:
                if isinstance(end_date, str):
                    end_date = pd.to_datetime(end_date)
                filtered_df = filtered_df[pd.to_datetime(filtered_df['Date']) <= end_date]
        
        logger.info(f"Filtered data: {len(filtered_df)} records from {len(df)} total")
        return filtered_df
        
    except Exception as e:
        logger.error(f"Error filtering data: {e}")
        return df

def apply_filters_to_data(df, agency='all', cluster='all', site='all', start_date=None, end_date=None):
    """Alias for filter_data() - maintains compatibility"""
    return filter_data(df, agency, cluster, site, start_date, end_date)

def create_filtered_data_display(filtered_df, theme):
    """
    Create display component for filtered data - used by consolidated callbacks
    """
    try:
        if filtered_df.empty:
            return html.Div([
                html.Div("📭 No data found", style={
                    "textAlign": "center",
                    "padding": "3rem",
                    "color": theme["text_secondary"],
                    "fontSize": "1.2rem",
                    "backgroundColor": theme["card_bg"],
                    "borderRadius": "12px",
                    "border": f"2px dashed {theme.get('accent_bg', '#444')}"
                })
            ])
        
        # Calculate summary statistics using your CSV columns
        total_records = len(filtered_df)
        total_weight = filtered_df['Net Weight'].sum() if 'Net Weight' in filtered_df.columns else 0
        weight_tons = total_weight / 1000
        unique_agencies = filtered_df['agency'].nunique() if 'agency' in filtered_df.columns else 0
        unique_vehicles = filtered_df['Vehicle No'].nunique() if 'Vehicle No' in filtered_df.columns else 0
        
        # Create summary cards
        summary_cards = html.Div([
            # Total Records Card
            html.Div([
                html.Div("📊", style={"fontSize": "2rem", "marginBottom": "0.5rem"}),
                html.Div(f"{total_records:,}", style={
                    "fontSize": "1.5rem", 
                    "fontWeight": "bold",
                    "color": theme["brand_primary"]
                }),
                html.Div("Total Records", style={
                    "fontSize": "0.9rem",
                    "color": theme["text_secondary"]
                })
            ], style={
                "backgroundColor": theme["card_bg"],
                "padding": "1.5rem",
                "borderRadius": "12px",
                "textAlign": "center",
                "border": f"1px solid {theme.get('border_light', '#333')}"
            }),
            
            # Total Weight Card
            html.Div([
                html.Div("⚖️", style={"fontSize": "2rem", "marginBottom": "0.5rem"}),
                html.Div(f"{weight_tons:.1f}", style={
                    "fontSize": "1.5rem", 
                    "fontWeight": "bold",
                    "color": theme["brand_primary"]
                }),
                html.Div("Total Tons", style={
                    "fontSize": "0.9rem",
                    "color": theme["text_secondary"]
                })
            ], style={
                "backgroundColor": theme["card_bg"],
                "padding": "1.5rem",
                "borderRadius": "12px",
                "textAlign": "center",
                "border": f"1px solid {theme.get('border_light', '#333')}"
            }),
            
            # Agencies Card
            html.Div([
                html.Div("🏢", style={"fontSize": "2rem", "marginBottom": "0.5rem"}),
                html.Div(f"{unique_agencies}", style={
                    "fontSize": "1.5rem", 
                    "fontWeight": "bold",
                    "color": theme["brand_primary"]
                }),
                html.Div("Agencies", style={
                    "fontSize": "0.9rem",
                    "color": theme["text_secondary"]
                })
            ], style={
                "backgroundColor": theme["card_bg"],
                "padding": "1.5rem",
                "borderRadius": "12px",
                "textAlign": "center",
                "border": f"1px solid {theme.get('border_light', '#333')}"
            }),
            
            # Vehicles Card
            html.Div([
                html.Div("🚛", style={"fontSize": "2rem", "marginBottom": "0.5rem"}),
                html.Div(f"{unique_vehicles}", style={
                    "fontSize": "1.5rem", 
                    "fontWeight": "bold",
                    "color": theme["brand_primary"]
                }),
                html.Div("Vehicles", style={
                    "fontSize": "0.9rem",
                    "color": theme["text_secondary"]
                })
            ], style={
                "backgroundColor": theme["card_bg"],
                "padding": "1.5rem",
                "borderRadius": "12px",
                "textAlign": "center",
                "border": f"1px solid {theme.get('border_light', '#333')}"
            })
        ], style={
            "display": "grid",
            "gridTemplateColumns": "repeat(auto-fit, minmax(200px, 1fr))",
            "gap": "1rem",
            "marginBottom": "2rem"
        })
        
        # Create data table (showing last 10 records)
        display_df = filtered_df.tail(10).copy()
        
        # Format columns for display using your CSV structure
        if 'Date' in display_df.columns:
            display_df['Date'] = pd.to_datetime(display_df['Date']).dt.strftime('%Y-%m-%d')
        if 'Net Weight' in display_df.columns:
            display_df['Weight (kg)'] = display_df['Net Weight'].astype(str)
            display_df = display_df.drop('Net Weight', axis=1)
        
        # Select columns to display from your CSV
        columns_to_show = ['Date', 'agency', 'site', 'cluster', 'Weight (kg)', 'Vehicle No']
        available_columns = [col for col in columns_to_show if col in display_df.columns]
        
        if available_columns:
            display_df = display_df[available_columns]
        
        data_table = dash_table.DataTable(
            data=display_df.to_dict('records'),
            columns=[{"name": col.title(), "id": col} for col in display_df.columns],
            style_table={'overflowX': 'auto'},
            style_cell={
                'backgroundColor': theme["card_bg"],
                'color': theme["text_primary"],
                'border': f'1px solid {theme.get("border_light", "#333")}',
                'textAlign': 'left',
                'padding': '12px',
                'fontFamily': 'Inter, sans-serif'
            },
            style_header={
                'backgroundColor': theme["brand_primary"],
                'color': 'white',
                'fontWeight': 'bold',
                'border': f'1px solid {theme["brand_primary"]}'
            },
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': theme.get("accent_bg", "#1a1a1a")
                }
            ],
            page_size=10
        )
        
        return html.Div([
            summary_cards,
            html.H4("Recent Records", style={
                "color": theme["text_primary"],
                "marginBottom": "1rem"
            }),
            data_table
        ])
        
    except Exception as e:
        logger.error(f"Error creating filtered data display: {e}")
        return html.Div([
            html.Div("❌ Error displaying data", style={
                "color": "#ff4444",
                "textAlign": "center",
                "padding": "2rem",
                "backgroundColor": theme["card_bg"],
                "borderRadius": "12px"
            }),
            html.Div(f"Error: {str(e)}", style={
                "color": theme["text_secondary"],
                "fontSize": "0.9rem",
                "textAlign": "center",
                "marginTop": "0.5rem"
            })
        ])

# Utility function to check if CSV file exists
def check_csv_file():
    """Check if CSV file exists and return info"""
    possible_paths = [
        'waste_management_data_updated.csv',
        'data/waste_management_data_updated.csv', 
        '/tmp/uploads/waste_management_data_updated.csv',
        '/tmp/uploads/dash_/uploads/waste_management_data_updated.csv'
    ]
    
    found_files = []
    for path in possible_paths:
        if os.path.exists(path):
            size = os.path.getsize(path)
            found_files.append({
                'path': path,
                'size': size,
                'size_mb': round(size / (1024 * 1024), 2)
            })
    
    return found_files

# Load data immediately when module is imported
logger.info("🔄 Loading CSV data...")
try:
    csv_files = check_csv_file()
    if csv_files:
        logger.info(f"📁 Found CSV files: {[f['path'] for f in csv_files]}")
    else:
        logger.warning("📁 No CSV files found, will use sample data")
    
    # Pre-load data
    _cached_data = load_csv_data()
    logger.info(f"✅ Data loaded successfully: {len(_cached_data)} records")
    
except Exception as e:
    logger.error(f"❌ Error during initial data load: {e}")
    _cached_data = get_sample_data()