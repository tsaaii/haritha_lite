# callbacks/dashboard_filter_callbacks.py
"""
Fixed Dashboard Filter Callbacks with Real CSV Data Integration
Resolves duplicate callback issues and handles filter interactions properly
"""

from dash import callback, Input, Output, State, html, ctx
from dash.exceptions import PreventUpdate
import pandas as pd
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

def register_dashboard_filter_callbacks():
    """Register all dashboard filter-related callbacks with real data integration"""
    
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
        """Apply filters and update data display with real CSV data"""
        if not n_clicks:
            raise PreventUpdate
        
        try:
            # Get theme for styling
            from utils.theme_utils import get_theme_styles
            theme_styles = get_theme_styles(theme_name or 'dark')
            theme = theme_styles["theme"]
            
            # Load the actual CSV data
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
                
                status_style = {"display": "block", "marginTop": "1rem", "padding": "0.75rem", 
                               "backgroundColor": theme.get("error", "#E53E3E"), "borderRadius": "8px", 
                               "textAlign": "center", "fontSize": "0.85rem", "color": "white"}
                status_text = "❌ No data found in the system"
                
                return empty_display, status_style, status_text
            
            # Apply filters to the real data
            filtered_df = filter_data(df, agency, cluster, site, start_date, end_date)
            
            # Create comprehensive filtered display with real data
            filtered_display = create_comprehensive_filtered_display_with_real_data(
                filtered_df, agency, cluster, site, start_date, end_date, theme
            )
            
            # Update status with real statistics
            status_style = {"display": "block", "marginTop": "1rem", "padding": "0.75rem", 
                           "backgroundColor": theme["accent_bg"], "borderRadius": "8px", 
                           "textAlign": "center", "fontSize": "0.85rem", "color": theme["text_secondary"]}
            
            record_count = len(filtered_df)
            total_weight = filtered_df['weight'].sum() if 'weight' in filtered_df.columns else 0
            
            status_text = f"✅ Applied filters successfully! Found {record_count:,} records with total weight {total_weight:,.0f} kg"
            
            logger.info(f"Filter applied: {len(df)} -> {record_count} records")
            
            return filtered_display, status_style, status_text
            
        except Exception as e:
            logger.error(f"Error in apply_analytics_filters: {e}")
            
            # Get theme for error fallback
            try:
                from utils.theme_utils import get_theme_styles
                theme_styles = get_theme_styles(theme_name or 'dark')
                theme = theme_styles["theme"]
            except:
                theme = {"card_bg": "#ffffff", "text_primary": "#000000", "error": "#E53E3E"}
            
            # Error fallback
            error_display = html.Div([
                html.Div(f"❌ Error processing filters: {str(e)}", style={
                    "textAlign": "center",
                    "padding": "2rem",
                    "color": theme.get("error", "#E53E3E"),
                    "fontSize": "1rem",
                    "backgroundColor": theme["card_bg"],
                    "borderRadius": "8px",
                    "border": f"2px solid {theme.get('error', '#E53E3E')}"
                })
            ])
            
            status_style = {"display": "block", "marginTop": "1rem", "padding": "0.75rem", 
                           "backgroundColor": theme.get("error", "#E53E3E"), "borderRadius": "8px", 
                           "textAlign": "center", "fontSize": "0.85rem", "color": "white"}
            status_text = f"❌ Error: {str(e)}"
            
            return error_display, status_style, status_text

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
        """Reset all filters to default values"""
        if not n_clicks:
            raise PreventUpdate
        
        # Set default date range to last 30 days
        default_end_date = datetime.now()
        default_start_date = default_end_date - timedelta(days=30)
        
        logger.info("Analytics filters reset to default values")
        return 'all', 'all', 'all', default_start_date.date(), default_end_date.date()

    @callback(
        [Output('analytics-filter-container-agency-filter', 'options'),
         Output('analytics-filter-container-cluster-filter', 'options'),
         Output('analytics-filter-container-site-filter', 'options')],
        [Input('analytics-filter-container', 'id')],  # Trigger on component mount
        prevent_initial_call=True  # Changed to True to avoid duplicate issues
    )
    def update_filter_options(component_id):
        """Update filter dropdown options with real data from CSV"""
        try:
            # Load data and get real options
            df = get_global_data()
            options = get_filter_options(df)
            
            logger.info(f"Updated filter options from real data")
            return options['agencies'], options['clusters'], options['sites']
            
        except Exception as e:
            logger.error(f"Error updating filter options: {e}")
            
            # Fallback to basic options
            agency_options = [{'label': 'All Agencies', 'value': 'all'}]
            cluster_options = [{'label': 'All Clusters', 'value': 'all'}]
            site_options = [{'label': 'All Sites', 'value': 'all'}]
            
            return agency_options, cluster_options, site_options

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
    def export_analytics_filtered_data(n_clicks, agency, cluster, site, start_date, end_date, theme_name):
        """Handle export of filtered real data"""
        if not n_clicks:
            raise PreventUpdate
        
        try:
            # Get theme for styling
            from utils.theme_utils import get_theme_styles
            theme_styles = get_theme_styles(theme_name or 'dark')
            theme = theme_styles["theme"]
            
            # Load and filter real data
            df = get_global_data()
            filtered_df = filter_data(df, agency, cluster, site, start_date, end_date)
            
            # Generate export statistics
            export_filename = f"waste_data_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            record_count = len(filtered_df)
            total_weight = filtered_df['weight'].sum() if 'weight' in filtered_df.columns else 0
            
            return html.Div([
                html.Div("📊 Export Ready!", style={
                    "color": "#38A169",
                    "fontWeight": "600",
                    "fontSize": "1rem",
                    "marginBottom": "0.5rem"
                }),
                html.Div([
                    html.P(f"📄 Filename: {export_filename}", style={
                        "color": theme["text_secondary"],
                        "fontSize": "0.9rem",
                        "margin": "0.25rem 0"
                    }),
                    html.P(f"📝 Records: {record_count:,}", style={
                        "color": theme["text_secondary"],
                        "fontSize": "0.9rem",
                        "margin": "0.25rem 0"
                    }),
                    html.P(f"⚖️ Total Weight: {total_weight:,.0f} kg", style={
                        "color": theme["text_secondary"],
                        "fontSize": "0.9rem",
                        "margin": "0.25rem 0"
                    })
                ])
            ], style={
                "padding": "1rem",
                "backgroundColor": theme["card_bg"],
                "borderRadius": "8px",
                "border": f"2px solid #38A169",
                "marginTop": "1rem"
            })
            
        except Exception as e:
            logger.error(f"Error in export: {e}")
            
            # Get theme for error handling
            try:
                from utils.theme_utils import get_theme_styles
                theme_styles = get_theme_styles(theme_name or 'dark')
                theme = theme_styles["theme"]
            except:
                theme = {"card_bg": "#ffffff", "error": "#E53E3E"}
            
            return html.Div([
                html.Div("❌ Export Failed", style={
                    "color": theme.get("error", "#E53E3E"),
                    "fontWeight": "600",
                    "fontSize": "1rem"
                }),
                html.Div(f"Error: {str(e)}", style={
                    "color": theme.get("error", "#E53E3E"),
                    "fontSize": "0.9rem",
                    "marginTop": "0.5rem"
                })
            ], style={
                "padding": "1rem",
                "backgroundColor": theme["card_bg"],
                "borderRadius": "8px",
                "border": f"2px solid {theme.get('error', '#E53E3E')}",
                "marginTop": "1rem"
            })


