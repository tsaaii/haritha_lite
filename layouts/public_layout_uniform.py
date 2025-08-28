# layouts/public_layout_uniform.py
"""
Updated layout with specific card content and uniform sizing - ENHANCED VERSION WITH NEW METRICS AND HEADER CARDS
Project Overview title added, followed by 1x4 header cards, agency header, then 2x4 main cards grid
"""

from dash import html, dcc, callback, Input, Output
import pandas as pd
from datetime import datetime, timedelta
import logging
import os
import numpy as np
from datetime import datetime, timedelta
from utils.theme_utils import get_theme_styles, get_hover_overlay_css, get_theme_css_variables
from components.navigation.hover_overlay import create_hover_overlay_banner  # ← IMPORT THE REAL ONE
from utils.theme_utils import get_theme_styles


# Initialize logger FIRST
logger = logging.getLogger(__name__)

# AGENCY NAMES MAPPING
AGENCY_NAMES = {
    'Zigma': 'Zigma Global Enviro Solutions Private Limited, Erode',
    'Saurashtra': 'Saurastra Enviro Pvt Ltd, Gujarat', 
    'Tharuni': 'Tharuni Associates, Guntur'
}

def get_display_agency_name(agency_key):
    """Get the full display name for an agency"""
    if not agency_key:
        return "Unknown Agency"
        
    # Try exact match first
    if agency_key in AGENCY_NAMES:
        return AGENCY_NAMES[agency_key]
    
    # Try partial match (case insensitive)
    agency_key_lower = agency_key.lower()
    for key, full_name in AGENCY_NAMES.items():
        if key.lower() in agency_key_lower or agency_key_lower in key.lower():
            return full_name
    
    # If no match found, return the original key with warning
    logger.warning(f"⚠️ No agency mapping found for: '{agency_key}'")
    return f"{agency_key} (Unmapped)"

def load_agency_data():
    """Load data from CSV with agency configuration logging"""
    try:
        csv_path = 'data/public_mini_processed_dates_fixed.csv'
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            logger.info(f"✅ Loaded {len(df)} records from agency data")
            
            # Convert date columns to datetime if needed
            date_columns = ['start_date', 'planned_end_date', 'expected_end_date']
            for col in date_columns:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
            
            # Clean column names
            df.columns = df.columns.str.strip()
            
            # Log agency mappings
            if 'Agency' in df.columns:
                unique_agencies = df['Agency'].dropna().unique()
                logger.info(f"📋 Found {len(unique_agencies)} agencies in data:")
                
                for agency in unique_agencies:
                    display_name = get_display_agency_name(agency)
                    if "(Unmapped)" in display_name:
                        status = "⚠️ UNMAPPED"
                    else:
                        status = "✅ MAPPED"
                    logger.info(f"  {status}: '{agency}' → '{display_name}'")
            
            return df
        else:
            logger.warning(f"📄 CSV file not found at {csv_path}, creating sample data")
            return create_sample_agency_data()
    except Exception as e:
        logger.error(f"❌ Error loading agency data: {e}")
        return create_sample_agency_data()

def create_sample_agency_data():
    """Create sample data using configured agency keys"""
    agency_keys = list(AGENCY_NAMES.keys())
    clusters = ['Nellore', 'Chittor', 'Tirupathi', 'GVMC', 'Kurnool', 'Erode', 'Guntur', 'Gujarat']
    sites = ['Site A', 'Site B', 'Site C', 'Site D', 'Site E']
    machines = ['Excavator', 'Truck', 'Loader', 'Compactor']
    
    data = []
    base_date = datetime.now()
    
    for i in range(60):
        agency_key = np.random.choice(agency_keys)
        total_quantity = np.random.randint(100, 1000)
        remediated_quantity = np.random.randint(0, int(total_quantity * 0.8))  # Max 80% completion
        
        data.append({
            'Agency': agency_key,
            'Sub-contractor': f'Contractor {i%5 + 1}',
            'Cluster': np.random.choice(clusters),
            'Site': f'{np.random.choice(sites)} {i}',
            'Machine': np.random.choice(machines),
            'Daily_Capacity': np.random.uniform(10, 50),
            'start_date': base_date - timedelta(days=np.random.randint(0, 30)),
            'planned_end_date': base_date + timedelta(days=np.random.randint(30, 100)),
            'expected_end_date': base_date + timedelta(days=np.random.randint(30, 120)),
            'days_to_sept30': str(np.random.randint(50, 150)),
            'Quantity to be remediated in MT': total_quantity,
            'Cumulative Quantity remediated till date in MT': remediated_quantity,
            'Active_site': np.random.choice(['yes', 'no']),
            'net_to_be_remediated_mt': total_quantity - remediated_quantity,
            'days_required': np.random.uniform(30, 120)
        })
    
    df = pd.DataFrame(data)
    logger.info(f"📊 Created sample data with agencies: {list(df['Agency'].unique())}")
    return df

def calculate_cluster_completion_rates(agency_data):
    """Calculate completion rate for each cluster in the agency"""
    cluster_rates = []
    print("@@@@@@@@@@@@@@@@@@",agency_data.columns)
    if agency_data.empty or 'Cluster' not in agency_data.columns:
        return cluster_rates
    
    try:
        # Required columns
        required_cols = ['Agency','Cluster', 'Site', 'Quantity to be remediated in MT','Cumulative Quantity remediated till date in MT']
        if not all(col in agency_data.columns for col in required_cols):
            logger.warning(f"Missing required columns for cluster calculation")
            return cluster_rates
        
        # Group by cluster and get unique sites within each cluster
        for cluster_name in agency_data['Cluster'].unique():
            cluster_data = agency_data[agency_data['Cluster'] == cluster_name]
            
            # Get unique sites in this cluster (to avoid double counting)
            unique_sites = cluster_data.drop_duplicates(subset=['Site'])
            
            # Calculate totals for this cluster
            total_to_remediate = unique_sites['Quantity to be remediated in MT'].sum()
            total_remediated = unique_sites['Cumulative Quantity remediated till date in MT'].sum()
            
            # Calculate completion percentage
            if total_to_remediate > 0:
                completion_rate = (total_remediated / total_to_remediate) * 100
                completion_rate = round(completion_rate, 1)  # Round to 1 decimal
            else:
                completion_rate = 0
            
            cluster_rates.append({
                'cluster': cluster_name,
                'completion_rate': completion_rate,
                'total_to_remediate': total_to_remediate,
                'total_remediated': total_remediated
            })
        
        # Sort by completion rate (highest first)
        cluster_rates.sort(key=lambda x: x['completion_rate'], reverse=True)
        
        logger.info(f"📊 Calculated completion rates for {len(cluster_rates)} clusters")
        for cluster in cluster_rates:
            logger.info(f"  {cluster['cluster']}: {cluster['completion_rate']}% ({cluster['total_remediated']}/{cluster['total_to_remediate']} MT)")
        
    except Exception as e:
        logger.error(f"❌ Error calculating cluster completion rates: {e}")
        cluster_rates = []
    
    return cluster_rates

def create_cluster_progress_card(current_agency_display, agency_data):
    """Create Card 5: Cluster Progress with list of clusters and completion rates"""
    
    cluster_rates = calculate_cluster_completion_rates(agency_data)
    
    # Create cluster list items
    cluster_items = []
    
    if not cluster_rates:
        # No data available
        cluster_items.append(
            html.Div(
                "No cluster data available",
                style={
                    "textAlign": "center",
                    "color": "var(--text-secondary)",
                    "fontStyle": "italic",
                    "padding": "1rem"
                }
            )
        )
    else:
        for cluster_info in cluster_rates:
            cluster_name = cluster_info['cluster']
            completion_rate = cluster_info['completion_rate']
            
            # Color coding based on completion rate
            if completion_rate >= 75:
                color = "var(--success, #38A169)"
            elif completion_rate >= 50:
                color = "var(--warning, #DD6B20)"
            elif completion_rate >= 25:
                color = "var(--info, #3182CE)"
            else:
                color = "var(--error, #E53E3E)"
            
            cluster_items.append(
                html.Div(
                    className="cluster-progress-item",
                    children=[
                        html.Div(
                            f"{cluster_name}:",
                            className="cluster-name"
                        ),
                        html.Div(
                            f"{completion_rate}%",
                            className="cluster-percentage",
                            style={"color": color}
                        )
                    ]
                )
            )
    
    return html.Div(
        className="enhanced-metric-card cluster-progress-card",
        children=[
            # Card Header
            html.Div(
                className="card-header",
                children=[
                    html.Div("📈", className="card-icon"),
                    html.H3("Cluster Progress", className="card-title")
                ]
            ),
            
            # Cluster List Container
            html.Div(
                className="cluster-progress-content",
                children=[
                    html.Div(
                        className="cluster-list",
                        children=cluster_items
                    )
                ]
            )
        ]
    )

def calculate_site_completion_rates(agency_data):
    """Calculate completion rate for each site in the agency"""
    site_rates = []
    
    if agency_data.empty or 'Site' not in agency_data.columns:
        return site_rates
    
    try:
        # Required columns
        required_cols = ['Site', 'Cluster', 'Quantity to be remediated in MT', 'Cumulative Quantity remediated till date in MT']
        if not all(col in agency_data.columns for col in required_cols):
            logger.warning(f"Missing required columns for site calculation")
            return site_rates
        
        # Group by site (each site should be unique anyway, but just in case)
        for site_name in agency_data['Site'].unique():
            site_data = agency_data[agency_data['Site'] == site_name].iloc[0]  # Take first record for this site
            
            # Get site details
            cluster_name = site_data['Cluster'] if 'Cluster' in site_data and pd.notna(site_data['Cluster']) else 'Unknown'
            total_to_remediate = site_data['Quantity to be remediated in MT'] if pd.notna(site_data['Quantity to be remediated in MT']) else 0
            total_remediated = site_data['Cumulative Quantity remediated till date in MT'] if pd.notna(site_data['Cumulative Quantity remediated till date in MT']) else 0
            
            # Calculate completion percentage
            if total_to_remediate > 0:
                completion_rate = (total_remediated / total_to_remediate) * 100
                completion_rate = round(completion_rate, 1)  # Round to 1 decimal
            else:
                completion_rate = 0
            
            site_rates.append({
                'site': site_name,
                'cluster': cluster_name,
                'completion_rate': completion_rate,
                'total_to_remediate': total_to_remediate,
                'total_remediated': total_remediated
            })
        
        # Sort by completion rate (highest first) - DESCENDING ORDER
        site_rates.sort(key=lambda x: x['completion_rate'], reverse=True)
        
        logger.info(f"📊 Calculated completion rates for {len(site_rates)} sites")
        for site in site_rates[:5]:  # Log top 5 for debugging
            logger.info(f"  {site['site']} ({site['cluster']}): {site['completion_rate']}% ({site['total_remediated']}/{site['total_to_remediate']} MT)")
        
    except Exception as e:
        logger.error(f"❌ Error calculating site completion rates: {e}")
        site_rates = []
    
    return site_rates

def overall_breakdown(current_agency_display, agency_data):
    """Create Card 6: Outward Processing with dummy data for each agency"""
    
    # Define dummy data for each agency
    agency_outward_data = {
        'Zigma Global Enviro Solutions Private Limited, Erode': {
            'Soil': 0.04,
            'CnD': 0,
            'Inert': 0,
            'RDF': 0
        },
        'Tharuni Associates, Guntur': {
            'Soil': 3.76,
            'CnD': 0,
            'Inert': 0,
            'RDF': 0
        },
        'Saurastra Enviro Pvt Ltd, Gujarat': {
            'Soil': 12,
            'CnD': 4,
            'Inert': 3.76,
            'RDF': 2
        }
    }
    
    # Get data for current agency (fallback to empty if not found)
    current_data = agency_outward_data.get(current_agency_display, {})
    
    # Create processing items
    processing_items = []
    
    if not current_data:
        # No data available
        processing_items.append(
            html.Div(
                "No outward processing data available",
                style={
                    "textAlign": "center",
                    "color": "var(--text-secondary)",
                    "fontStyle": "italic",
                    "padding": "1rem"
                }
            )
        )
    else:
        # Create items for each processing type
        for i, (process_type, percentage) in enumerate(current_data.items(), 1):
            # Color coding based on percentage
            if percentage >= 3:
                color = "var(--success, #38A169)"
            elif percentage >= 1:
                color = "var(--warning, #DD6B20)"
            elif percentage > 0:
                color = "var(--info, #3182CE)"
            else:
                color = "var(--error, #E53E3E)"
            
            processing_items.append(
                html.Div(
                    className="site-progress-item",
                    style={
                        "width": "100%",
                        "minWidth": "280px",
                        "padding": "clamp(0.75rem, 1.5vh, 1rem)",
                        "display": "flex",
                        "justifyContent": "space-between",
                        "alignItems": "center"
                    },
                    children=[
                        html.Div(
                            className="site-info",
                            children=[
                                html.Div(
                                    f"{i}. {process_type}",
                                    className="site-name"
                                )
                            ]
                        ),
                        html.Div(
                            f"{percentage}%",
                            className="site-percentage",
                            style={"color": color}
                        )
                    ]
                )
            )
    
    return html.Div(
        className="enhanced-metric-card site-progress-card",
        children=[
            # Card Header
            html.Div(
                className="card-header",
                children=[
                    html.Div("📊", className="card-icon"),
                    html.H3("Outward Processing", className="card-title")
                ]
            ),
            
            # Processing List Container
            html.Div(
                className="site-progress-content",
                children=[
                    html.Div(
                        className="site-list",
                        children=processing_items
                    )
                ]
            )
        ]
    )

