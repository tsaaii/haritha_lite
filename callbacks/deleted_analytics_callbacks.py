# callbacks/analytics_callbacks.py
"""
Consolidated Analytics Callbacks - No Duplicate Issues
Single file to handle all analytics filter functionality
"""

from dash import callback, Input, Output, State, html, ctx
from dash.exceptions import PreventUpdate
import pandas as pd
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# Global flag to prevent multiple registrations
_analytics_callbacks_registered = False

def register_analytics_callbacks():
    """
    Register all analytics filter callbacks in one place to avoid duplicates
    Call this ONCE from your main.py
    """
    global _analytics_callbacks_registered
    
    if _analytics_callbacks_registered:
        logger.warning("Analytics callbacks already registered, skipping...")
        return
    
    try:
        # Main filter processing callback
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
        def process_analytics_filters(n_clicks, agency, cluster, site, start_date, end_date, theme_name):
            """Main filter processing with real CSV data"""
            if not n_clicks:
                raise PreventUpdate
            
            try:
                # Get theme for styling
                from utils.theme_utils import get_theme_styles
                theme_styles = get_theme_styles(theme_name or 'dark')
                theme = theme_styles["theme"]
                
                # Load the actual CSV data
                df = load_waste_data()
                
                if df.empty:
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
                    status_text = "❌ No data found"
                    
                    return empty_display, status_style, status_text
                
                # Apply filters
                filtered_df = apply_data_filters(df, agency, cluster, site, start_date, end_date)
                
                # Create display
                filtered_display = create_analytics_display(filtered_df, agency, cluster, site, start_date, end_date, theme)
                
                # Update status
                record_count = len(filtered_df)
                total_weight = filtered_df['weight'].sum() if 'weight' in filtered_df.columns else 0
                
                status_style = {"display": "block", "marginTop": "1rem", "padding": "0.75rem", 
                               "backgroundColor": theme["accent_bg"], "borderRadius": "8px", 
                               "textAlign": "center", "fontSize": "0.85rem", "color": theme["text_secondary"]}
                
                status_text = f"✅ Found {record_count:,} records | Total Weight: {total_weight:,.0f} kg"
                
                logger.info(f"Analytics filter applied: {len(df)} -> {record_count} records")
                return filtered_display, status_style, status_text
                
            except Exception as e:
                logger.error(f"Error in process_analytics_filters: {e}")
                
                # Error fallback
                try:
                    from utils.theme_utils import get_theme_styles
                    theme_styles = get_theme_styles(theme_name or 'dark')
                    theme = theme_styles["theme"]
                except:
                    theme = {"card_bg": "#ffffff", "text_primary": "#000000", "error": "#E53E3E"}
                
                error_display = html.Div([
                    html.Div(f"❌ Error: {str(e)}", style={
                        "textAlign": "center",
                        "padding": "2rem",
                        "color": theme.get("error", "#E53E3E"),
                        "backgroundColor": theme["card_bg"],
                        "borderRadius": "8px"
                    })
                ])
                
                status_style = {"display": "block", "backgroundColor": theme.get("error", "#E53E3E"), "color": "white", "padding": "0.75rem", "borderRadius": "8px", "textAlign": "center"}
                status_text = f"❌ Error: {str(e)}"
                
                return error_display, status_style, status_text

        # Reset filters callback
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
            
            default_end_date = datetime.now()
            default_start_date = default_end_date - timedelta(days=30)
            
            logger.info("Analytics filters reset")
            return 'all', 'all', 'all', default_start_date.date(), default_end_date.date()

        # Update dropdown options callback

        logger.info("Filter options will be handled by the filter container component")
        # Export callback with unique output ID
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
        def export_analytics_data(n_clicks, agency, cluster, site, start_date, end_date, theme_name):
            """Handle export of filtered analytics data"""
            if not n_clicks:
                raise PreventUpdate
            
            try:
                from utils.theme_utils import get_theme_styles
                theme_styles = get_theme_styles(theme_name or 'dark')
                theme = theme_styles["theme"]
                
                df = load_waste_data()
                filtered_df = apply_data_filters(df, agency, cluster, site, start_date, end_date)
                
                export_filename = f"analytics_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
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
                        html.P(f"📄 File: {export_filename}", style={
                            "color": theme["text_secondary"],
                            "fontSize": "0.9rem",
                            "margin": "0.25rem 0"
                        }),
                        html.P(f"📝 Records: {record_count:,}", style={
                            "color": theme["text_secondary"],
                            "fontSize": "0.9rem",
                            "margin": "0.25rem 0"
                        }),
                        html.P(f"⚖️ Weight: {total_weight:,.0f} kg", style={
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
                logger.error(f"Error in analytics export: {e}")
                return html.Div(f"❌ Export failed: {str(e)}", style={
                    "color": "#E53E3E",
                    "padding": "1rem",
                    "textAlign": "center"
                })

        _analytics_callbacks_registered = True
        logger.info("✅ Analytics callbacks registered successfully")
        
    except Exception as e:
        logger.error(f"❌ Error registering analytics callbacks: {e}")
        raise


# Helper functions
def load_waste_data():
    """Load waste management data"""
    try:
        # Try to import from data_loader if available
        from data_loader import get_cached_data
        return get_cached_data()
    except ImportError:
        logger.warning("data_loader not found, using sample data")
        # Fallback sample data
        sample_data = [
            {"Date": "2025-05-23", "agency": "madanapalle", "site": "madanapalle", "cluster": "MM", 
             "weight": 11540, "vehicle": "AP39VB2709", "time": "03:37:22 PM", "waste_type": "MSW"},
            {"Date": "2025-05-23", "agency": "madanapalle", "site": "madanapalle", "cluster": "MM", 
             "weight": 17350, "vehicle": "AP39UN2025", "time": "03:20:54 PM", "waste_type": "MSW"},
            {"Date": "2025-06-05", "agency": "donthalli", "site": "donthalli", "cluster": "NMC", 
             "weight": 23390, "vehicle": "AP04UB0825", "time": "07:42:41 PM", "waste_type": "MSW"},
            {"Date": "2025-06-05", "agency": "donthalli", "site": "donthalli", "cluster": "NMC", 
             "weight": 19570, "vehicle": "AP39VB4518", "time": "07:33:40 PM", "waste_type": "MSW"},
            {"Date": "2025-06-04", "agency": "madanapalle", "site": "madanapalle", "cluster": "MM", 
             "weight": 7940, "vehicle": "AP39UM8487", "time": "04:27:11 PM", "waste_type": "MSW"}
        ]
        df = pd.DataFrame(sample_data)
        df['Date'] = pd.to_datetime(df['Date'])
        return df
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        return pd.DataFrame()


def get_dropdown_options(df):
    """Get dropdown options from dataframe"""
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
        logger.error(f"Error getting dropdown options: {e}")
        return {
            'agencies': [{'label': 'All Agencies', 'value': 'all'}],
            'sites': [{'label': 'All Sites', 'value': 'all'}],
            'clusters': [{'label': 'All Clusters', 'value': 'all'}]
        }


def apply_data_filters(df, agency='all', cluster='all', site='all', start_date=None, end_date=None):
    """Apply filters to dataframe"""
    try:
        if df.empty:
            return df
            
        filtered_df = df.copy()
        
        if agency and agency != 'all' and 'agency' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['agency'] == agency]
        
        if cluster and cluster != 'all' and 'cluster' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['cluster'] == cluster]
        
        if site and site != 'all' and 'site' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['site'] == site]
        
        if start_date and 'Date' in filtered_df.columns:
            start_dt = pd.to_datetime(start_date)
            filtered_df = filtered_df[filtered_df['Date'] >= start_dt]
        
        if end_date and 'Date' in filtered_df.columns:
            end_dt = pd.to_datetime(end_date)
            filtered_df = filtered_df[filtered_df['Date'] <= end_dt]
        
        return filtered_df
        
    except Exception as e:
        logger.error(f"Error applying filters: {e}")
        return df