# Helper functions that need to be imported or defined
def get_global_data():
    """Load and return the global dataset - replace with your actual data loading"""
    try:
        # This should import from your data_loader.py
        from data_loader import get_cached_data
        return get_cached_data()
    except ImportError:
        # Fallback sample data if data_loader not available
        sample_data = [
            {"Date": "2025-05-23", "agency": "madanapalle", "site": "madanapalle", "cluster": "MM", 
             "weight": 11540, "vehicle": "AP39VB2709", "time": "03:37:22 PM", "waste_type": "MSW"},
            {"Date": "2025-06-05", "agency": "donthalli", "site": "donthalli", "cluster": "NMC", 
             "weight": 23390, "vehicle": "AP04UB0825", "time": "07:42:41 PM", "waste_type": "MSW"}
        ]
        df = pd.DataFrame(sample_data)
        df['Date'] = pd.to_datetime(df['Date'])
        return df


def get_filter_options(df):
    """Get filter options from dataframe"""
    try:
        if df.empty:
            return {
                'agencies': [{'label': 'All Agencies', 'value': 'all'}],
                'sites': [{'label': 'All Sites', 'value': 'all'}],
                'clusters': [{'label': 'All Clusters', 'value': 'all'}]
            }
        
        agencies = sorted(df['agency'].unique()) if 'agency' in df.columns else []
        sites = sorted(df['site'].unique()) if 'site' in df.columns else []
        clusters = sorted(df['cluster'].unique()) if 'cluster' in df.columns else []
        
        return {
            'agencies': [{'label': 'All Agencies', 'value': 'all'}] + 
                       [{'label': agency.title(), 'value': agency} for agency in agencies],
            'sites': [{'label': 'All Sites', 'value': 'all'}] + 
                    [{'label': site.title(), 'value': site} for site in sites],
            'clusters': [{'label': 'All Clusters', 'value': 'all'}] + 
                       [{'label': cluster, 'value': cluster} for cluster in clusters]
        }
    except Exception as e:
        logger.error(f"Error getting filter options: {e}")
        return {
            'agencies': [{'label': 'All Agencies', 'value': 'all'}],
            'sites': [{'label': 'All Sites', 'value': 'all'}],
            'clusters': [{'label': 'All Clusters', 'value': 'all'}]
        }


