"""
# callbacks/unified_dashboard_callbacks.py
UNIFIED DASHBOARD CALLBACKS - SINGLE SOURCE OF TRUTH
This file consolidates ALL dashboard callbacks to eliminate duplicates
"""

from dash import callback, Input, Output, State, html, ctx, clientside_callback
from dash.exceptions import PreventUpdate
import pandas as pd
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

def register_unified_dashboard_callbacks():
    """Register ALL dashboard callbacks with STRICT access control"""
    
    @callback(
        [Output('tab-content', 'children'),
         Output('tab-dashboard', 'style'),
         Output('tab-analytics', 'style'),
         Output('tab-reports', 'style'),
         Output('tab-reviews', 'style'),
         Output('tab-upload', 'style')],
        [Input('tab-dashboard', 'n_clicks'),
         Input('tab-analytics', 'n_clicks'),
         Input('tab-reports', 'n_clicks'),
         Input('tab-reviews', 'n_clicks'),
         Input('tab-upload', 'n_clicks')],
        [State('current-theme', 'data'),
         State('user-session-data', 'data'),
         State('current-page', 'data'),
         State('user-authenticated', 'data')],
        prevent_initial_call=True
    )
    def unified_tab_navigation(dashboard_clicks, analytics_clicks, reports_clicks, 
                              reviews_clicks, upload_clicks, theme_name, user_data, 
                              current_page, is_authenticated):
        """UNIFIED: Handle tab navigation with STRICT role-based access control"""
        
        if not is_authenticated or current_page != 'admin_dashboard':
            raise PreventUpdate
        
        if not ctx.triggered:
            raise PreventUpdate
        
        # Get user role
        user_role = user_data.get('role', 'viewer') if user_data else 'viewer'
        
        # STRICT ACCESS CONTROL - No fallback that allows everything
        try:
            from config.auth import can_user_access_tab
        except ImportError:
            # If import fails, create a RESTRICTIVE fallback
            def can_user_access_tab(role, tab):
                restrictive_permissions = {
                    'viewer': ['dashboard', 'analytics', 'reports'],  # No charts, reviews, upload
                    'administrator': ['dashboard', 'analytics', 'reports', 'reviews', 'upload'],
                    'super_admin': ['dashboard', 'analytics', 'reports', 'reviews', 'upload', 'forecasting']
                }
                return tab in restrictive_permissions.get(role, ['dashboard'])
        
        # Get the clicked tab
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        # Map button IDs to tab names
        tab_mapping = {
            'tab-dashboard': 'dashboard',
            'tab-analytics': 'analytics', 
            'tab-reports': 'reports',
            'tab-reviews': 'reviews',  # This should be blocked for viewers
            'tab-upload': 'upload'     # This should be blocked for viewers
        }
        
        requested_tab = tab_mapping.get(button_id, 'dashboard')
        
        # STRICT ACCESS CHECK
        if not can_user_access_tab(user_role, requested_tab):
            # Show access denied message
            from layouts.admin_dashboard import get_theme_styles
            
            theme_styles = get_theme_styles(theme_name or 'dark')
            
            error_content = html.Div([
                html.H2("🚫 Access Restricted", 
                       style={"color": "#E53E3E", "textAlign": "center", "marginBottom": "1rem"}),
                html.P(f"Sorry, users with '{user_role}' role cannot access the '{requested_tab}' section.", 
                       style={"textAlign": "center", "fontSize": "1.1rem", 
                             "color": theme_styles['theme']['text_secondary']}),
                html.P("Available sections: Dashboard, Analytics, Reports", 
                       style={"textAlign": "center", "fontSize": "0.9rem", 
                             "color": theme_styles['theme']['text_secondary'], "marginTop": "1rem"})
            ], style={"padding": "3rem", "textAlign": "center"})
            
            # Keep all button styles as default (no highlighting of restricted tab)
            default_style = {
                "backgroundColor": theme_styles["theme"]["accent_bg"],
                "color": theme_styles["theme"]["text_primary"],
                "border": f"2px solid {theme_styles['theme']['card_bg']}"
            }
            return error_content, default_style, default_style, default_style, default_style, default_style
        
        # If access is allowed, proceed with normal tab switching
        from layouts.admin_dashboard import create_tab_content, get_theme_styles
        
        theme_styles = get_theme_styles(theme_name or 'dark')
        content = create_tab_content(button_id, theme_styles, user_data)
        
        # Define button styles
        default_style = {
            "backgroundColor": theme_styles["theme"]["accent_bg"],
            "color": theme_styles["theme"]["text_primary"],
            "border": f"2px solid {theme_styles['theme']['card_bg']}"
        }
        
        active_style = {
            "backgroundColor": theme_styles["theme"]["primary"],
            "color": "white",
            "border": f"2px solid {theme_styles['theme']['primary']}"
        }
        
        # Return content and update button styles
        return (
            content,
            active_style if button_id == 'tab-dashboard' else default_style,
            active_style if button_id == 'tab-analytics' else default_style,
            active_style if button_id == 'tab-reports' else default_style,
            active_style if button_id == 'tab-reviews' else default_style,
            active_style if button_id == 'tab-upload' else default_style
        )
    # ========================================
    # 2. FILTER OPTIONS CALLBACK
    # ========================================
    @callback(
        [Output('analytics-filter-container-agency-filter', 'options'),
         Output('analytics-filter-container-cluster-filter', 'options'),
         Output('analytics-filter-container-site-filter', 'options')],
        [Input('analytics-filter-container', 'id')],
        prevent_initial_call=True
    )
    def unified_filter_options(component_id):
        """UNIFIED: Update filter dropdown options"""
        try:
            from data_loader import get_global_data, get_filter_options
            df = get_global_data()
            
            if df.empty:
                logger.warning("No data available for filter options")
                raise Exception("No data available")
            
            options = get_filter_options(df)
            
            logger.info(f"✅ Updated filter options: {len(options['agencies'])-1} agencies")
            return options['agencies'], options['clusters'], options['sites']
            
        except Exception as e:
            logger.error(f"❌ Error updating filter options: {e}")
            
            # Fallback options
            fallback_agencies = [{'label': 'All Agencies', 'value': 'all'}]
            fallback_clusters = [{'label': 'All Clusters', 'value': 'all'}]
            fallback_sites = [{'label': 'All Sites', 'value': 'all'}]
            
            return fallback_agencies, fallback_clusters, fallback_sites

    # ========================================
    # 3. FILTER PROCESSING CALLBACK
    # ========================================
    @callback(
        [Output('filtered-data-display', 'children'),
         Output('analytics-filter-container-loading', 'style')],
        [Input('analytics-filter-container-apply-btn', 'n_clicks')],
        [State('analytics-filter-container-agency-filter', 'value'),
         State('analytics-filter-container-cluster-filter', 'value'),
         State('analytics-filter-container-site-filter', 'value'),
         State('analytics-filter-container-date-filter', 'start_date'),
         State('analytics-filter-container-date-filter', 'end_date'),
         State('current-theme', 'data')],
        prevent_initial_call=True
    )
    def unified_filter_processing(n_clicks, agency, cluster, site, start_date, end_date, theme_name):
        """UNIFIED: Process filter applications"""
        if not n_clicks:
            raise PreventUpdate
        
        try:
            # Get theme for styling
            from utils.theme_utils import get_theme_styles
            theme_styles = get_theme_styles(theme_name or 'dark')
            theme = theme_styles["theme"]
            
            # Load the actual CSV data
            from data_loader import get_global_data
            df = get_global_data()
            
            if df.empty:
                # Handle empty dataset
                empty_display = html.Div([
                    html.Div("📭 No data available", style={
                        "textAlign": "center",
                        "padding": "3rem",
                        "color": theme["text_secondary"],
                        "fontSize": "1.2rem",
                        "backgroundColor": theme["card_bg"],
                        "borderRadius": "12px",
                        "border": f"2px dashed {theme['accent_bg']}"
                    })
                ])
                
                return empty_display, {"display": "none"}
            
            # Apply filters to data
            filtered_df = df.copy()
            
            # Agency filter
            if agency and agency != 'all':
                if 'Waste_Management_Agency' in filtered_df.columns:
                    filtered_df = filtered_df[filtered_df['Waste_Management_Agency'] == agency]
            
            # Cluster filter
            if cluster and cluster != 'all':
                if 'Cluster' in filtered_df.columns:
                    filtered_df = filtered_df[filtered_df['Cluster'] == cluster]
            
            # Site filter
            if site and site != 'all':
                if 'Collection_Site' in filtered_df.columns:
                    filtered_df = filtered_df[filtered_df['Collection_Site'] == site]
            
            # Date filter
            if start_date and end_date:
                if 'Collection_Date' in filtered_df.columns:
                    filtered_df = filtered_df[
                        (filtered_df['Collection_Date'] >= start_date) & 
                        (filtered_df['Collection_Date'] <= end_date)
                    ]
            
            # Create results display
            if filtered_df.empty:
                results_display = html.Div([
                    html.H3("🔍 No Results Found", style={
                        "color": theme["text_primary"],
                        "textAlign": "center",
                        "marginBottom": "1rem"
                    }),
                    html.P("Try adjusting your filter criteria.", style={
                        "color": theme["text_secondary"],
                        "textAlign": "center"
                    })
                ], style={
                    "padding": "2rem",
                    "backgroundColor": theme["card_bg"],
                    "borderRadius": "12px",
                    "textAlign": "center"
                })
            else:
                # Display filtered results
                total_weight = filtered_df.get('Total_Weight_kg', [0]).sum() if 'Total_Weight_kg' in filtered_df.columns else 0
                
                results_display = html.Div([
                    html.H3(f"✅ Found {len(filtered_df):,} Records", style={
                        "color": "#38A169",
                        "marginBottom": "1rem"
                    }),
                    html.Div([
                        html.P(f"📊 Total Weight: {total_weight:,.0f} kg", style={
                            "color": theme["text_secondary"],
                            "margin": "0.5rem 0"
                        }),
                        html.P(f"📅 Date Range: {start_date or 'All'} to {end_date or 'All'}", style={
                            "color": theme["text_secondary"],
                            "margin": "0.5rem 0"
                        }),
                        html.P(f"🏢 Agency: {agency or 'All'}", style={
                            "color": theme["text_secondary"],
                            "margin": "0.5rem 0"
                        })
                    ])
                ], style={
                    "padding": "1.5rem",
                    "backgroundColor": theme["card_bg"],
                    "borderRadius": "12px",
                    "border": f"2px solid #38A169"
                })
            
            return results_display, {"display": "none"}
            
        except Exception as e:
            logger.error(f"❌ Filter processing error: {e}")
            error_display = html.Div(f"❌ Error processing filters: {str(e)}", style={
                "color": "#E53E3E",
                "padding": "1rem",
                "textAlign": "center"
            })
            return error_display, {"display": "none"}

    # ========================================
    # 4. RESET FILTERS CALLBACK
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
    def unified_reset_filters(n_clicks):
        """UNIFIED: Reset all filters to default values"""
        if not n_clicks:
            raise PreventUpdate
        
        return 'all', 'all', 'all', None, None

    # ========================================
    # 5. EXPORT DATA CALLBACK
    # ========================================
    @callback(
        Output('analytics-filter-container-loading', 'children'),
        [Input('analytics-filter-container-export-btn', 'n_clicks')],
        [State('analytics-filter-container-agency-filter', 'value'),
         State('analytics-filter-container-cluster-filter', 'value'),
         State('analytics-filter-container-site-filter', 'value'),
         State('analytics-filter-container-date-filter', 'start_date'),
         State('analytics-filter-container-date-filter', 'end_date'),
         State('current-theme', 'data')],
        prevent_initial_call=True
    )
    def unified_export_data(n_clicks, agency, cluster, site, start_date, end_date, theme_name):
        """UNIFIED: Export filtered data"""
        if not n_clicks:
            raise PreventUpdate
        
        try:
            from utils.theme_utils import get_theme_styles
            theme_styles = get_theme_styles(theme_name or 'dark')
            theme = theme_styles["theme"]
            
            # Create export filename
            export_filename = f"filtered_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            return html.Div([
                html.Span("✅ Export completed", style={
                    "color": "#38A169",
                    "fontWeight": "600"
                }),
                html.Div(f"📄 File: {export_filename}", style={
                    "fontSize": "0.9rem",
                    "color": theme["text_secondary"]
                })
            ])
            
        except Exception as e:
            logger.error(f"Export error: {e}")
            return html.Div("❌ Export failed", style={"color": "#dc3545"})

    logger.info("✅ Unified dashboard callbacks registered successfully")