# def overall_breakdown(current_agency_display, agency_data):
#     """Create Card 6: Site Progress with list of sites and completion rates"""
    
#     site_rates = calculate_site_completion_rates(agency_data)
    
#     # Create site list items
#     site_items = []
    
#     if not site_rates:
#         # No data available
#         site_items.append(
#             html.Div(
#                 "No site data available",
#                 style={
#                     "textAlign": "center",
#                     "color": "var(--text-secondary)",
#                     "fontStyle": "italic",
#                     "padding": "1rem"
#                 }
#             )
#         )
#     else:
#         # Limit to top 8 sites to fit in the card (can be scrollable)
#         display_sites = site_rates[:8] if len(site_rates) > 8 else site_rates
        
#         for site_info in display_sites:
#             site_name = site_info['site']
#             cluster_name = site_info['cluster']
#             completion_rate = site_info['completion_rate']
            
#             # Color coding based on completion rate (same as cluster card)
#             if completion_rate >= 75:
#                 color = "var(--success, #38A169)"
#             elif completion_rate >= 50:
#                 color = "var(--warning, #DD6B20)"
#             elif completion_rate >= 25:
#                 color = "var(--info, #3182CE)"
#             else:
#                 color = "var(--error, #E53E3E)"
            
#             # Truncate long site names for display
#             display_site_name = site_name if len(site_name) <= 20 else f"{site_name[:17]}..."
            
#             site_items.append(
#                 html.Div(
#                     className="site-progress-item",
#                     children=[
#                         html.Div(
#                             className="site-info",
#                             children=[
#                                 html.Div(
#                                     f"{display_site_name}",
#                                     className="site-name",
#                                     title=site_name  # Full name on hover
#                                 ),
#                                 html.Div(
#                                     f"({cluster_name})",
#                                     className="site-cluster"
#                                 )
#                             ]
#                         ),
#                         html.Div(
#                             f"{completion_rate}%",
#                             className="site-percentage",
#                             style={"color": color}
#                         )
#                     ]
#                 )
#             )
        
#         # Add "and X more" if there are more sites
#         if len(site_rates) > 8:
#             remaining_count = len(site_rates) - 8
#             site_items.append(
#                 html.Div(
#                     f"... and {remaining_count} more sites",
#                     className="more-sites-indicator",
#                     style={
#                         "textAlign": "center",
#                         "color": "var(--text-secondary)",
#                         "fontStyle": "italic",
#                         "fontSize": "clamp(0.8rem, 1.5vh, 0.95rem)",
#                         "padding": "clamp(0.5rem, 1vh, 0.75rem)"
#                     }
#                 )
#             )
    
#     return html.Div(
#         className="enhanced-metric-card site-progress-card",
#         children=[
#             # Card Header
#             html.Div(
#                 className="card-header",
#                 children=[
#                     html.Div("📊", className="card-icon"),
#                     html.H3("Site Progress", className="card-title")
#                 ]
#             ),
            
#             # Site List Container
#             html.Div(
#                 className="site-progress-content",
#                 children=[
#                     html.Div(
#                         className="site-list",
#                         children=site_items
#                     )
#                 ]
#             )
#         ]
#     )

def calculate_lagging_sites(agency_data):
    """Calculate sites that cannot be completed before September 30, 2025 based on days_required"""
    lagging_sites = []
    
    if agency_data.empty or 'Site' not in agency_data.columns:
        return lagging_sites
    
    try:
        # Required columns
        required_cols = ['Site', 'Cluster', 'days_required']
        if not all(col in agency_data.columns for col in required_cols):
            logger.warning(f"Missing required columns for lagging sites calculation")
            return lagging_sites
        
        # Calculate days until September 30, 2025
        today = datetime.now().date()
        sept_30 = datetime(2025, 9, 30).date()
        days_until_sept30 = (sept_30 - today).days
        
        logger.info(f"📅 Days until Sept 30, 2025: {days_until_sept30}")
        
        # Process each site
        for site_name in agency_data['Site'].unique():
            site_data = agency_data[agency_data['Site'] == site_name].iloc[0]  # Take first record for this site
            
            # Get site details
            cluster_name = site_data['Cluster'] if 'Cluster' in site_data and pd.notna(site_data['Cluster']) else 'Unknown'
            days_required = site_data['days_required'] if pd.notna(site_data['days_required']) else None
            
            # Skip sites with blank/NULL days_required
            if days_required is None or days_required == '' or str(days_required).strip() == '':
                logger.debug(f"⏭️ Skipping {site_name} - days_required is blank/NULL")
                continue
            
            # Convert days_required to numeric if it's a string
            try:
                days_required = float(days_required)
                # Skip if days_required is 0 or negative
                if days_required <= 0:
                    logger.debug(f"⏭️ Skipping {site_name} - days_required is {days_required}")
                    continue
            except (ValueError, TypeError):
                logger.debug(f"⏭️ Skipping {site_name} - cannot convert days_required '{days_required}' to number")
                continue
            
            # Simple logic: if days_required > days_until_sept30, then it's lagging
            if days_required > days_until_sept30:
                days_overdue = days_required - days_until_sept30
                
                # Get additional details for display
                active_status = site_data.get('Active_site', 'unknown')
                
                lagging_sites.append({
                    'site': site_name,
                    'cluster': cluster_name,
                    'days_required': round(days_required, 1),
                    'days_until_sept30': days_until_sept30,
                    'days_overdue': round(days_overdue, 1),
                    'active_status': active_status.lower() if isinstance(active_status, str) else 'unknown'
                })
        
        # Sort by days_overdue (most critical first - highest overdue days)
        lagging_sites.sort(key=lambda x: x['days_overdue'], reverse=True)
        
        logger.info(f"🚨 Found {len(lagging_sites)} lagging sites (cannot complete before Sept 30, 2025)")
        for site in lagging_sites[:3]:  # Log top 3 for debugging
            logger.info(f"  {site['site']} ({site['cluster']}): needs {site['days_required']} days, only {site['days_until_sept30']} available (overdue by {site['days_overdue']} days)")
        
    except Exception as e:
        logger.error(f"❌ Error calculating lagging sites: {e}")
        lagging_sites = []
    
    return lagging_sites

def create_lagging_sites_card(current_agency_display, agency_data):
    """Create Card 7: Lagging Performers with list of worst performing sites"""
    
    # Use the same performance calculation as Top Performers but in reverse order
    performance_sites = calculate_performance_rankings(agency_data)
    
    # Get lagging performers (worst performers) by reversing the list
    lagging_performers = list(reversed(performance_sites)) if performance_sites else []
    
    # Create lagging performers list items
    performer_items = []
    
    if not lagging_performers:
        # No performance data available
        performer_items.append(
            html.Div(
                "No performance data available",
                style={
                    "textAlign": "center",
                    "color": "var(--text-secondary)",
                    "fontStyle": "italic",
                    "padding": "1rem"
                }
            )
        )
    else:
        # Limit to bottom 8 performers to fit in the card
        display_performers = lagging_performers[:8] if len(lagging_performers) > 8 else lagging_performers
        
        for i, site_info in enumerate(display_performers):
            rank_from_bottom = i + 1  # Rank from worst (1st worst, 2nd worst, etc.)
            site_name = site_info['site']
            cluster_name = site_info['cluster']
            completion_rate = site_info['completion_rate']
            days_ahead_behind = site_info['days_ahead_behind']
            composite_score = site_info['composite_score']
            active_status = site_info['active_status']
            
            # Warning icons for poor performers
            if composite_score < 20:
                rank_icon = "🔴"  # Critical
                rank_color = "var(--error, #E53E3E)"
            elif composite_score < 40:
                rank_icon = "🟠"  # Poor
                rank_color = "var(--warning, #DD6B20)"
            elif composite_score < 60:
                rank_icon = "🟡"  # Below average
                rank_color = "#FFA500"
            else:
                rank_icon = "🔵"  # Needs improvement
                rank_color = "var(--info, #3182CE)"
            
            # Timeline indicator (same logic but for poor performers)
            if days_ahead_behind > 0:
                timeline_text = f"{abs(days_ahead_behind)}d ahead"
                timeline_color = "var(--success, #38A169)"
                timeline_icon = "⚡"
            elif days_ahead_behind < 0:
                timeline_text = f"{abs(days_ahead_behind)}d behind"
                timeline_color = "var(--warning, #DD6B20)"
                timeline_icon = "⏰"
            else:
                timeline_text = "on schedule"
                timeline_color = "var(--info, #3182CE)"
                timeline_icon = "🎯"
            
            # Active status indicator
            status_indicator = "" if str(active_status).lower() == 'yes' else "⚫"
            
            # Truncate long site names
            display_site_name = site_name if len(site_name) <= 16 else f"{site_name[:13]}..."
            
            performer_items.append(
                html.Div(
                    className="performance-ranking-item",  # ← FIXED: Use existing CSS class
                    children=[
                        html.Div(
                            className="ranking-info",  # ← FIXED: Use existing CSS class
                            children=[
                                html.Div(
                                    className="ranking-header",  # ← FIXED: Use existing CSS class
                                    children=[
                                        html.Span(rank_icon, className="rank-icon", style={"color": rank_color}),
                                        html.Span(status_indicator, className="status-icon"),
                                        html.Div(
                                            f"{display_site_name}",
                                            className="ranking-site-name",  # ← FIXED: Use existing CSS class
                                            title=f"#{rank_from_bottom} worst: {site_name} - Score: {composite_score}"
                                        )
                                    ]
                                ),
                                html.Div(
                                    f"({cluster_name})",
                                    className="ranking-site-cluster"  # ← FIXED: Use existing CSS class
                                )
                            ]
                        ),
                        html.Div(
                            className="performance-metrics",
                            children=[
                                html.Div(
                                    f"{completion_rate}%",
                                    className="completion-metric",
                                    style={"color": "var(--error, #E53E3E)" if completion_rate < 25 else "var(--warning, #DD6B20)"},
                                    title=f"{completion_rate}% complete"
                                ),
                                html.Div(
                                    f"{timeline_icon}{abs(days_ahead_behind)}d" if days_ahead_behind != 0 else "🎯",
                                    className="timeline-metric",
                                    style={"color": timeline_color},
                                    title=timeline_text
                                )
                            ]
                        )
                    ]
                )
            )
        
        # Add summary if there are more poor performers
        if len(lagging_performers) > 8:
            remaining_count = len(lagging_performers) - 8
            performer_items.append(
                html.Div(
                    f"... and {remaining_count} more underperforming sites",
                    className="more-rankings-indicator",  # ← FIXED: Use existing CSS class
                    style={
                        "textAlign": "center",
                        "color": "var(--error, #E53E3E)",
                        "fontWeight": "600",
                        "fontSize": "clamp(0.8rem, 1.5vh, 0.95rem)",
                        "padding": "clamp(0.5rem, 1vh, 0.75rem)"
                    }
                )
            )
    
    return html.Div(
        className="enhanced-metric-card performance-rankings-card",  # ← FIXED: Use existing CSS class
        children=[
            # Card Header
            html.Div(
                className="card-header",
                children=[
                    html.Div("📉", className="card-icon"),
                    html.H3("Lagging Performers", className="card-title")
                ]
            ),
            
            # Lagging Performers List Container
            html.Div(
                className="performance-rankings-content",  # ← FIXED: Use existing CSS class
                children=[
                    html.Div(
                        className="performance-rankings-list",  # ← FIXED: Use existing CSS class
                        children=performer_items
                    )
                ]
            )
        ]
    )