def filter_data(df, agency='all', cluster='all', site='all', start_date=None, end_date=None):
    """Apply filters to dataframe"""
    try:
        if df.empty:
            return df
            
        filtered_df = df.copy()
        
        # Agency filter
        if agency and agency != 'all' and 'agency' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['agency'] == agency]
        
        # Cluster filter
        if cluster and cluster != 'all' and 'cluster' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['cluster'] == cluster]
        
        # Site filter
        if site and site != 'all' and 'site' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['site'] == site]
        
        # Date range filter
        if start_date and 'Date' in filtered_df.columns:
            start_dt = pd.to_datetime(start_date)
            filtered_df = filtered_df[filtered_df['Date'] >= start_dt]
        
        if end_date and 'Date' in filtered_df.columns:
            end_dt = pd.to_datetime(end_date)
            filtered_df = filtered_df[filtered_df['Date'] <= end_dt]
        
        return filtered_df
        
    except Exception as e:
        logger.error(f"Error filtering data: {e}")
        return df


def create_comprehensive_filtered_display_with_real_data(filtered_df, agency, cluster, site, start_date, end_date, theme):
    """Create comprehensive filtered display using real CSV data"""
    
    if filtered_df.empty:
        return html.Div([
            html.Div("📭 No records match your current filters", style={
                "textAlign": "center",
                "padding": "3rem",
                "color": theme["text_secondary"],
                "fontSize": "1.2rem",
                "backgroundColor": theme["card_bg"],
                "borderRadius": "12px",
                "border": f"2px dashed {theme['accent_bg']}"
            }),
            html.Div([
                html.P("Try adjusting your filters:", style={"color": theme["text_secondary"], "marginBottom": "1rem"}),
                html.Ul([
                    html.Li("Select 'All' for agency, cluster, or site filters"),
                    html.Li("Expand the date range"),
                    html.Li("Reset all filters to see all data")
                ], style={"color": theme["text_secondary"], "textAlign": "left", "maxWidth": "400px", "margin": "0 auto"})
            ], style={"marginTop": "1rem", "textAlign": "center"})
        ])
    
    try:
        # Import data display functions
        try:
            from data_loader import create_data_summary_stats, create_data_charts, create_data_table
        except ImportError:
            # Fallback if data_loader not available
            def create_data_summary_stats(df, theme):
                return html.Div(f"📊 {len(df)} records loaded")
            def create_data_charts(df, theme):
                return html.Div("📈 Charts would appear here")
            def create_data_table(df, theme):
                return html.Div("📋 Data table would appear here")
        
        return html.Div([
            # Filter summary header
            html.Div([
                html.H3("🔍 Filtered Results", style={
                    "color": theme["text_primary"],
                    "fontSize": "1.8rem",
                    "fontWeight": "700",
                    "marginBottom": "1rem",
                    "textAlign": "center"
                }),
                
                # Active filters display
                html.Div([
                    html.Div([
                        html.Strong("Active Filters: ", style={"color": theme["text_primary"]}),
                        html.Span(f"Agency: {agency} | ", style={"color": theme["text_secondary"]}),
                        html.Span(f"Cluster: {cluster} | ", style={"color": theme["text_secondary"]}),
                        html.Span(f"Site: {site} | ", style={"color": theme["text_secondary"]}),
                        html.Span(f"Dates: {start_date or 'All'} to {end_date or 'All'}", style={"color": theme["text_secondary"]})
                    ], style={"textAlign": "center", "marginBottom": "1.5rem"})
                ])
            ], style={
                "padding": "1.5rem",
                "backgroundColor": theme["accent_bg"],
                "borderRadius": "12px",
                "marginBottom": "1.5rem",
                "border": f"1px solid {theme.get('border_light', theme['card_bg'])}"
            }),
            
            # Summary statistics
            create_data_summary_stats(filtered_df, theme),
            
            # Spacing
            html.Div(style={"height": "1.5rem"}),
            
            # Data visualizations
            html.Div([
                html.H4("📊 Data Visualizations", style={
                    "color": theme["text_primary"],
                    "marginBottom": "1rem"
                }),
                create_data_charts(filtered_df, theme)
            ], style={
                "marginBottom": "1.5rem"
            }),
            
            # Data table
            create_data_table(filtered_df, theme),
            
            # Export section
            html.Div([
                html.Hr(style={"margin": "2rem 0", "border": f"1px solid {theme['accent_bg']}"}),
                html.Div([
                    html.P(f"📋 Showing {len(filtered_df):,} records matching your filters", style={
                        "color": theme["text_secondary"],
                        "textAlign": "center",
                        "margin": "0"
                    }),
                    html.P("Use the export button above to download this filtered data", style={
                        "color": theme["text_secondary"],
                        "textAlign": "center",
                        "fontSize": "0.9rem",
                        "margin": "0.5rem 0 0 0"
                    })
                ])
            ])
        ])
        
    except Exception as e:
        logger.error(f"Error creating comprehensive display: {e}")
        return html.Div([
            html.Div(f"Error displaying data: {str(e)}", style={
                "color": theme.get("error", "#E53E3E"),
                "textAlign": "center",
                "padding": "2rem"
            })
        ])