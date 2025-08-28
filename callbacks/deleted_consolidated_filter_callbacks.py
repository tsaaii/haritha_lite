# callbacks/consolidated_filter_callbacks.py
"""
CONSOLIDATED CALLBACK STRUCTURE - NO DUPLICATES
This replaces multiple callback files to eliminate duplicate outputs
"""

from dash import callback, Input, Output, State, html, ctx, ALL
from dash.exceptions import PreventUpdate
import pandas as pd
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

def register_consolidated_callbacks():
    """Register all filter callbacks with NO duplicates"""
    
    # ========================================
    # 1. SINGLE CALLBACK FOR FILTER OPTIONS
    # ========================================
    @callback(
        [Output('analytics-filter-container-agency-filter', 'options'),
         Output('analytics-filter-container-cluster-filter', 'options'),
         Output('analytics-filter-container-site-filter', 'options')],
        [Input('analytics-filter-container', 'id')],
        prevent_initial_call=True
    )


    def update_analytics_filter_options(component_id):
        """SINGLE callback for updating filter dropdown options"""
        try:
            from data_loader import get_global_data, get_filter_options
            df = get_global_data()
            
            if df.empty:
                logger.warning("No data available for filter options")
                raise Exception("No data available")
            
            options = get_filter_options(df)
            
            logger.info(f"✅ Updated analytics filter options: {len(options['agencies'])-1} agencies, {len(options['clusters'])-1} clusters, {len(options['sites'])-1} sites")
            return options['agencies'], options['clusters'], options['sites']
            
        except Exception as e:
            logger.error(f"❌ Error updating filter options: {e}")
            
            # Fallback options
            fallback_agencies = [{'label': 'All Agencies', 'value': 'all'}]
            fallback_clusters = [{'label': 'All Clusters', 'value': 'all'}]
            fallback_sites = [{'label': 'All Sites', 'value': 'all'}]
            
            return fallback_agencies, fallback_clusters, fallback_sites

    # ========================================
    # 2. SINGLE CALLBACK FOR APPLYING FILTERS
    # ========================================
    @callback(
        [Output('filtered-data-display', 'children'),
         Output('analytics-filter-container-status', 'style'),
         Output('analytics-filter-container-status-text', 'children')],
        [Input('analytics-filter-container-apply-btn', 'n_clicks')],
        [State('analytics-filter-container-agency-filter', 'value'),
         State('analytics-filter-container-cluster-filter', 'value'),
         State('analytics-filter-container-site-filter', 'value'),
         State('analytics-filter-container-date-filter', 'start_date'),
         State('analytics-filter-container-date-filter', 'end_date'),
         State('current-theme', 'data')],
        prevent_initial_call=True
    )
    def apply_analytics_filters(n_clicks, agency, cluster, site, start_date, end_date, theme_name):
        """SINGLE callback for applying filters and updating display"""
        if not n_clicks:
            raise PreventUpdate
        
        try:
            from utils.theme_utils import get_theme_styles
            from data_loader import get_global_data, filter_data, create_filtered_data_display
            
            theme_styles = get_theme_styles(theme_name or 'dark')
            theme = theme_styles["theme"]
            
            # Load and filter data
            df = get_global_data()
            filtered_df = filter_data(df, agency, cluster, site, start_date, end_date)
            
            # Create display
            filtered_display = create_filtered_data_display(filtered_df, theme)
            
            # Update status
            status_style = {"display": "block", "marginTop": "1rem"}
            status_text = f"✅ Applied filters: {len(filtered_df)} records found"
            
            logger.info(f"Applied analytics filters: {len(filtered_df)} records")
            return filtered_display, status_style, status_text
            
        except Exception as e:
            logger.error(f"Error applying filters: {e}")
            
            error_display = html.Div([
                html.Div("❌ Error applying filters", style={
                    "color": "#ff4444",
                    "textAlign": "center",
                    "padding": "2rem"
                })
            ])
            
            status_style = {"display": "block"}
            status_text = "Error occurred while filtering data"
            
            return error_display, status_style, status_text

    # ========================================
    # 3. SINGLE CALLBACK FOR RESETTING FILTERS
    # ========================================
    @callback(
        [Output('analytics-filter-container-agency-filter', 'value'),
         Output('analytics-filter-container-cluster-filter', 'value'),
         Output('analytics-filter-container-site-filter', 'value'),
         Output('analytics-filter-container-date-filter', 'start_date'),
         Output('analytics-filter-container-date-filter', 'end_date')],
        [Input('analytics-filter-container-reset-btn', 'n_clicks')],
        prevent_initial_call=True
    )
    def reset_analytics_filters(n_clicks):
        """SINGLE callback for resetting all filters"""
        if not n_clicks:
            raise PreventUpdate
        
        # Default date range (last 30 days)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        logger.info("Analytics filters reset to default values")
        return 'all', 'all', 'all', start_date.date(), end_date.date()

    # ========================================
    # 4. EXPORT CALLBACK (NO DUPLICATES)
    # ========================================
    @callback(
        Output('analytics-export-status', 'children'),
        [Input('analytics-filter-container-export-btn', 'n_clicks')],
        [State('analytics-filter-container-agency-filter', 'value'),
         State('analytics-filter-container-cluster-filter', 'value'),
         State('analytics-filter-container-site-filter', 'value'),
         State('analytics-filter-container-date-filter', 'start_date'),
         State('analytics-filter-container-date-filter', 'end_date'),
         State('current-theme', 'data')],
        prevent_initial_call=True
    )
    def export_filtered_data(n_clicks, agency, cluster, site, start_date, end_date, theme_name):
        """Handle export of filtered data"""
        if not n_clicks:
            raise PreventUpdate
        
        try:
            from data_loader import get_global_data, filter_data
            
            # Load and filter data
            df = get_global_data()
            filtered_df = filter_data(df, agency, cluster, site, start_date, end_date)
            
            export_filename = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            record_count = len(filtered_df)
            
            return html.Div([
                html.Div("📊 Export Ready!", style={
                    "color": "#28a745",
                    "fontWeight": "bold",
                    "marginBottom": "0.5rem"
                }),
                html.Div(f"File: {export_filename}", style={"fontSize": "0.9rem"}),
                html.Div(f"Records: {record_count:,}", style={"fontSize": "0.9rem"})
            ])
            
        except Exception as e:
            logger.error(f"Export error: {e}")
            return html.Div("❌ Export failed", style={"color": "#dc3545"})