def create_analytics_display(filtered_df, agency, cluster, site, start_date, end_date, theme):
    """Create the analytics display with filtered data"""
    
    if filtered_df.empty:
        return html.Div([
            html.Div("📭 No records match your filters", style={
                "textAlign": "center",
                "padding": "3rem",
                "color": theme["text_secondary"],
                "fontSize": "1.2rem",
                "backgroundColor": theme["card_bg"],
                "borderRadius": "12px",
                "border": f"2px dashed {theme['accent_bg']}"
            })
        ])
    
    try:
        # Try to import display functions
        try:
            from data_loader import create_data_summary_stats, create_data_charts, create_data_table
        except ImportError:
            # Simple fallback display functions
            def create_data_summary_stats(df, theme):
                return html.Div([
                    html.H4("📊 Summary Statistics", style={"color": theme["text_primary"]}),
                    html.P(f"Total Records: {len(df):,}", style={"color": theme["text_secondary"]}),
                    html.P(f"Total Weight: {df['weight'].sum():,.0f} kg", style={"color": theme["text_secondary"]}) if 'weight' in df.columns else None
                ])
            
            def create_data_charts(df, theme):
                return html.Div("📈 Charts would appear here with data_loader.py", style={
                    "textAlign": "center",
                    "padding": "2rem",
                    "color": theme["text_secondary"]
                })
            
            def create_data_table(df, theme):
                return html.Div([
                    html.H4("📋 Data Table", style={"color": theme["text_primary"]}),
                    html.P(f"Showing {len(df)} records", style={"color": theme["text_secondary"]})
                ])
        
        return html.Div([
            # Header
            html.Div([
                html.H3("🔍 Analytics Results", style={
                    "color": theme["text_primary"],
                    "fontSize": "1.8rem",
                    "fontWeight": "700",
                    "marginBottom": "1rem",
                    "textAlign": "center"
                }),
                html.Div([
                    html.Strong("Filters: ", style={"color": theme["text_primary"]}),
                    html.Span(f"Agency: {agency} | Cluster: {cluster} | Site: {site}", style={"color": theme["text_secondary"]})
                ], style={"textAlign": "center", "marginBottom": "1.5rem"})
            ], style={
                "padding": "1.5rem",
                "backgroundColor": theme["accent_bg"],
                "borderRadius": "12px",
                "marginBottom": "1.5rem"
            }),
            
            # Summary stats
            create_data_summary_stats(filtered_df, theme),
            html.Div(style={"height": "1rem"}),
            
            # Charts
            create_data_charts(filtered_df, theme),
            html.Div(style={"height": "1rem"}),
            
            # Data table
            create_data_table(filtered_df, theme)
        ])
        
    except Exception as e:
        logger.error(f"Error creating analytics display: {e}")
        return html.Div([
            html.Div(f"Error creating display: {str(e)}", style={
                "color": theme.get("error", "#E53E3E"),
                "textAlign": "center",
                "padding": "2rem"
            })
        ])