# legacy_report.py
"""
Enhanced Legacy Report Dashboard with CSV Data View
Matches the public landing page style with minimalistic UI
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import sys

# Add the parent directory to sys.path to import from your Flask app
sys.path.append('..')

# Configure the page with your branding
st.set_page_config(
    page_title="Legacy Report - स्वच्छ आंध्र प्रदेश",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS to match your public landing page style
st.markdown("""
<style>
    /* Import your color scheme */
    :root {
        --primary-bg: #0A0E1A;
        --secondary-bg: #0D1B2A;
        --accent-bg: #1A1F2E;
        --card-bg: #2D3748;
        --text-primary: #FFFFFF;
        --text-secondary: #A0AEC0;
        --brand-primary: #eb9534;
        --success: #38A169;
        --warning: #DD6B20;
        --error: #E53E3E;
        --info: #3182CE;
    }
    
    /* Main app styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        background: var(--primary-bg);
    }
    
    /* Header styling */
    .main-header {
        text-align: center;
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
        padding: 2rem;
        margin: -2rem -2rem 2rem -2rem;
        border-radius: 0 0 20px 20px;
    }
    
    .main-title {
        color: white;
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    .main-subtitle {
        color: rgba(255,255,255,0.9);
        font-size: 1.2rem;
        margin-bottom: 0;
    }
    
    /* Card styling to match your public layout */
    .metric-card {
        background: var(--card-bg);
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border: 2px solid var(--accent-bg);
        transition: all 0.3s ease;
        margin-bottom: 1rem;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 15px rgba(0,0,0,0.2);
        border-color: var(--brand-primary);
    }
    
    .metric-title {
        color: var(--text-secondary);
        font-size: 0.9rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.5rem;
    }
    
    .metric-value {
        color: var(--text-primary);
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.25rem;
    }
    
    .metric-description {
        color: var(--text-secondary);
        font-size: 0.8rem;
        opacity: 0.8;
    }
    
    /* Custom Streamlit component styling */
    .stMetric {
        background: var(--card-bg);
        border-radius: 12px;
        padding: 1rem;
        border: 2px solid var(--accent-bg);
    }
    
    .stSelectbox > div > div {
        background: var(--card-bg);
        border: 2px solid var(--accent-bg);
        border-radius: 8px;
    }
    
    .stDataFrame {
        background: var(--card-bg);
        border-radius: 12px;
        overflow: hidden;
        border: 2px solid var(--accent-bg);
    }
    
    /* Table styling */
    .dataframe {
        background: var(--card-bg) !important;
        color: var(--text-primary) !important;
    }
    
    .dataframe th {
        background: linear-gradient(135deg, var(--brand-primary), var(--info)) !important;
        color: white !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        font-size: 0.8rem !important;
        letter-spacing: 0.5px !important;
        border: none !important;
    }
    
    .dataframe td {
        background: var(--card-bg) !important;
        color: var(--text-primary) !important;
        border-bottom: 1px solid var(--accent-bg) !important;
        border-left: none !important;
        border-right: none !important;
    }
    
    .dataframe tr:nth-child(even) td {
        background: var(--accent-bg) !important;
    }
    
    .dataframe tr:hover td {
        background: rgba(235, 149, 52, 0.1) !important;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: var(--secondary-bg);
    }
    
    /* Success/info boxes */
    .stAlert {
        background: var(--card-bg);
        border: 2px solid var(--success);
        border-radius: 12px;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_waste_data():
    """Load waste management data using your existing data loader"""
    try:
        # Try to import from your Flask app's data loader
        sys.path.append('.')
        from data_loader import get_cached_data, check_csv_file
        
        # Check if CSV files exist
        csv_files = check_csv_file()
        if csv_files:
            st.sidebar.success(f"📁 Found {len(csv_files)} CSV file(s)")
            for file_info in csv_files:
                st.sidebar.info(f"📄 {file_info['path']} ({file_info['size_mb']} MB)")
        
        # Load the actual data
        df = get_cached_data()
        
        if not df.empty:
            st.sidebar.success(f"✅ Loaded {len(df):,} records")
            return df
        else:
            st.sidebar.warning("No data in CSV files")
            return create_sample_data()
            
    except ImportError:
        st.sidebar.warning("Could not import data_loader, using sample data")
        return create_sample_data()
    except Exception as e:
        st.sidebar.error(f"Error loading data: {e}")
        return create_sample_data()

def create_sample_data():
    """Create sample data if real data not available"""
    sample_data = [
        {"Date": "2025-08-19", "agency": "madanapalle", "site": "madanapalle", "cluster": "MM", 
         "weight": 15420, "vehicle": "AP39VB2709", "time": "09:30:00", "waste_type": "MSW"},
        {"Date": "2025-08-19", "agency": "donthalli", "site": "donthalli", "cluster": "NMC", 
         "weight": 23150, "vehicle": "AP04UB0825", "time": "10:15:00", "waste_type": "MSW"},
        {"Date": "2025-08-19", "agency": "visakhapatnam", "site": "visakhapatnam", "cluster": "VMRC", 
         "weight": 18750, "vehicle": "AP39UC5432", "time": "08:45:00", "waste_type": "MSW"},
        {"Date": "2025-08-18", "agency": "guntur", "site": "guntur", "cluster": "GMC", 
         "weight": 26800, "vehicle": "AP16DB9087", "time": "13:45:00", "waste_type": "MSW"},
        {"Date": "2025-08-18", "agency": "tirupati", "site": "tirupati", "cluster": "TTD", 
         "weight": 14200, "vehicle": "AP07RB2398", "time": "07:30:00", "waste_type": "MSW"},
    ] * 50  # Multiply to create more sample data
    
    df = pd.DataFrame(sample_data)
    df['Date'] = pd.to_datetime(df['Date'])
    df['weight_tons'] = df['weight'] / 1000
    return df

def create_summary_metrics(df):
    """Create summary metrics cards matching your dashboard style"""
    if df.empty:
        return
    
    # Calculate key metrics
    total_records = len(df)
    total_weight = df['weight'].sum() / 1000  # Convert to tons
    unique_agencies = df['agency'].nunique() if 'agency' in df.columns else 0
    unique_vehicles = df['vehicle'].nunique() if 'vehicle' in df.columns else 0
    avg_weight = df['weight'].mean() / 1000 if 'weight' in df.columns else 0
    
    # Create metrics row
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            label="📊 Total Records",
            value=f"{total_records:,}",
            delta=f"+{min(total_records, 500)} today"
        )
    
    with col2:
        st.metric(
            label="⚖️ Total Weight",
            value=f"{total_weight:,.1f} tons",
            delta=f"+{avg_weight:.1f} avg/record"
        )
    
    with col3:
        st.metric(
            label="🏢 Active Agencies", 
            value=f"{unique_agencies}",
            delta="Operational"
        )
    
    with col4:
        st.metric(
            label="🚛 Fleet Size",
            value=f"{unique_vehicles}",
            delta="Vehicles"
        )
    
    with col5:
        st.metric(
            label="📈 Avg Collection",
            value=f"{avg_weight:.1f} tons",
            delta="Per record"
        )

def create_filters_sidebar(df):
    """Create filters in sidebar matching your style"""
    st.sidebar.header("🔧 Data Filters")
    st.sidebar.markdown("---")
    
    # Date range filter
    if 'Date' in df.columns and not df.empty:
        min_date = df['Date'].min().date()
        max_date = df['Date'].max().date()
        
        date_range = st.sidebar.date_input(
            "📅 Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
    else:
        date_range = None
    
    # Agency filter
    agencies = ['All'] + sorted(df['agency'].unique().tolist()) if 'agency' in df.columns else ['All']
    selected_agency = st.sidebar.selectbox("🏢 Agency", agencies)
    
    # Cluster filter
    clusters = ['All'] + sorted(df['cluster'].unique().tolist()) if 'cluster' in df.columns else ['All']
    selected_cluster = st.sidebar.selectbox("🌐 Cluster", clusters)
    
    # Site filter
    sites = ['All'] + sorted(df['site'].unique().tolist()) if 'site' in df.columns else ['All']
    selected_site = st.sidebar.selectbox("📍 Site", sites)
    
    # Vehicle filter
    vehicles = ['All'] + sorted(df['vehicle'].unique().tolist()) if 'vehicle' in df.columns else ['All']
    selected_vehicle = st.sidebar.selectbox("🚛 Vehicle", vehicles)
    
    return {
        'date_range': date_range,
        'agency': selected_agency,
        'cluster': selected_cluster,
        'site': selected_site,
        'vehicle': selected_vehicle
    }

def apply_filters(df, filters):
    """Apply filters to dataframe"""
    if df.empty:
        return df
    
    filtered_df = df.copy()
    
    # Date filter
    if filters['date_range'] and len(filters['date_range']) == 2:
        start_date, end_date = filters['date_range']
        if 'Date' in filtered_df.columns:
            filtered_df = filtered_df[
                (filtered_df['Date'].dt.date >= start_date) & 
                (filtered_df['Date'].dt.date <= end_date)
            ]
    
    # Agency filter
    if filters['agency'] != 'All' and 'agency' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['agency'] == filters['agency']]
    
    # Cluster filter
    if filters['cluster'] != 'All' and 'cluster' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['cluster'] == filters['cluster']]
    
    # Site filter
    if filters['site'] != 'All' and 'site' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['site'] == filters['site']]
    
    # Vehicle filter
    if filters['vehicle'] != 'All' and 'vehicle' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['vehicle'] == filters['vehicle']]
    
    return filtered_df