def calculate_performance_rankings(agency_data):
    """Calculate performance rankings for sites based on completion rate and timeline performance"""
    performance_sites = []
    
    if agency_data.empty or 'Site' not in agency_data.columns:
        return performance_sites
    
    try:
        # Required columns
        required_cols = ['Site', 'Cluster', 'Quantity to be remediated in MT', 'Cumulative Quantity remediated till date in MT']
        if not all(col in agency_data.columns for col in required_cols):
            logger.warning(f"Missing required columns for performance rankings calculation")
            return performance_sites
        
        # Calculate days until September 30, 2025
        today = datetime.now().date()
        sept_30 = datetime(2025, 9, 30).date()
        days_until_sept30 = (sept_30 - today).days
        
        # Process each site
        for site_name in agency_data['Site'].unique():
            site_data = agency_data[agency_data['Site'] == site_name].iloc[0]  # Take first record for this site
            
            # Get site details
            cluster_name = site_data['Cluster'] if 'Cluster' in site_data and pd.notna(site_data['Cluster']) else 'Unknown'
            total_to_remediate = site_data.get('Quantity to be remediated in MT', 0)
            total_remediated = site_data.get('Cumulative Quantity remediated till date in MT', 0)
            days_required = site_data.get('days_required', 0)
            active_status = site_data.get('Active_site', 'unknown')
            
            # Skip sites with no meaningful data
            if pd.isna(total_to_remediate) or total_to_remediate <= 0:
                continue
                
            # Calculate completion rate
            completion_rate = 0
            if total_to_remediate > 0:
                completion_rate = (total_remediated / total_to_remediate) * 100
                completion_rate = max(0, min(100, completion_rate))  # Clamp between 0-100
            
            # Calculate timeline performance (days ahead/behind)
            timeline_performance = 0
            days_ahead_behind = 0
            
            if pd.notna(days_required) and days_required > 0:
                try:
                    days_required_float = float(days_required)
                    days_ahead_behind = days_until_sept30 - days_required_float
                    
                    # Timeline performance score (0-100 scale)
                    if days_ahead_behind >= 0:
                        # Ahead of schedule - bonus points
                        timeline_performance = min(100, 50 + (days_ahead_behind / 2))
                    else:
                        # Behind schedule - penalty
                        timeline_performance = max(0, 50 + (days_ahead_behind / 2))
                        
                except (ValueError, TypeError):
                    timeline_performance = 50  # Neutral score if can't calculate
            else:
                timeline_performance = 50  # Neutral score for missing data
            
            # Calculate composite performance score
            # 60% weight on completion rate, 40% weight on timeline performance
            composite_score = (completion_rate * 0.6) + (timeline_performance * 0.4)
            
            # Only include sites with meaningful performance (>5% completion or active)
            is_active = str(active_status).lower() == 'yes'
            has_progress = completion_rate > 5
            
            if has_progress or is_active:
                performance_sites.append({
                    'site': site_name,
                    'cluster': cluster_name,
                    'completion_rate': round(completion_rate, 1),
                    'days_ahead_behind': round(days_ahead_behind, 1),
                    'timeline_performance': round(timeline_performance, 1),
                    'composite_score': round(composite_score, 1),
                    'active_status': active_status,
                    'total_to_remediate': total_to_remediate,
                    'total_remediated': total_remediated
                })
        
        # Sort by composite score (highest first - best performers)
        performance_sites.sort(key=lambda x: x['composite_score'], reverse=True)
        
        logger.info(f"🏆 Calculated performance rankings for {len(performance_sites)} sites")
        for i, site in enumerate(performance_sites[:3]):  # Log top 3 for debugging
            rank = i + 1
            logger.info(f"  #{rank}: {site['site']} ({site['cluster']}) - Score: {site['composite_score']}, Completion: {site['completion_rate']}%, Timeline: {site['days_ahead_behind']}d")
        
    except Exception as e:
        logger.error(f"❌ Error calculating performance rankings: {e}")
        performance_sites = []
    
    return performance_sites

def create_performance_rankings_card(current_agency_display, agency_data):
    """Create Card 8: Performance Rankings with list of top performing sites"""
    
    performance_sites = calculate_performance_rankings(agency_data)
    
    # Create performance rankings list items
    ranking_items = []
    
    if not performance_sites:
        # No performance data available
        ranking_items.append(
            html.Div(
                "No performance data available",
                style={
                    "textAlign": "center",
                    "color": "var(--text-secondary)",
                    "fontStyle": "italic",
                    "padding": "1rem"
                }
            )
        )
    else:
        # Limit to top 8 performers to fit in the card
        display_sites = performance_sites[:8] if len(performance_sites) > 8 else performance_sites
        
        for i, site_info in enumerate(display_sites):
            rank = i + 1
            site_name = site_info['site']
            cluster_name = site_info['cluster']
            completion_rate = site_info['completion_rate']
            days_ahead_behind = site_info['days_ahead_behind']
            composite_score = site_info['composite_score']
            active_status = site_info['active_status']
            
            # Medal/ranking icons
            if rank == 1:
                rank_icon = "🥇"
                rank_color = "#FFD700"  # Gold
            elif rank == 2:
                rank_icon = "🥈"
                rank_color = "#C0C0C0"  # Silver
            elif rank == 3:
                rank_icon = "🥉"
                rank_color = "#CD7F32"  # Bronze
            else:
                rank_icon = "🏅"
                rank_color = "var(--info, #3182CE)"  # Blue
            
            # Timeline indicator
            if days_ahead_behind > 0:
                timeline_text = f"{abs(days_ahead_behind)}d ahead"
                timeline_color = "var(--success, #38A169)"
                timeline_icon = "⚡"
            elif days_ahead_behind < 0:
                timeline_text = f"{abs(days_ahead_behind)}d behind"
                timeline_color = "var(--warning, #DD6B20)"
                timeline_icon = "⏰"
            else:
                timeline_text = "on schedule"
                timeline_color = "var(--info, #3182CE)"
                timeline_icon = "🎯"
            
            # Active status indicator
            status_indicator = "🟢" if str(active_status).lower() == 'yes' else "⚫"
            
            # Truncate long site names
            display_site_name = site_name if len(site_name) <= 16 else f"{site_name[:13]}..."
            
            ranking_items.append(
                html.Div(
                    className="performance-ranking-item",
                    children=[
                        html.Div(
                            className="ranking-info",
                            children=[
                                html.Div(
                                    className="ranking-header",
                                    children=[
                                        html.Span(rank_icon, className="rank-icon", style={"color": rank_color}),
                                        html.Span(status_indicator, className="status-icon"),
                                        html.Div(
                                            f"{display_site_name}",
                                            className="ranking-site-name",
                                            title=f"#{rank}: {site_name} - Score: {composite_score}"
                                        )
                                    ]
                                ),
                                html.Div(
                                    f"({cluster_name})",
                                    className="ranking-site-cluster"
                                )
                            ]
                        ),
                        html.Div(
                            className="performance-metrics",
                            children=[
                                html.Div(
                                    f"{completion_rate}%",
                                    className="completion-metric",
                                    style={"color": "var(--success, #38A169)" if completion_rate >= 50 else "var(--warning, #DD6B20)"},
                                    title=f"{completion_rate}% complete"
                                ),
                                html.Div(
                                    f"{timeline_icon}{abs(days_ahead_behind)}d" if days_ahead_behind != 0 else "🎯",
                                    className="timeline-metric",
                                    style={"color": timeline_color},
                                    title=timeline_text
                                )
                            ]
                        )
                    ]
                )
            )
        
        # Add summary if there are more sites
        if len(performance_sites) > 8:
            remaining_count = len(performance_sites) - 8
            ranking_items.append(
                html.Div(
                    f"... and {remaining_count} more performing sites",
                    className="more-rankings-indicator",
                    style={
                        "textAlign": "center",
                        "color": "var(--text-secondary)",
                        "fontStyle": "italic",
                        "fontSize": "clamp(0.8rem, 1.5vh, 0.95rem)",
                        "padding": "clamp(0.5rem, 1vh, 0.75rem)"
                    }
                )
            )
    
    return html.Div(
        className="enhanced-metric-card performance-rankings-card",
        children=[
            # Card Header
            html.Div(
                className="card-header",
                children=[
                    html.Div("🏆", className="card-icon"),
                    html.H3("Top Performers", className="card-title")
                ]
            ),
            
            # Performance Rankings List Container
            html.Div(
                className="performance-rankings-content",
                children=[
                    html.Div(
                        className="performance-rankings-list",
                        children=ranking_items
                    )
                ]
            )
        ]
    )

def get_agency_rotation_data(df, rotation_index=0):
    """Get agency rotation data with display name mapping"""
    if df.empty:
        return {
            'agencies': [],
            'current_agency_key': 'No Data Available',
            'current_agency_display': 'No Data Available',
            'agency_data': pd.DataFrame()
        }
    
    try:
        # Get unique agency keys from data
        agency_keys = []
        if 'Agency' in df.columns:
            agency_keys = df['Agency'].dropna().unique().tolist()
        
        if not agency_keys:
            return {
                'agencies': [],
                'current_agency_key': 'No Agencies Found',
                'current_agency_display': 'No Agencies Found',
                'agency_data': pd.DataFrame()
            }
        
        # Get current agency for rotation
        current_agency_index = rotation_index % len(agency_keys)
        current_agency_key = agency_keys[current_agency_index]
        current_agency_display = get_display_agency_name(current_agency_key)
        
        # Filter data for current agency
        agency_data = df[df['Agency'] == current_agency_key].copy()
        
        # Log rotation with mapping status
        if "(Unmapped)" in current_agency_display:
            mapping_status = "⚠️"
        else:
            mapping_status = "✅"
        logger.info(f"🔄 Rotation #{rotation_index}: {mapping_status} '{current_agency_key}' → '{current_agency_display}'")
        
        return {
            'agencies': agency_keys,
            'current_agency_key': current_agency_key,
            'current_agency_display': current_agency_display,
            'agency_data': agency_data
        }
        
    except Exception as e:
        logger.error(f"❌ Error in agency rotation: {e}")
        return {
            'agencies': [],
            'current_agency_key': 'Error Loading',
            'current_agency_display': 'Error Loading Data',
            'agency_data': pd.DataFrame()
        }