# ========================================
# PATTERN CALLBACK (for dynamic containers)
# ========================================
@callback(
    [Output({'type': 'filter-container-agency', 'index': ALL}, 'options'),
     Output({'type': 'filter-container-cluster', 'index': ALL}, 'options'),
     Output({'type': 'filter-container-site', 'index': ALL}, 'options')],
    [Input({'type': 'filter-container', 'index': ALL}, 'id')],
    prevent_initial_call=True
)
def update_pattern_filter_options(container_ids):
    """Pattern callback for dynamic filter containers - NO DUPLICATES"""
    if not container_ids:
        raise PreventUpdate
    
    try:
        from data_loader import get_global_data, get_filter_options
        
        df = get_global_data()
        options = get_filter_options(df)
        
        # Return options for all matching containers
        num_containers = len(container_ids)
        agencies = [options['agencies']] * num_containers
        clusters = [options['clusters']] * num_containers
        sites = [options['sites']] * num_containers
        
        return agencies, clusters, sites
        
    except Exception as e:
        logger.error(f"Pattern callback error: {e}")
        
        # Fallback
        fallback_agencies = [{'label': 'All', 'value': 'all'}]
        fallback_clusters = [{'label': 'All', 'value': 'all'}]
        fallback_sites = [{'label': 'All', 'value': 'all'}]
        
        num_containers = len(container_ids)
        return ([fallback_agencies] * num_containers, 
                [fallback_clusters] * num_containers, 
                [fallback_sites] * num_containers)


# ========================================
# MAIN REGISTRATION FUNCTION
# ========================================
def register_all_callbacks():
    """Register all callbacks - call this ONCE in main.py"""
    register_consolidated_callbacks()
    logger.info("✅ All callbacks registered with NO duplicates")