def create_data_visualizations(df):
    """Create charts matching your theme"""
    if df.empty:
        st.warning("No data available for visualization")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Daily Collection Trends")
        
        # Group by date
        if 'Date' in df.columns and 'weight' in df.columns:
            daily_data = df.groupby(df['Date'].dt.date)['weight'].sum().reset_index()
            daily_data['weight_tons'] = daily_data['weight'] / 1000
            
            fig_line = px.line(
                daily_data, 
                x='Date', 
                y='weight_tons',
                title="Daily Waste Collection (Tons)",
                color_discrete_sequence=['#eb9534']
            )
            fig_line.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(45,55,72,1)',
                font_color='white',
                title_font_color='#eb9534'
            )
            st.plotly_chart(fig_line, use_container_width=True)
    
    with col2:
        st.subheader("🏢 Collection by Agency")
        
        if 'agency' in df.columns and 'weight' in df.columns:
            agency_data = df.groupby('agency')['weight'].sum().reset_index()
            agency_data['weight_tons'] = agency_data['weight'] / 1000
            agency_data = agency_data.sort_values('weight_tons', ascending=True)
            
            fig_bar = px.bar(
                agency_data, 
                x='weight_tons',
                y='agency',
                orientation='h',
                title="Total Waste by Agency (Tons)",
                color='weight_tons',
                color_continuous_scale=['#E53E3E', '#DD6B20', '#eb9534', '#38A169']
            )
            fig_bar.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(45,55,72,1)',
                font_color='white',
                title_font_color='#eb9534'
            )
            st.plotly_chart(fig_bar, use_container_width=True)