def calculate_agency_metrics(agency_data):
    """Calculate metrics for current agency including new cluster completion rate"""
    if agency_data.empty:
        return {
            'clusters_count': 0,
            'sites_count': 0,
            'active_sites': 0,
            'inactive_sites': 0,
            'planned_machines': 0,
            'deployed_machines': 0,
            'sites_not_on_track': 0,
            'critically_lagging': 0,
            'avg_cluster_completion': 0,
            'best_cluster_completion': 0,
            'total_capacity': 0,
            'avg_daily_capacity': 0,
            'total_planned_quantity': 0,
            'total_remediated_quantity': 0,
            'overall_completion_rate': 0,
            'remaining_quantity': 0
        }
    
    try:
        today = datetime.now().date()
        # FIX: Use pd.Timestamp instead of datetime.date for comparison
        sept_30 = pd.Timestamp(2025, 9, 30).date()  # Note: Changed year to 2025 to match your logs
        
        # Original metrics
        clusters_count = agency_data['Cluster'].nunique() if 'Cluster' in agency_data.columns else 0
        sites_count = agency_data['Site'].nunique() if 'Site' in agency_data.columns else 0
        
        active_sites = 0
        inactive_sites = 0
        if 'Active_site' in agency_data.columns:
            active_sites = len(agency_data[agency_data['Active_site'].str.lower() == 'yes'])
            inactive_sites = len(agency_data[agency_data['Active_site'].str.lower() == 'no'])
        
        planned_machines = agency_data['Machine'].nunique() if 'Machine' in agency_data.columns else 0
        deployed_machines = 0
        if 'Machine' in agency_data.columns and 'Active_site' in agency_data.columns:
            active_data = agency_data[agency_data['Active_site'].str.lower() == 'yes']
            deployed_machines = active_data['Machine'].nunique() if not active_data.empty else 0
        
        sites_not_on_track = 0
        if 'Active_site' in agency_data.columns and 'expected_end_date' in agency_data.columns:
            active_sites_data = agency_data[agency_data['Active_site'].str.lower() == 'yes']
            if not active_sites_data.empty:
                # FIX: Ensure both sides of comparison are the same type
                # Convert expected_end_date to date if it's datetime
                try:
                    if pd.api.types.is_datetime64_any_dtype(active_sites_data['expected_end_date']):
                        # Convert pandas datetime to date for comparison
                        expected_dates = pd.to_datetime(active_sites_data['expected_end_date']).dt.date
                        not_on_track_mask = expected_dates > sept_30
                    else:
                        # If it's already date, compare directly
                        not_on_track_mask = active_sites_data['expected_end_date'] > sept_30
                    
                    sites_not_on_track = len(active_sites_data[not_on_track_mask])
                except Exception as date_error:
                    print(f"⚠️ Warning: Could not calculate sites_not_on_track: {date_error}")
                    sites_not_on_track = 0
        
        critically_lagging = 0
        if all(col in agency_data.columns for col in ['Active_site', 'days_required', 'days_to_sept30']):
            active_data = agency_data[agency_data['Active_site'].str.lower() == 'yes']
            if not active_data.empty:
                try:
                    days_to_sept30_numeric = pd.to_numeric(active_data['days_to_sept30'], errors='coerce')
                    days_required_numeric = pd.to_numeric(active_data['days_required'], errors='coerce')
                    critically_lagging_mask = days_required_numeric > days_to_sept30_numeric
                    critically_lagging = len(active_data[critically_lagging_mask.fillna(False)])
                except Exception as lag_error:
                    print(f"⚠️ Warning: Could not calculate critically_lagging: {lag_error}")
                    critically_lagging = 0
        
        # NEW METRICS - Card 5: Cluster Completion Rate
        avg_cluster_completion = 0
        best_cluster_completion = 0
        
        if all(col in agency_data.columns for col in ['Cluster', 'Quantity to be remediated in MT', 'Cumulative Quantity remediated till date in MT']):
            try:
                cluster_metrics = agency_data.groupby('Cluster').agg({
                    'Quantity to be remediated in MT': 'sum',
                    'Cumulative Quantity remediated till date in MT': 'sum'
                }).reset_index()
                
                # Calculate completion rate for each cluster
                cluster_metrics['completion_rate'] = (
                    cluster_metrics['Cumulative Quantity remediated till date in MT'] / 
                    cluster_metrics['Quantity to be remediated in MT'] * 100
                ).fillna(0)
                
                # Round to 1 decimal place for display
                cluster_metrics['completion_rate'] = cluster_metrics['completion_rate'].round(1)
                
                avg_cluster_completion = cluster_metrics['completion_rate'].mean()
                best_cluster_completion = cluster_metrics['completion_rate'].max()
                
                # Round final values
                avg_cluster_completion = round(avg_cluster_completion, 1) if not pd.isna(avg_cluster_completion) else 0
                best_cluster_completion = round(best_cluster_completion, 1) if not pd.isna(best_cluster_completion) else 0
            except Exception as cluster_error:
                print(f"⚠️ Warning: Could not calculate cluster completion rates: {cluster_error}")
                avg_cluster_completion = 0
                best_cluster_completion = 0
        
        # NEW METRICS - Card 6: Daily Capacity
        total_capacity = 0
        avg_daily_capacity = 0
        
        if 'Daily_Capacity' in agency_data.columns:
            try:
                total_capacity = agency_data['Daily_Capacity'].sum()
                avg_daily_capacity = agency_data['Daily_Capacity'].mean()
                
                total_capacity = round(total_capacity, 0)
                avg_daily_capacity = round(avg_daily_capacity, 1) if not pd.isna(avg_daily_capacity) else 0
            except Exception as capacity_error:
                print(f"⚠️ Warning: Could not calculate capacity metrics: {capacity_error}")
                total_capacity = 0
                avg_daily_capacity = 0
        
        # NEW METRICS - Card 7: Overall Progress
        total_planned_quantity = 0
        total_remediated_quantity = 0
        overall_completion_rate = 0
        
        if all(col in agency_data.columns for col in ['Quantity to be remediated in MT', 'Cumulative Quantity remediated till date in MT']):
            try:
                total_planned_quantity = agency_data['Quantity to be remediated in MT'].sum()
                total_remediated_quantity = agency_data['Cumulative Quantity remediated till date in MT'].sum()
                
                if total_planned_quantity > 0:
                    overall_completion_rate = (total_remediated_quantity / total_planned_quantity * 100)
                    overall_completion_rate = round(overall_completion_rate, 1)
            except Exception as progress_error:
                print(f"⚠️ Warning: Could not calculate progress metrics: {progress_error}")
                total_planned_quantity = 0
                total_remediated_quantity = 0
                overall_completion_rate = 0
        
        # NEW METRICS - Card 8: Remaining Work
        remaining_quantity = total_planned_quantity - total_remediated_quantity
        remaining_quantity = max(0, remaining_quantity)  # Ensure non-negative
        
        return {
            'clusters_count': clusters_count,
            'sites_count': sites_count,
            'active_sites': active_sites,
            'inactive_sites': inactive_sites,
            'planned_machines': planned_machines,
            'deployed_machines': deployed_machines,
            'sites_not_on_track': sites_not_on_track,
            'critically_lagging': critically_lagging,
            'avg_cluster_completion': avg_cluster_completion,
            'best_cluster_completion': best_cluster_completion,
            'total_capacity': int(total_capacity),
            'avg_daily_capacity': avg_daily_capacity,
            'total_planned_quantity': int(total_planned_quantity),
            'total_remediated_quantity': int(total_remediated_quantity),
            'overall_completion_rate': overall_completion_rate,
            'remaining_quantity': int(remaining_quantity)
        }
        
    except Exception as e:
        logger.error(f"❌ Error calculating metrics: {e}")
        import traceback
        traceback.print_exc()  # Print full traceback for debugging
        return {
            'clusters_count': 0,
            'sites_count': 0,
            'active_sites': 0,
            'inactive_sites': 0,
            'planned_machines': 0,
            'deployed_machines': 0,
            'sites_not_on_track': 0,
            'critically_lagging': 0,
            'avg_cluster_completion': 0,
            'best_cluster_completion': 0,
            'total_capacity': 0,
            'avg_daily_capacity': 0,
            'total_planned_quantity': 0,
            'total_remediated_quantity': 0,
            'overall_completion_rate': 0,
            'remaining_quantity': 0
        }
    

def create_dual_metric_card_horizontal_ultra_compact(icon, title, metric1_label, metric1_value, metric1_color, metric2_label, metric2_value, metric2_color, completion_percentage=None):
    """Create a card with two metrics stacked vertically with MINIMAL spacing and horizontal separator using CSS class"""
    
    # Create title section with optional percentage
    title_children = [html.H3(title, className="card-title")]
    
    # Add styled percentage if provided
    if completion_percentage is not None:
        # Determine badge color based on performance percentage ← ADD THIS LOGIC
        if completion_percentage >= 100:
            badge_color = "var(--success, #38A169)"  # Green for meeting/exceeding target
        elif completion_percentage >= 80:
            badge_color = "var(--info, #3182CE)"     # Blue for close to target
        elif completion_percentage >= 50:
            badge_color = "var(--warning, #DD6B20)"  # Orange for behind target
        else:
            badge_color = "var(--error, #E53E3E)"    # Red for critical performance
            
        title_children.append(
            html.Span(
                f"{completion_percentage}%",
                style={
                    "color": "white",
                    "fontSize": "clamp(1rem, 2vh, 1.3rem)",
                    "fontWeight": "700",
                    "textShadow": "0 1px 2px rgba(0, 0, 0, 0.5)",
                    "background": badge_color,  # ← USE the calculated badge_color
                    "padding": "0.2rem 0.5rem",
                    "borderRadius": "12px",
                    "border": f"1px solid {badge_color}",  # ← Border matches background
                    "marginLeft": "0.5rem"
                }
            )
        )
    
    return html.Div(
        className="enhanced-metric-card",
        children=[
            # Card Header
            html.Div(
                className="card-header",
                children=[
                    html.Div(icon, className="card-icon"),
                    html.Div(
                        style={
                            "display": "flex",
                            "alignItems": "center",
                            "flex": "1"
                        },
                        children=title_children  # ← Uses the title_children with conditional badge
                    )
                ]
            ),
            
            # Metrics Container - Ultra Compact Layout
            html.Div(
                className="metrics-container-horizontal-ultra-compact",
                children=[
                    # First metric (top) - ultra compact
                    html.Div(
                        className="metric-display horizontal ultra-compact",
                        children=[
                            html.Div(
                                str(metric1_value),
                                className="metric-number",
                                style={"color": metric1_color}
                            ),
                            html.Div(
                                metric1_label,
                                className="metric-label"
                            )
                        ]
                    ),
                    
                    # NEW: Use CSS class instead of inline styles
                    html.Div(className="metrics-separator-horizontal-ultra-compact"),
                    
                    # Second metric (bottom) - ultra compact
                    html.Div(
                        className="metric-display horizontal ultra-compact",
                        children=[
                            html.Div(
                                str(metric2_value),
                                className="metric-number",
                                style={"color": metric2_color}
                            ),
                            html.Div(
                                metric2_label,
                                className="metric-label"
                            )
                        ]
                    )
                ]
            )
        ]
    )


def create_dual_metric_card_horizontal(icon, title, metric1_label, metric1_value, metric1_color, metric2_label, metric2_value, metric2_color):
    """Create a card with two metrics stacked vertically with horizontal separation"""
    return html.Div(
        className="enhanced-metric-card",
        children=[
            # Card Header
            html.Div(
                className="card-header",
                children=[
                    html.Div(icon, className="card-icon"),
                    html.H3(title, className="card-title")
                ]
            ),
            
            # Metrics Container - Horizontal Layout (stacked vertically)
            html.Div(
                className="metrics-container-horizontal",
                style={
                    "display": "flex",
                    "flexDirection": "column",
                    "alignItems": "stretch",
                    "justifyContent": "space-between", 
                    "padding": "clamp(1rem, 2vh, 1.5rem)",
                    "gap": "clamp(0.5rem, 1vh, 1rem)",
                    "flex": "1"
                },
                children=[
                    # First metric (top)
                    html.Div(
                        className="metric-display primary horizontal",
                        style={
                            "flex": "1",
                            "display": "flex",
                            "flexDirection": "column",
                            "alignItems": "center",
                            "justifyContent": "center",
                            "textAlign": "center",
                            "gap": "clamp(0.3rem, 0.5vh, 0.5rem)",
                            "padding": "clamp(0.75rem, 1.5vh, 1.25rem)"
                        },
                        children=[
                            html.Div(
                                str(metric1_value),
                                className="metric-number",
                                style={"color": metric1_color}
                            ),
                            html.Div(
                                metric1_label,
                                className="metric-label"
                            )
                        ]
                    ),
                    
                    # Horizontal Visual Separator
                    html.Div(
                        className="metrics-separator-horizontal",
                        style={
                            "height": "2px",
                            "width": "100%",
                            "background": "linear-gradient(to right, transparent 20%, rgba(255, 255, 255, 0.3) 50%, transparent 80%)",
                            "borderRadius": "1px",
                            "flexShrink": "0",
                            "margin": "clamp(0.5rem, 1vh, 1rem) 0"
                        }
                    ),
                    
                    # Second metric (bottom)
                    html.Div(
                        className="metric-display secondary horizontal",
                        style={
                            "flex": "1",
                            "display": "flex",
                            "flexDirection": "column",
                            "alignItems": "center",
                            "justifyContent": "center",
                            "textAlign": "center",
                            "gap": "clamp(0.3rem, 0.5vh, 0.5rem)",
                            "padding": "clamp(0.75rem, 1.5vh, 1.25rem)"
                        },
                        children=[
                            html.Div(
                                str(metric2_value),
                                className="metric-number",
                                style={"color": metric2_color}
                            ),
                            html.Div(
                                metric2_label,
                                className="metric-label"
                            )
                        ]
                    )
                ]
            )
        ]
    )


def create_dual_metric_card_horizontal_compact(icon, title, metric1_label, metric1_value, metric1_color, metric2_label, metric2_value, metric2_color):
    """Create a more compact card with two metrics stacked vertically with horizontal separation"""
    return html.Div(
        className="enhanced-metric-card",
        children=[
            # Card Header
            html.Div(
                className="card-header",
                children=[
                    html.Div(icon, className="card-icon"),
                    html.H3(title, className="card-title")
                ]
            ),
            
            # Metrics Container - Compact Horizontal Layout
            html.Div(
                className="metrics-container-horizontal-compact",
                style={
                    "display": "flex",
                    "flexDirection": "column",
                    "alignItems": "center",
                    "justifyContent": "center", 
                    "padding": "clamp(1rem, 2vh, 1.5rem)",
                    "gap": "clamp(0.75rem, 1.5vh, 1rem)",
                    "flex": "1"
                },
                children=[
                    # First metric (top) - more compact
                    html.Div(
                        className="metric-display primary horizontal compact",
                        style={
                            "display": "flex",
                            "flexDirection": "column",
                            "alignItems": "center",
                            "justifyContent": "center",
                            "textAlign": "center",
                            "gap": "clamp(0.2rem, 0.4vh, 0.3rem)",
                            "width": "100%"
                        },
                        children=[
                            html.Div(
                                str(metric1_value),
                                className="metric-number",
                                style={
                                    "color": metric1_color,
                                    "fontSize": "clamp(1.8rem, 3.5vh, 2.5rem)"  # Slightly smaller
                                }
                            ),
                            html.Div(
                                metric1_label,
                                className="metric-label",
                                style={
                                    "fontSize": "clamp(0.8rem, 1.5vh, 1rem)"  # Slightly smaller
                                }
                            )
                        ]
                    ),
                    
                    # Horizontal Separator - thinner for compact version
                    html.Div(
                        className="metrics-separator-horizontal-compact",
                        style={
                            "height": "1px",
                            "width": "80%",
                            "background": "linear-gradient(to right, transparent 10%, rgba(255, 255, 255, 0.25) 50%, transparent 90%)",
                            "borderRadius": "0.5px",
                            "flexShrink": "0"
                        }
                    ),
                    
                    # Second metric (bottom) - more compact
                    html.Div(
                        className="metric-display secondary horizontal compact",
                        style={
                            "display": "flex",
                            "flexDirection": "column",
                            "alignItems": "center",
                            "justifyContent": "center",
                            "textAlign": "center",
                            "gap": "clamp(0.2rem, 0.4vh, 0.3rem)",
                            "width": "100%"
                        },
                        children=[
                            html.Div(
                                str(metric2_value),
                                className="metric-number",
                                style={
                                    "color": metric2_color,
                                    "fontSize": "clamp(1.8rem, 3.5vh, 2.5rem)"  # Slightly smaller
                                }
                            ),
                            html.Div(
                                metric2_label,
                                className="metric-label",
                                style={
                                    "fontSize": "clamp(0.8rem, 1.5vh, 1rem)"  # Slightly smaller
                                }
                            )
                        ]
                    )
                ]
            )
        ]
    )

def create_dual_metric_card(icon, title, metric1_label, metric1_value, metric1_color, metric2_label, metric2_value, metric2_color):
    """Create a card with two metrics side by side with enhanced design and clean structure"""
    return html.Div(
        className="enhanced-metric-card",
        children=[
            # Card Header
            html.Div(
                className="card-header",
                children=[
                    html.Div(icon, className="card-icon"),
                    html.H3(title, className="card-title")
                ]
            ),
            
            # Metrics Container
            html.Div(
                className="metrics-container",
                children=[
                    # First metric
                    html.Div(
                        className="metric-display primary",
                        children=[
                            html.Div(
                                str(metric1_value),
                                className="metric-number",
                                style={"color": metric1_color}
                            ),
                            html.Div(
                                metric1_label,
                                className="metric-label"
                            )
                        ]
                    ),
                    
                    # Visual Separator
                    html.Div(className="metrics-separator"),
                    
                    # Second metric
                    html.Div(
                        className="metric-display secondary",
                        children=[
                            html.Div(
                                str(metric2_value),
                                className="metric-number",
                                style={"color": metric2_color}
                            ),
                            html.Div(
                                metric2_label,
                                className="metric-label"
                            )
                        ]
                    )
                ]
            )
        ]
    )

def create_empty_card(card_number):
    """Create an empty placeholder card with consistent structure"""
    return html.Div(
        className="enhanced-metric-card placeholder-card",
        children=[
            html.Div(
                className="card-header",
                children=[
                    html.Div("📊", className="card-icon placeholder-icon"),
                    html.H3(f"Card {card_number}", className="card-title placeholder-title")
                ]
            ),
            html.Div(
                className="placeholder-content",
                children=[
                    html.Div("Coming Soon", className="placeholder-text"),
                    html.Div("More metrics will be added here", className="placeholder-subtext")
                ]
            )
        ]
    )


def create_header_card_1(current_agency_display=None, agency_data=None, all_agencies_data=None):
    """Create Header Card 1: Project Overview with quantity metrics including MT units and completion percentage"""
    
    # Calculate project-wide quantity metrics
    total_remediated = 0
    total_to_remediate = 0
    
    # Calculate based on all_agencies_data
    if all_agencies_data is not None and not all_agencies_data.empty:
        # Calculate total remediated quantity across all agencies
        if 'Cumulative Quantity remediated till date in MT' in all_agencies_data.columns:
            total_remediated = all_agencies_data['Cumulative Quantity remediated till date in MT'].sum()
            total_remediated = int(round(total_remediated, 0))
        
        # Calculate total quantity to be remediated across all agencies
        if 'Quantity to be remediated in MT' in all_agencies_data.columns:
            total_to_remediate = all_agencies_data['Quantity to be remediated in MT'].sum()
            total_to_remediate = int(round(total_to_remediate, 0))
    
    # Calculate completion percentage
    completion_rate = 0
    if total_to_remediate > 0:
        completion_rate = round((total_remediated / total_to_remediate) * 100, 1)
    
    # Format numbers in Indian format (XX,XX,XXX)
    def format_indian_number(num):
        """Format number in Indian style: XX,XX,XXX"""
        if num == 0:
            return "0"
        
        # Convert to string
        num_str = str(abs(num))
        
        # If number has 3 or fewer digits, no formatting needed
        if len(num_str) <= 3:
            return num_str
        
        # For Indian format: rightmost 3 digits, then groups of 2
        result = ""
        
        # Take the rightmost 3 digits
        if len(num_str) >= 3:
            result = num_str[-3:]
            remaining = num_str[:-3]
        else:
            result = num_str
            remaining = ""
        
        # Process remaining digits in groups of 2 from right to left
        while remaining:
            if len(remaining) >= 2:
                result = remaining[-2:] + "," + result
                remaining = remaining[:-2]
            else:
                result = remaining + "," + result
                remaining = ""
        
        # Add negative sign if needed
        if num < 0:
            result = "-" + result
            
        return result
    
    # Use the ULTRA COMPACT horizontal layout method WITH completion percentage
    return create_dual_metric_card_horizontal_ultra_compact(
        icon="📋",
        title="Project Overview",
        metric1_label="Remediated (MT)",        # Updated label with units
        metric1_value=format_indian_number(total_remediated),  # Indian formatted
        metric1_color="var(--success, #38A169)",  # Green for completed work
        metric2_label="Total Required (MT)",     # Updated label with units
        metric2_value=format_indian_number(total_to_remediate),  # Indian formatted
        metric2_color="var(--info, #3182CE)",    # Blue for total work
        completion_percentage=completion_rate    # ADD completion percentage
    )

def create_header_card_2(current_agency_display=None, agency_data=None, all_agencies_data=None):
    """Create Header Card 2: Active & Inactive Sites Count"""
    
    # Calculate active and inactive sites across all agencies
    active_sites = 0
    inactive_sites = 0
    total_sites = 0  # ← ADD THIS
    
    # Calculate based on all_agencies_data
    if all_agencies_data is not None and not all_agencies_data.empty:
        if 'Active_site' in all_agencies_data.columns:
            # Count active sites (Active_site == 'yes')
            active_sites = len(all_agencies_data[all_agencies_data['Active_site'].str.lower() == 'yes'])
            
            # Count inactive sites (Active_site == 'no')
            inactive_sites = len(all_agencies_data[all_agencies_data['Active_site'].str.lower() == 'no'])
            
            # Calculate total sites ← ADD THIS
            total_sites = active_sites + inactive_sites
    
    # Create title with count badge ← ADD THIS SECTION
    title_children = [html.H3("Site Status", className="card-title")]
    
    if total_sites > 0:
        title_children.append(
            html.Span(
                f"{total_sites} Sites",
                style={
                    "color": "white",
                    "fontSize": "clamp(0.9rem, 1.8vh, 1.2rem)",
                    "fontWeight": "700",
                    "textShadow": "0 1px 2px rgba(0, 0, 0, 0.5)",
                    "background": "#38A169",  # Blue background
                    "padding": "0.15rem 0.4rem",
                    "borderRadius": "10px",
                    "border": "1px solid #38A169",
                    "marginLeft": "0.5rem"
                }
            )
        )
    
    return html.Div(
        className="enhanced-metric-card header-card-2",
        children=[
            # Card Header with count badge
            html.Div(
                className="card-header",
                children=[
                    html.Div("📊", className="card-icon"),
                    html.Div(
                        style={
                            "display": "flex",
                            "alignItems": "center",
                            "flex": "1"
                        },
                        children=title_children  # ← UPDATED: Use title_children instead of single H3
                    )
                ]
            ),
            
            # Rest of your existing metrics container code...
            html.Div(
                className="metrics-container",
                children=[
                    # First metric - Active Sites
                    html.Div(
                        className="metric-display primary",
                        children=[
                            html.Div(
                                str(active_sites),
                                className="metric-number",
                                style={"color": "var(--success, #38A169)"}
                            ),
                            html.Div(
                                "Active sites",
                                className="metric-label"
                            )
                        ]
                    ),
                    
                    # Visual Separator
                    html.Div(className="metrics-separator"),
                    
                    # Second metric - Inactive Sites
                    html.Div(
                        className="metric-display secondary",
                        children=[
                            html.Div(
                                str(inactive_sites),
                                className="metric-number",
                                style={"color": "var(--error, #E53E3E)"}
                            ),
                            html.Div(
                                "Inactive sites",
                                className="metric-label"
                            )
                        ]
                    )
                ]
            )
        ]
    )



def create_header_card_3(current_agency_display=None, agency_data=None, all_agencies_data=None):
    """Create Header Card 3: Daily Performance Comparison - Actual vs Required"""
    
    # Calculate daily performance metrics
    current_daily_rate = 0
    required_daily_rate = 0
    
    today = datetime.now().date()
    sept_30 = datetime(2025, 9, 30).date()
    days_remaining = (sept_30 - today).days
    
    if all_agencies_data is not None and not all_agencies_data.empty:
        try:
            # Calculate CURRENT daily rate using "Quantity remediated today"
            if 'Quantity remediated today' in all_agencies_data.columns:
                # Sum today's actual processing across all agencies
                current_daily_rate = all_agencies_data['Quantity remediated today'].fillna(0).sum()
                logger.info(f"📊 Today's actual processing: {current_daily_rate} MT across all agencies")
            else:
                logger.warning("⚠️ 'Quantity remediated today' column not found, using fallback calculation")
                # Fallback: use Daily_Capacity if available
                if 'Daily_Capacity' in all_agencies_data.columns:
                    current_daily_rate = all_agencies_data['Daily_Capacity'].fillna(0).sum()
                else:
                    # Last resort: estimate from cumulative data
                    if 'Cumulative Quantity remediated till date in MT' in all_agencies_data.columns:
                        total_remediated = all_agencies_data['Cumulative Quantity remediated till date in MT'].fillna(0).sum()
                        current_daily_rate = total_remediated / 90 if total_remediated > 0 else 0
                    else:
                        current_daily_rate = 0
            
            # Calculate REQUIRED daily rate (unchanged logic)
            if all(col in all_agencies_data.columns for col in ['Quantity to be remediated in MT', 'Cumulative Quantity remediated till date in MT']):
                total_to_remediate = all_agencies_data['Quantity to be remediated in MT'].fillna(0).sum()
                total_remediated = all_agencies_data['Cumulative Quantity remediated till date in MT'].fillna(0).sum()
                remaining_quantity = total_to_remediate - total_remediated
                
                if days_remaining > 0:
                    required_daily_rate = remaining_quantity / days_remaining
                    logger.info(f"📈 Required daily rate: {required_daily_rate} MT/day ({remaining_quantity} MT remaining ÷ {days_remaining} days)")
                else:
                    required_daily_rate = remaining_quantity
                    logger.warning(f"⚠️ Deadline passed! Remaining quantity: {remaining_quantity} MT")
            else:
                logger.warning("⚠️ Missing columns for required rate calculation")
                required_daily_rate = 0
                
            # Round values for display
            current_daily_rate = round(current_daily_rate, 1)
            required_daily_rate = round(required_daily_rate, 1)
            
            # Log performance comparison
            if required_daily_rate > 0:
                performance_ratio = (current_daily_rate / required_daily_rate) * 100
                if performance_ratio >= 100:
                    status = f"✅ AHEAD - {performance_ratio:.1f}% of target"
                elif performance_ratio >= 80:
                    status = f"⚡ ON TRACK - {performance_ratio:.1f}% of target"
                elif performance_ratio >= 50:
                    status = f"⚠️ BEHIND - {performance_ratio:.1f}% of target"
                else:
                    status = f"🚨 CRITICAL - {performance_ratio:.1f}% of target"
                logger.info(f"🎯 Daily Performance: {status}")
            
        except Exception as e:
            logger.error(f"❌ Error calculating daily rates: {e}")
            current_daily_rate = 0
            required_daily_rate = 0
    else:
        logger.warning("⚠️ No data available for daily rate calculation")
    
    # Calculate performance percentage ← ADD THIS SECTION
    performance_percentage = 0
    if required_daily_rate > 0:
        performance_percentage = round((current_daily_rate / required_daily_rate) * 100, 1)
    
    def format_indian_number(num):
        """Format number in Indian style: XX,XX,XXX"""
        if num == 0:
            return "0"
        
        # Handle decimal numbers
        if isinstance(num, float) and num % 1 != 0:
            # For decimal numbers, format the integer part and add decimal
            integer_part = int(num)
            decimal_part = num - integer_part
            
            if integer_part == 0:
                return f"{num:.1f}"  # Just show decimal for small numbers
            
            formatted_integer = format_indian_number(integer_part)
            return f"{formatted_integer}.{int(decimal_part * 10)}"
        
        # Convert to string for integer formatting
        num_str = str(abs(int(num)))
        
        # If number has 3 or fewer digits, no formatting needed
        if len(num_str) <= 3:
            return num_str
        
        # For Indian format: rightmost 3 digits, then groups of 2
        result = ""
        
        # Take the rightmost 3 digits
        if len(num_str) >= 3:
            result = num_str[-3:]
            remaining = num_str[:-3]
        else:
            result = num_str
            remaining = ""
        
        # Process remaining digits in groups of 2 from right to left
        while remaining:
            if len(remaining) >= 2:
                result = remaining[-2:] + "," + result
                remaining = remaining[:-2]
            else:
                result = remaining + "," + result
                remaining = ""
        
        # Add negative sign if needed
        if num < 0:
            result = "-" + result
            
        return result
    
    # Enhanced color logic based on performance
    def get_performance_colors(current, required):
        if required <= 0:
            return "var(--info, #3182CE)", "var(--info, #3182CE)"
        
        performance_ratio = current / required
        
        if performance_ratio >= 1.0:
            current_color = "var(--success, #38A169)"  # Green - Meeting or exceeding target
        elif performance_ratio >= 0.8:
            current_color = "var(--info, #3182CE)"     # Blue - Close to target
        elif performance_ratio >= 0.5:
            current_color = "var(--warning, #DD6B20)"  # Orange - Behind target
        else:
            current_color = "var(--error, #E53E3E)"    # Red - Critical performance
        
        # Required rate color based on urgency
        if days_remaining <= 30:
            required_color = "var(--error, #E53E3E)"   # Red - Very urgent
        elif days_remaining <= 60:
            required_color = "var(--warning, #DD6B20)" # Orange - Urgent
        else:
            required_color = "var(--info, #3182CE)"    # Blue - Normal
        
        return current_color, required_color
    
    current_color, required_color = get_performance_colors(current_daily_rate, required_daily_rate)
    
    return create_dual_metric_card_horizontal_ultra_compact(
        icon="⚡",
        title="Required Performance",  # Updated title to be more descriptive
        metric1_label="Today (MT)",     # Updated label to clarify it's today's actual
        metric1_value=format_indian_number(current_daily_rate),
        metric1_color=current_color,
        metric2_label="Required (MT)",  # Updated label to clarify it's the required rate
        metric2_value=format_indian_number(required_daily_rate),
        metric2_color=required_color,
        completion_percentage=performance_percentage  # ← ADD THIS LINE
    )