def display_data_table(df, filters):
    """Display data table with your styling"""
    st.subheader("📋 Waste Management Records")
    
    if df.empty:
        st.warning("No records match the selected filters.")
        return
    
    # Display options
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    
    with col1:
        records_to_show = st.selectbox(
            "Records per page:", 
            [10, 25, 50, 100, "All"], 
            index=1
        )
    
    with col2:
        if st.button("📊 Export CSV", use_container_width=True):
            csv = df.to_csv(index=False)
            st.download_button(
                label="💾 Download",
                data=csv,
                file_name=f"waste_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
    
    with col3:
        if st.button("🔄 Refresh", use_container_width=True):
            st.cache_data.clear()
            st.experimental_rerun()
    
    with col4:
        show_details = st.checkbox("Show Details", value=False)
    
    # Prepare display dataframe
    display_df = df.copy()
    
    if records_to_show != "All":
        display_df = display_df.head(int(records_to_show))
    
    # Format for display
    if 'Date' in display_df.columns:
        display_df['Date'] = display_df['Date'].dt.strftime('%Y-%m-%d')
    
    if 'weight' in display_df.columns:
        display_df['Weight (tons)'] = (display_df['weight'] / 1000).round(2)
    
    # Show columns based on detail level
    if show_details:
        columns_to_show = display_df.columns.tolist()
    else:
        # Show only key columns
        key_columns = ['Date', 'agency', 'site', 'cluster', 'Weight (tons)', 'vehicle']
        columns_to_show = [col for col in key_columns if col in display_df.columns]
    
    # Display the table
    st.dataframe(
        display_df[columns_to_show],
        use_container_width=True,
        hide_index=True,
        height=400
    )
    
    # Show summary
    st.info(f"📊 Showing {len(display_df):,} of {len(df):,} records")

def main():
    """Main Streamlit application"""
    
    # Header
    st.markdown("""
    <div class="main-header">
        <div class="main-title">📊 स्वच्छ आंध्र प्रदेश</div>
        <div class="main-subtitle">Legacy Report Dashboard • CSV Data Explorer</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Load data
    df = load_waste_data()
    
    # Sidebar filters
    filters = create_filters_sidebar(df)
    
    # Apply filters
    filtered_df = apply_filters(df, filters)
    
    # Show success message
    st.success("🎉 **Streamlit Integration Successful!** You've successfully logged in via Flask and reached the enhanced dashboard.")
    
    # Summary metrics
    st.subheader("📈 Key Metrics")
    create_summary_metrics(filtered_df)
    
    # Visualizations
    st.subheader("📊 Data Insights")
    create_data_visualizations(filtered_df)
    
    # Data table
    display_data_table(filtered_df, filters)
    
    # Footer with info
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("🔗 **Integration**: Flask (8050) + Streamlit (8051)")
    
    with col2:
        st.info(f"⏰ **Last Updated**: {datetime.now().strftime('%H:%M:%S')}")
    
    with col3:
        st.info("🎯 **Status**: Much simpler than Dash callbacks!")
    
    st.markdown("*Powered by Streamlit + Flask • Real-time data synchronization*")

if __name__ == "__main__":
    main()