def create_header_cards_grid(current_agency_display=None, agency_data=None, all_agencies_data=None):
    """Create the 1x4 header cards grid with individual card functions"""
    
    header_cards = [
        create_header_card_1(current_agency_display, agency_data, all_agencies_data),
        create_header_card_2(current_agency_display, agency_data, all_agencies_data),
        create_header_card_3(current_agency_display, agency_data, all_agencies_data),
        create_header_card_4(current_agency_display, agency_data, all_agencies_data)
    ]
    
    return html.Div(
        className="header-cards-grid",
        children=header_cards
    )

# Legacy function for backwards compatibility (you can remove this later)
def create_header_card(card_number, icon="📊", title=None, content="Coming Soon"):
    """Legacy function - use individual card functions instead"""
    logger.warning("create_header_card() is deprecated. Use individual card functions instead.")
    
    card_title = title if title else f"Card {card_number}"
    
    return html.Div(
        className="enhanced-metric-card header-placeholder-card",
        children=[
            html.Div(
                className="card-header",
                children=[
                    html.Div(icon, className="card-icon placeholder-icon"),
                    html.H3(card_title, className="card-title placeholder-title")
                ]
            ),
            html.Div(
                className="placeholder-content",
                children=[
                    html.Div(content, className="placeholder-text"),
                    html.Div("Header metrics will be added here", className="placeholder-subtext")
                ]
            )
        ]
    )

def get_progress_color(percentage):
    """Return color based on completion percentage"""
    if percentage >= 80:
        return "#38A169"  # Green
    elif percentage >= 60:
        return "#F6AD55"  # Orange
    elif percentage >= 40:
        return "#ECC94B"  # Yellow
    else:
        return "#F56565"  # Red


def count_machines_from_data(data, only_active=False):
    """
    Count machines from the Machine column, handling comma-separated values
    
    Args:
        data: DataFrame with Machine column
        only_active: If True, only count machines from active sites
    
    Returns:
        int: Total count of machines
    """
    if data is None or data.empty or 'Machine' not in data.columns:
        return 0
    
    # Filter for active sites if requested
    working_data = data.copy()
    if only_active and 'Active_site' in data.columns:
        working_data = data[data['Active_site'].str.lower() == 'yes']
    
    if working_data.empty:
        return 0
    
    total_machines = 0
    
    try:
        for _, row in working_data.iterrows():
            machine_value = row['Machine']
            
            # Skip if machine value is null or empty
            if pd.isna(machine_value) or str(machine_value).strip() == '':
                continue
            
            # Convert to string and split by comma
            machine_str = str(machine_value).strip()
            
            # Split by comma and count each machine
            machines = [m.strip() for m in machine_str.split(',') if m.strip()]
            total_machines += len(machines)
            
    except Exception as e:
        print(f"⚠️ Error counting machines: {e}")
        return 0
    
    return total_machines


def create_header_card_4(current_agency_display=None, agency_data=None, all_agencies_data=None):
    """Create Header Card 4: Overall Machine Status - Deployed vs Planned"""

    # Calculate overall machine deployment metrics
    planned_machines = 0
    deployed_machines = 0

    # Calculate based on all_agencies_data
    if all_agencies_data is not None and not all_agencies_data.empty:
        try:
            # Count total planned machines across all agencies (all records)
            planned_machines = count_machines_from_data(all_agencies_data)
            
            # Count deployed machines across all agencies (only active sites)
            deployed_machines = count_machines_from_data(all_agencies_data, only_active=True)
            
            not_deployed_machines = abs(planned_machines - deployed_machines)
                
            print(f"🚀 Overall Machine Status: {deployed_machines} deployed out of {planned_machines} planned")
                
        except Exception as e:
            print(f"⚠️ Error calculating overall machine status: {e}")
            planned_machines = 0
            deployed_machines = 0

    # Calculate deployment percentage ← ADD THIS
    deployment_percentage = 0
    if planned_machines > 0:
        deployment_percentage = round((deployed_machines / planned_machines) * 100, 1)

    # Use the dual metric card format but with machine count badge ← MODIFY THIS
    return html.Div(
        className="enhanced-metric-card header-card-4",
        children=[
            # Card Header with machine count badge ← ADD THIS SECTION
            html.Div(
                className="card-header",
                children=[
                    html.Div("🚀", className="card-icon"),
                    html.Div(
                        style={
                            "display": "flex",
                            "alignItems": "center",
                            "flex": "1"
                        },
                        children=[
                            html.H3("Machine Status", className="card-title"),
                            html.Span(
                                f"{planned_machines} Machines",
                                style={
                                    "color": "white",
                                    "fontSize": "clamp(0.9rem, 1.8vh, 1.2rem)",
                                    "fontWeight": "700",
                                    "textShadow": "0 1px 2px rgba(0, 0, 0, 0.5)",
                                    "background": "var(--info, #3182CE)",  # Blue for total count
                                    "padding": "0.15rem 0.4rem",
                                    "borderRadius": "10px",
                                    "border": "1px solid var(--info, #3182CE)",
                                    "marginLeft": "0.5rem"
                                }
                            ) if planned_machines > 0 else ""
                        ]
                    )
                ]
            ),
            
            # Metrics Container ← KEEP EXISTING
            html.Div(
                className="metrics-container",
                children=[
                    # First metric
                    html.Div(
                        className="metric-display primary",
                        children=[
                            html.Div(
                                str(deployed_machines),
                                className="metric-number",
                                style={"color": "var(--success, #38A169)"}  # Green for deployed machines
                            ),
                            html.Div(
                                "Deployed",
                                className="metric-label"
                            )
                        ]
                    ),
                    
                    # Visual Separator
                    html.Div(className="metrics-separator"),
                    
                    # Second metric
                    html.Div(
                        className="metric-display secondary",
                        children=[
                            html.Div(
                                str(not_deployed_machines),
                                className="metric-number",
                                style={"color": "var(--info, #3182CE)"}     # Blue for planned machines
                            ),
                            html.Div(
                                "Not deployed",
                                className="metric-label"
                            )
                        ]
                    )
                ]
            )
        ]
    )


def create_agency_completion_card(agency_data=None):
    """Create Card 4: Agency Machine Status - Deployed vs Planned (agency-specific)"""

    # Calculate agency machine deployment metrics
    agency_planned_machines = 0
    agency_deployed_machines = 0

    # Calculate based on agency_data (current agency only)
    if agency_data is not None and not agency_data.empty:
        try:
            # Count total planned machines for current agency (all records)
            agency_planned_machines = count_machines_from_data(agency_data, only_active=False)
            # Count deployed machines for current agency (only active sites)
            agency_deployed_machines = count_machines_from_data(agency_data, only_active=True)
            agency_not_deployed_machines = abs(agency_planned_machines - agency_deployed_machines)
                
            print(f"🏢 Agency Machine Status: {agency_deployed_machines} deployed out of {agency_planned_machines} planned")
                
        except Exception as e:
            print(f"⚠️ Error calculating agency machine status: {e}")
            agency_planned_machines = 0
            agency_deployed_machines = 0


    # Use dual metric card format with machine count badge ← MODIFY THIS
    return html.Div(
        className="enhanced-metric-card agency-machine-card",
        children=[
            # Card Header with machine count badge ← ADD THIS SECTION
            html.Div(
                className="card-header",
                children=[
                    html.Div("🏗️", className="card-icon"),
                    html.Div(
                        style={
                            "display": "flex",
                            "alignItems": "center",
                            "flex": "1"
                        },
                        children=[
                            html.H3("Machine Status", className="card-title"),
                            html.Span(
                                f"{agency_planned_machines} Machines",
                                style={
                                    "color": "white",
                                    "fontSize": "clamp(0.9rem, 1.8vh, 1.2rem)",
                                    "fontWeight": "700",
                                    "textShadow": "0 1px 2px rgba(0, 0, 0, 0.5)",
                                    "background": "var(--info, #3182CE)",  # Blue for total count
                                    "padding": "0.15rem 0.4rem",
                                    "borderRadius": "10px",
                                    "border": "1px solid var(--info, #3182CE)",
                                    "marginLeft": "0.5rem"
                                }
                            ) if agency_not_deployed_machines > 0 else ""
                        ]
                    )
                ]
            ),
            
            # Metrics Container ← KEEP EXISTING
            html.Div(
                className="metrics-container",
                children=[
                    # First metric
                    html.Div(
                        className="metric-display primary",
                        children=[
                            html.Div(
                                str(agency_deployed_machines),
                                className="metric-number",
                                style={"color": "var(--success, #38A169)"}  # Green for deployed machines
                            ),
                            html.Div(
                                "Deployed",
                                className="metric-label"
                            )
                        ]
                    ),
                    
                    # Visual Separator
                    html.Div(className="metrics-separator"),
                    
                    # Second metric
                    html.Div(
                        className="metric-display secondary",
                        children=[
                            html.Div(
                                str(agency_not_deployed_machines),
                                className="metric-number",
                                style={"color": "var(--info, #3182CE)"}     # Blue for planned machines
                            ),
                            html.Div(
                                "Not deployed",
                                className="metric-label"
                            )
                        ]
                    )
                ]
            )
        ]
    )


def create_specific_metric_cards(current_agency_display, metrics, theme_styles, agency_data=None):
    """Create all 8 cards in 2x4 grid with enhanced Card 1 showing agency completion percentage"""
    cards = []
    
    # Card 1: Agency Quantity Metrics (Remediated vs Required) WITH COMPLETION PERCENTAGE
    # Calculate agency-specific quantity metrics
    agency_total_remediated = 0
    agency_total_to_remediate = 0
    
    if agency_data is not None and not agency_data.empty:
        # Calculate total remediated quantity for current agency
        if 'Cumulative Quantity remediated till date in MT' in agency_data.columns:
            agency_total_remediated = agency_data['Cumulative Quantity remediated till date in MT'].sum()
            agency_total_remediated = int(round(agency_total_remediated, 0))
        
        # Calculate total quantity to be remediated for current agency
        if 'Quantity to be remediated in MT' in agency_data.columns:
            agency_total_to_remediate = agency_data['Quantity to be remediated in MT'].sum()
            agency_total_to_remediate = int(round(agency_total_to_remediate, 0))
    
    # Calculate agency completion percentage
    agency_completion_rate = 0
    if agency_total_to_remediate > 0:
        agency_completion_rate = round((agency_total_remediated / agency_total_to_remediate) * 100, 1)
    
    # Format numbers in Indian format (XX,XX,XXX) - same as header card 1
    def format_indian_number(num):
        """Format number in Indian style: XX,XX,XXX"""
        if num == 0:
            return "0"
        
        # Convert to string
        num_str = str(abs(num))
        
        # If number has 3 or fewer digits, no formatting needed
        if len(num_str) <= 3:
            return num_str
        
        # For Indian format: rightmost 3 digits, then groups of 2
        result = ""
        
        # Take the rightmost 3 digits
        if len(num_str) >= 3:
            result = num_str[-3:]
            remaining = num_str[:-3]
        else:
            result = num_str
            remaining = ""
        
        # Process remaining digits in groups of 2 from right to left
        while remaining:
            if len(remaining) >= 2:
                result = remaining[-2:] + "," + result
                remaining = remaining[:-2]
            else:
                result = remaining + "," + result
                remaining = ""
        
        # Add negative sign if needed
        if num < 0:
            result = "-" + result
            
        return result
    
    # Card 1: Use the ULTRA COMPACT horizontal layout method WITH completion percentage
    card1 = create_dual_metric_card_horizontal_ultra_compact(
        icon="🏢",  # Changed icon to represent agency-specific data
        title="Agency Overview",  # Changed title to reflect agency scope
        metric1_label="Remediated (MT)",        # Same label with units
        metric1_value=format_indian_number(agency_total_remediated),  # Indian formatted
        metric1_color="var(--success, #38A169)",  # Green for completed work
        metric2_label="Total Required (MT)",     # Same label with units
        metric2_value=format_indian_number(agency_total_to_remediate),  # Indian formatted
        metric2_color="var(--info, #3182CE)",    # Blue for total work
        completion_percentage=agency_completion_rate  # ADD agency completion percentage
    )
    cards.append(card1)
    
    # Card 2: Active Sites (green) and Inactive Sites (red)
    agency_total_sites = metrics['active_sites'] + metrics['inactive_sites'] 
    card2 = html.Div(
        className="enhanced-metric-card",
        children=[
            # Card Header with count badge ← MODIFY THIS SECTION
            html.Div(
                className="card-header",
                children=[
                    html.Div("🏭", className="card-icon"),
                    html.Div(
                        style={
                            "display": "flex",
                            "alignItems": "center",
                            "flex": "1"
                        },
                        children=[
                            html.H3("Site Status", className="card-title"),
                            html.Span(
                                f"{agency_total_sites} Sites",
                                style={
                                    "color": "white",
                                    "fontSize": "clamp(0.9rem, 1.8vh, 1.2rem)",
                                    "fontWeight": "700",
                                    "textShadow": "0 1px 2px rgba(0, 0, 0, 0.5)",
                                    "background": "#38A169",
                                    "padding": "0.15rem 0.4rem",
                                    "borderRadius": "10px",
                                    "border": "1px solid #38A169",
                                    "marginLeft": "0.5rem"
                                }
                            ) if agency_total_sites > 0 else ""
                        ]
                    )
                ]
            ),
            
            # Rest of your existing metrics container...
            html.Div(
                className="metrics-container",
                children=[
                    # First metric
                    html.Div(
                        className="metric-display primary",
                        children=[
                            html.Div(
                                str(metrics['active_sites']),
                                className="metric-number",
                                style={"color": "var(--success, #38A169)"}
                            ),
                            html.Div(
                                "Active Sites",
                                className="metric-label"
                            )
                        ]
                    ),
                    
                    # Visual Separator
                    html.Div(className="metrics-separator"),
                    
                    # Second metric
                    html.Div(
                        className="metric-display secondary",
                        children=[
                            html.Div(
                                str(metrics['inactive_sites']),
                                className="metric-number",
                                style={"color": "var(--error, #E53E3E)"}
                            ),
                            html.Div(
                                "Inactive Sites",
                                className="metric-label"
                            )
                        ]
                    )
                ]
            )
        ]
    )
    cards.append(card2)
    
    # Card 3: ENHANCED - Agency Daily Performance (same logic as header card 3 but agency-specific)
    card3 = create_agency_daily_performance_card(current_agency_display, agency_data)
    cards.append(card3)
    
    # Card 4: ENHANCED - Agency Completion Percentage (similar to header card 4)
    card4 = create_agency_completion_card(agency_data)
    cards.append(card4)
    
    # Card 5: Cluster Progress (LIST STYLE) - UNCHANGED
    if agency_data is not None and not agency_data.empty:
        card5 = create_cluster_progress_card(current_agency_display, agency_data)
    else:
        card5 = create_empty_card(5)
    cards.append(card5)

    # Card 6: Lagging Sites (LIST STYLE) - MOVED FROM POSITION 7
    if agency_data is not None and not agency_data.empty:
        card6 = create_lagging_sites_card(current_agency_display, agency_data)
    else:
        card6 = create_empty_card(6)
    cards.append(card6)

    # Card 7: Performance Rankings - MOVED FROM POSITION 8
    if agency_data is not None and not agency_data.empty:
        card7 = create_performance_rankings_card(current_agency_display, agency_data)
    else:
        card7 = create_empty_card(7)
    cards.append(card7)

    # Card 8: Site Progress (LIST STYLE) - MOVED FROM POSITION 6
    if agency_data is not None and not agency_data.empty:
        card8 = overall_breakdown(current_agency_display, agency_data)
    else:
        card8 = create_empty_card(8)
    cards.append(card8)
    
    return cards

def create_agency_daily_performance_card(current_agency_display, agency_data):
    """Create Card 3: Agency Daily Performance - Today's Actual vs Required Daily Rate"""
    
    # Calculate agency-specific daily performance metrics
    agency_current_daily_rate = 0
    agency_required_daily_rate = 0
    
    today = datetime.now().date()
    sept_30 = datetime(2025, 9, 30).date()
    days_remaining = (sept_30 - today).days
    
    if agency_data is not None and not agency_data.empty:
        try:
            # Calculate CURRENT daily rate using "Quantity remediated today" for this agency
            if 'Quantity remediated today' in agency_data.columns:
                # Sum today's actual processing for current agency only
                agency_current_daily_rate = agency_data['Quantity remediated today'].fillna(0).sum()
                logger.info(f"📊 {current_agency_display} today's processing: {agency_current_daily_rate} MT")
            else:
                logger.warning(f"⚠️ 'Quantity remediated today' column not found for {current_agency_display}, using fallback")
                # Fallback: use Daily_Capacity if available
                if 'Daily_Capacity' in agency_data.columns:
                    agency_current_daily_rate = agency_data['Daily_Capacity'].fillna(0).sum()
                else:
                    # Last resort: estimate from cumulative data for this agency
                    if 'Cumulative Quantity remediated till date in MT' in agency_data.columns:
                        agency_total_remediated = agency_data['Cumulative Quantity remediated till date in MT'].fillna(0).sum()
                        agency_current_daily_rate = agency_total_remediated / 90 if agency_total_remediated > 0 else 0
                    else:
                        agency_current_daily_rate = 0
            
            # Calculate REQUIRED daily rate for this agency
            if all(col in agency_data.columns for col in ['Quantity to be remediated in MT', 'Cumulative Quantity remediated till date in MT']):
                agency_total_to_remediate = agency_data['Quantity to be remediated in MT'].fillna(0).sum()
                agency_total_remediated = agency_data['Cumulative Quantity remediated till date in MT'].fillna(0).sum()
                agency_remaining_quantity = agency_total_to_remediate - agency_total_remediated
                
                if days_remaining > 0:
                    agency_required_daily_rate = agency_remaining_quantity / days_remaining
                    logger.info(f"📈 {current_agency_display} required rate: {agency_required_daily_rate} MT/day ({agency_remaining_quantity} MT remaining ÷ {days_remaining} days)")
                else:
                    agency_required_daily_rate = agency_remaining_quantity
                    logger.warning(f"⚠️ {current_agency_display} deadline passed! Remaining: {agency_remaining_quantity} MT")
            else:
                logger.warning(f"⚠️ Missing columns for {current_agency_display} required rate calculation")
                agency_required_daily_rate = 0
                
            # Round values for display
            agency_current_daily_rate = round(agency_current_daily_rate, 1)
            agency_required_daily_rate = round(agency_required_daily_rate, 1)
            
            # Log agency performance comparison
            if agency_required_daily_rate > 0:
                performance_ratio = (agency_current_daily_rate / agency_required_daily_rate) * 100
                if performance_ratio >= 100:
                    status = f"✅ AHEAD - {performance_ratio:.1f}% of target"
                elif performance_ratio >= 80:
                    status = f"⚡ ON TRACK - {performance_ratio:.1f}% of target"
                elif performance_ratio >= 50:
                    status = f"⚠️ BEHIND - {performance_ratio:.1f}% of target"
                else:
                    status = f"🚨 CRITICAL - {performance_ratio:.1f}% of target"
                logger.info(f"🎯 {current_agency_display} Performance: {status}")
            
        except Exception as e:
            logger.error(f"❌ Error calculating {current_agency_display} daily rates: {e}")
            agency_current_daily_rate = 0
            agency_required_daily_rate = 0
    else:
        logger.warning(f"⚠️ No data available for {current_agency_display} daily rate calculation")
    
    # Calculate agency performance percentage ← ADD THIS SECTION
    agency_performance_percentage = 0
    if agency_required_daily_rate > 0:
        agency_performance_percentage = round((agency_current_daily_rate / agency_required_daily_rate) * 100, 1)
    
    def format_indian_number(num):
        """Format number in Indian style: XX,XX,XXX (same as header card)"""
        if num == 0:
            return "0"
        
        # Handle decimal numbers
        if isinstance(num, float) and num % 1 != 0:
            # For decimal numbers, format the integer part and add decimal
            integer_part = int(num)
            decimal_part = num - integer_part
            
            if integer_part == 0:
                return f"{num:.1f}"  # Just show decimal for small numbers
            
            formatted_integer = format_indian_number(integer_part)
            return f"{formatted_integer}.{int(decimal_part * 10)}"
        
        # Convert to string for integer formatting
        num_str = str(abs(int(num)))
        
        # If number has 3 or fewer digits, no formatting needed
        if len(num_str) <= 3:
            return num_str
        
        # For Indian format: rightmost 3 digits, then groups of 2
        result = ""
        
        # Take the rightmost 3 digits
        if len(num_str) >= 3:
            result = num_str[-3:]
            remaining = num_str[:-3]
        else:
            result = num_str
            remaining = ""
        
        # Process remaining digits in groups of 2 from right to left
        while remaining:
            if len(remaining) >= 2:
                result = remaining[-2:] + "," + result
                remaining = remaining[:-2]
            else:
                result = remaining + "," + result
                remaining = ""
        
        # Add negative sign if needed
        if num < 0:
            result = "-" + result
            
        return result
    
    # Enhanced color logic based on agency performance (same as header card)
    def get_agency_performance_colors(current, required):
        if required <= 0:
            return "var(--info, #3182CE)", "var(--info, #3182CE)"
        
        performance_ratio = current / required
        
        if performance_ratio >= 1.0:
            current_color = "var(--success, #38A169)"  # Green - Meeting or exceeding target
        elif performance_ratio >= 0.8:
            current_color = "var(--info, #3182CE)"     # Blue - Close to target
        elif performance_ratio >= 0.5:
            current_color = "var(--warning, #DD6B20)"  # Orange - Behind target
        else:
            current_color = "var(--error, #E53E3E)"    # Red - Critical performance
        
        # Required rate color based on urgency
        if days_remaining <= 30:
            required_color = "var(--error, #E53E3E)"   # Red - Very urgent
        elif days_remaining <= 60:
            required_color = "var(--warning, #DD6B20)" # Orange - Urgent
        else:
            required_color = "var(--info, #3182CE)"    # Blue - Normal
        
        return current_color, required_color
    
    current_color, required_color = get_agency_performance_colors(agency_current_daily_rate, agency_required_daily_rate)
    
    # Use ultra compact horizontal layout for consistency with header cards
    return create_dual_metric_card_horizontal_ultra_compact(
        icon="📊",  # Changed icon to represent agency-specific data analysis
        title="Agency Performance",  # Updated title to reflect agency scope
        metric1_label="Today (MT)",     # Same as header card - today's actual
        metric1_value=format_indian_number(agency_current_daily_rate),
        metric1_color=current_color,
        metric2_label="Required (MT)",  # Same as header card - required rate
        metric2_value=format_indian_number(agency_required_daily_rate),
        metric2_color=required_color,
        completion_percentage=agency_performance_percentage  # ← ADD THIS LINE
    )

def create_project_overview_header():
    """Create project overview header with today's date using agency header styling"""
    today = datetime.now().strftime("%B %d, %Y")
    
    return html.Div(
        className="agency-header",  # Using same CSS class as agency header
        children=[
            html.H1(f"Overall Project Overview in Real Time as of {today}", className="agency-title")
        ]
    )

def create_agency_header(current_agency_display):
    """Create agency header with full display name - positioned after header cards"""
    
    return html.Div(
        className="agency-header",
        children=[
            html.H1(current_agency_display, className="agency-title")
        ]
    )

def create_hero_section():
    """Create the hero section with logos and title"""
    return html.Div(
        className="hero-section",
        children=[
            html.Div(
                className="hero-content",
                children=[
                    # Left Logo Section (A.png, B.png, left.png)
                    html.Div(
                        style={
                            "display": "flex", "alignItems": "center", "justifyContent": "center",
                            "height": "100%", "flex": "1", "gap": "clamp(0.8rem, 2vw, 1.5rem)"
                        },
                        children=[
                            html.Img(
                                src="/assets/img/A.png",
                                alt="Organization Logo A",
                                className="responsive-logo",
                                style={
                                    "height": "clamp(60px, 12vh, 90px)",
                                    "width": "auto",
                                    "objectFit": "contain",
                                    "filter": "drop-shadow(2px 2px 4px rgba(0, 0, 0, 0.3))",
                                    "transition": "all 0.3s ease"
                                }
                            ),
                            html.Img(
                                src="/assets/img/B.png",
                                alt="Organization Logo B",
                                className="responsive-logo",
                                style={
                                    "height": "clamp(60px, 12vh, 90px)",
                                    "width": "auto",
                                    "objectFit": "contain",
                                    "filter": "drop-shadow(2px 2px 4px rgba(0, 0, 0, 0.3))",
                                    "transition": "all 0.3s ease"
                                }
                            ),
                            html.Img(
                                src="/assets/img/left1.png",
                                alt="Left Organization Logo",
                                className="responsive-logo",
                                style={
                                    "height": "clamp(60px, 12vh, 90px)",
                                    "width": "auto",
                                    "objectFit": "contain",
                                    "filter": "drop-shadow(2px 2px 4px rgba(0, 0, 0, 0.3))",
                                    "transition": "all 0.3s ease"
                                }
                            )
                        ]
                    ),
                    
                    # Title Section
                    html.Div(
                        className="hero-title-section",
                        style={
                            "textAlign": "center", "flex": "0 1 auto", "padding": "0 clamp(0.5rem, 2vw, 1.5rem)",
                            "display": "flex", "flexDirection": "column", "justifyContent": "center", 
                            "alignItems": "center", "height": "100%", "minWidth": "300px"
                        },
                        children=[
                            html.H1(
                                "Swachha Andhra Corporation",
                                className="hero-title",
                                style={
                                    "margin": "0", "padding": "0", "fontSize": "clamp(1.5rem, 4vw, 2.5rem)",
                                    "fontWeight": "800", "lineHeight": "1.1", 
                                    "textShadow": "2px 2px 4px rgba(0, 0, 0, 0.3)", "letterSpacing": "-0.5px"
                                }
                            ),
                            html.P(
                                "Real Time Legacy Waste Remediation Progress Tracker",
                                className="hero-subtitle",
                                style={
                                    "margin": "0.25rem 0 0 0", "padding": "0", 
                                    "fontSize": "clamp(0.8rem, 1.8vw, 1rem)",
                                    "fontWeight": "500", "lineHeight": "1.3", "opacity": "0.9", "textAlign": "center"
                                }
                            )
                        ]
                    ),
                    
                    # Right Logo Section (right.png, C.png, D.png)
                    html.Div(
                        style={
                            "display": "flex", "alignItems": "center", "justifyContent": "center", 
                            "height": "100%", "flex": "1", "gap": "clamp(0.8rem, 2vw, 1.5rem)"
                        },
                        children=[
                            html.Img(
                                src="/assets/img/right1.png",
                                alt="Right Organization Logo",
                                className="responsive-logo",
                                style={
                                    "height": "clamp(60px, 12vh, 90px)",
                                    "width": "auto",
                                    "objectFit": "contain",
                                    "filter": "drop-shadow(2px 2px 4px rgba(0, 0, 0, 0.3))",
                                    "transition": "all 0.3s ease"
                                }
                            ),
                            html.Img(
                                src="/assets/img/C2.png",
                                alt="Organization Logo C",
                                className="responsive-logo",
                                style={
                                    "height": "clamp(60px, 12vh, 90px)",
                                    "width": "auto",
                                    "objectFit": "contain",
                                    "filter": "drop-shadow(2px 2px 4px rgba(0, 0, 0, 0.3))",
                                    "transition": "all 0.3s ease"
                                }
                            ),
                            html.Img(
                                src="/assets/img/D2.png",
                                alt="Organization Logo D",
                                className="responsive-logo",
                                style={
                                    "height": "clamp(60px, 12vh, 90px)",
                                    "width": "auto",
                                    "objectFit": "contain",
                                    "filter": "drop-shadow(2px 2px 4px rgba(0, 0, 0, 0.3))",
                                    "transition": "all 0.3s ease"
                                }
                            )
                        ]
                    )
                ]
            )
        ]
    )

def build_public_layout(theme_name="dark", is_authenticated=False, user_data=None):
    """Build the public layout with enhanced card structure - project overview, 1x4 header cards, agency header, then 2x4 main cards"""
    theme_styles = get_theme_styles(theme_name)
    
    # DEBUG: Check if assets folder exists
    assets_path = "assets/css/uniform_cards.css"
    css_exists = os.path.exists(assets_path)
    logger.info(f"🔍 CSS Debug: uniform_cards.css exists at {assets_path}: {css_exists}")
    
    return html.Div(
        className="public-layout",
        style={
            "--primary-bg": theme_styles["theme"]["primary_bg"],
            "--secondary-bg": theme_styles["theme"]["secondary_bg"],
            "--accent-bg": theme_styles["theme"]["accent_bg"],
            "--card-bg": theme_styles["theme"]["card_bg"],
            "--text-primary": theme_styles["theme"]["text_primary"],
            "--text-secondary": theme_styles["theme"]["text_secondary"],
            "--brand-primary": theme_styles["theme"]["brand_primary"],
            "--border-light": theme_styles["theme"].get("border_light", theme_styles["theme"]["accent_bg"]),
            "--success": theme_styles["theme"]["success"],
            "--warning": theme_styles["theme"]["warning"],
            "--error": theme_styles["theme"]["error"],
            "--info": theme_styles["theme"]["info"]
        },
        children=[
            # Enhanced CSS Loading with timestamp to force refresh
            html.Link(
                rel="stylesheet",
                href=f"/assets/css/container_zoom_fix.css?v={int(datetime.now().timestamp())}"
            ),
        
            # In your public_layout_uniform.py, add mobile detection
                
            dcc.Interval(id='auto-rotation-interval', interval=15*1000, n_intervals=0),
            dcc.Store(id='current-theme', data=theme_name),
            create_hover_overlay_banner(theme_name),
            html.Div(
                className="main-content",
                children=[
                    create_hero_section(),
                    html.Div(id="project-overview-container"),  # NEW: Project overview title first
                    html.Div(id="header-cards-container"),      # Header cards second  
                    html.Div(id="agency-header-container"),     # Agency header third
                    html.Div(id="dynamic-cards-container", className="cards-grid")  # Main cards grid (2x4) fourth
                ]
            )
        ]
    )

@callback(
    [Output('project-overview-container', 'children'),  # NEW: Project overview first
     Output('header-cards-container', 'children'),      # Header cards second
     Output('agency-header-container', 'children'),     # Agency header third  
     Output('dynamic-cards-container', 'children')],    # Main cards fourth
    [Input('auto-rotation-interval', 'n_intervals'), Input('current-theme', 'data')],
    prevent_initial_call=False
)
def update_agency_dashboard(n_intervals, theme_name):
    """Update dashboard with enhanced card layout - project overview, 1x4 header cards, agency header, then 2x4 main cards"""
    try:
        logger.info(f"🔄 Agency rotation update #{n_intervals}")
        
        df = load_agency_data()
        rotation_data = get_agency_rotation_data(df, n_intervals)
        current_agency_key = rotation_data['current_agency_key']
        current_agency_display = rotation_data['current_agency_display']
        agency_data = rotation_data['agency_data']
        
        logger.info(f"🏢 Displaying: {current_agency_display} (Records: {len(agency_data)})")
        
        # Calculate metrics
        metrics = calculate_agency_metrics(agency_data)
        
        if not agency_data.empty:
            try:
                lagging_sites = calculate_lagging_sites(agency_data)
                logger.info(f"🚨 Lagging Sites Summary: {len(lagging_sites)} sites cannot complete before Sept 30, 2025")
            except Exception as lagging_error:
                logger.warning(f"⚠️ Could not calculate lagging sites: {lagging_error}")
        
        theme_styles = get_theme_styles(theme_name or 'dark')
        
        # Create components in new order
        project_overview = create_project_overview_header()  # NEW: Project overview first
        header_cards = create_header_cards_grid(           # Header cards second - WITH DATA
        current_agency_display=current_agency_display,
        agency_data=agency_data,
        all_agencies_data=df  # Pass ALL agencies data for project-wide metrics
        )        # Header cards second
        agency_header = create_agency_header(current_agency_display)  # Agency header third
        main_cards = create_specific_metric_cards(current_agency_display, metrics, theme_styles, agency_data)  # Main cards fourth (2x4 grid)
        
        logger.info(f"✅ Created project overview, header cards, agency header, and {len(main_cards)} main cards for {current_agency_display}")
        
        # Return exactly 4 values in new order: project_overview, header_cards, agency_header, main_cards
        return project_overview, header_cards, agency_header, main_cards
        
    except Exception as e:
        logger.error(f"❌ Error in dashboard update: {e}")
        import traceback
        traceback.print_exc()
        
        # Create fallback content - ALWAYS return exactly 4 values
        try:
            fallback_project_overview = create_project_overview_header()  # Use default project overview
            fallback_header_cards = create_header_cards_grid()  # Use default header cards
            
            fallback_agency_header = html.Div(
                "Error Loading Agency Data",
                className="agency-header",
                style={'color': 'red', 'textAlign': 'center', 'padding': '1rem'}
            )
            
            fallback_main_cards = []
            for i in range(8):
                fallback_main_cards.append(create_empty_card(i + 1))
            
            # Return exactly 4 values in new order
            return fallback_project_overview, fallback_header_cards, fallback_agency_header, fallback_main_cards
            
        except Exception as fallback_error:
            logger.error(f"❌ Error creating fallback content: {fallback_error}")
            
            # Ultimate fallback - simple HTML elements, exactly 4 values
            simple_project_overview = html.Div("Loading project overview...", style={'padding': '1rem'})
            simple_header_cards = html.Div("Loading header cards...", style={'padding': '1rem'})
            simple_agency_header = html.Div("System Error", style={'color': 'red', 'padding': '1rem'})
            simple_main_cards = [html.Div("Loading...", style={'padding': '1rem'}) for _ in range(8)]
            
            # Return exactly 4 values in new order
            return simple_project_overview, simple_header_cards, simple_agency_header, simple_main_cards

# Export functions
__all__ = [
    'build_public_layout',
    'load_agency_data',
    'get_agency_rotation_data',
    'calculate_agency_metrics',
    'create_specific_metric_cards',
    'create_header_cards_grid',
    'create_header_card_1',        # NEW: Individual header card functions
    'create_header_card_2',        # NEW
    'create_header_card_3',        # NEW
    'create_header_card_4',        # NEW
    'create_project_overview_header',
    'get_display_agency_name',
    'AGENCY_NAMES'
]

def register_public_layout_callbacks():
    """Register public layout callbacks - REQUIRED FOR DASH TO FIND CALLBACKS"""
    # The callback is already defined above with @callback decorator
    # This function exists to ensure callbacks are properly registered
    # when the module is imported
    pass

# ✅ CRITICAL: Auto-register callbacks when module is imported
try:
    register_public_layout_callbacks()
    print("✅ Public layout callbacks registered successfully")
except Exception as e:
    print(f"❌ Failed to register public layout callbacks: {e}")
