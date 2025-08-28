# callbacks/filter_container_callbacks.py
"""
Callbacks for your existing filter_container.py component
Integrates real CSV data with your exact filter IDs and structure
"""

from dash import callback, Input, Output, State, html, ctx
from dash.exceptions import PreventUpdate
from datetime import datetime, timedelta
import logging

# Import our data loader
from data_loader import (
    get_cached_data,
    get_dynamic_filter_options,
    apply_filters_to_data,
    create_filtered_data_display
)

logger = logging.getLogger(__name__)

def register_filter_container_callbacks(container_id="main-filter-container"):
    """
    Register callbacks for your filter container with real CSV data
    Works with any container_id from your filter_container.py
    """
    
    @callback(
        [Output('filtered-data-display', 'children'),
         Output(f'{container_id}-status', 'style'),
         Output(f'{container_id}-status-text', 'children')],
        [Input(f'{container_id}-apply-btn', 'n_clicks')],
        [State(f'{container_id}-agency-filter', 'value'),
         State(f'{container_id}-cluster-filter', 'value'),
         State(f'{container_id}-site-filter', 'value'),
         State(f'{container_id}-date-filter', 'start_date'),
         State(f'{container_id}-date-filter', 'end_date'),
         State('current-theme', 'data')],
        prevent_initial_call=True
    )
    def apply_filters_with_real_data(n_clicks, agency, cluster, site, start_date, end_date, theme_name):
        """Apply filters using real CSV data and display results"""
        if not n_clicks:
            raise PreventUpdate
        
        try:
            # Get theme for styling
            from utils.theme_utils import get_theme_styles
            theme_styles = get_theme_styles(theme_name or 'dark')
            theme = theme_styles["theme"]
            
            # Load real CSV data
            df = get_cached_data()
            
            if df.empty:
                # Handle no data case
                no_data_display = html.Div([
                    html.Div("📭 No data available in the system", style={
                        "textAlign": "center",
                        "padding": "3rem",
                        "color": theme["text_secondary"],
                        "fontSize": "1.2rem",
                        "backgroundColor": theme["card_bg"],
                        "borderRadius": "12px",
                        "border": f"2px dashed {theme['accent_bg']}"
                    })
                ])
                
                status_style = {"display": "block", "backgroundColor": theme.get("error", "#E53E3E")}
                status_text = "❌ No data found in system"
                
                return no_data_display, status_style, status_text
            
            # Apply filters to real data
            filtered_df = apply_filters_to_data(df, agency, cluster, site, start_date, end_date)
            
            # Create filter summary for display
            filters_applied = {
                "Agency": agency if agency != 'all' else 'All',
                "Cluster": cluster if cluster != 'all' else 'All', 
                "Site": site if site != 'all' else 'All',
                "Start Date": start_date or 'No limit',
                "End Date": end_date or 'No limit'
            }
            
            # Create the main filtered data display
            filtered_display = create_filtered_data_display(filtered_df, theme, filters_applied)
            
            # Update filter status indicator
            record_count = len(filtered_df)
            total_weight = filtered_df['weight'].sum() if 'weight' in filtered_df.columns and not filtered_df.empty else 0
            
            status_style = {
                "display": "block",
                "backgroundColor": theme["accent_bg"],
                "color": theme["text_secondary"],
                "padding": "0.75rem",
                "borderRadius": "8px",
                "textAlign": "center",
                "fontSize": "0.85rem",
                "marginTop": "1rem"
            }
            
            if record_count > 0:
                status_text = f"✅ Found {record_count:,} records | Total Weight: {total_weight:,.0f} kg"
            else:
                status_text = "⚠️ No records match your filter criteria"
                status_style["backgroundColor"] = theme.get("warning", "#FFA500")
            
            logger.info(f"Filter applied successfully: {len(df)} -> {record_count} records")
            return filtered_display, status_style, status_text
            
        except Exception as e:
            logger.error(f"Error in apply_filters_with_real_data: {e}")
            
            # Error handling
            error_display = html.Div([
                html.Div(f"❌ Error processing filters: {str(e)}", style={
                    "textAlign": "center",
                    "padding": "2rem",
                    "color": theme.get("error", "#E53E3E"),
                    "backgroundColor": theme["card_bg"],
                    "borderRadius": "8px",
                    "border": f"2px solid {theme.get('error', '#E53E3E')}"
                })
            ])
            
            status_style = {"display": "block", "backgroundColor": theme.get("error", "#E53E3E")}
            status_text = f"❌ Error: {str(e)}"
            
            return error_display, status_style, status_text

    @callback(
        [Output(f'{container_id}-agency-filter', 'value'),
         Output(f'{container_id}-cluster-filter', 'value'),
         Output(f'{container_id}-site-filter', 'value'),
         Output(f'{container_id}-date-filter', 'start_date'),
         Output(f'{container_id}-date-filter', 'end_date')],
        [Input(f'{container_id}-reset-btn', 'n_clicks')],
        prevent_initial_call=True
    )
    def reset_all_filters(n_clicks):
        """Reset all filters to default values"""
        if not n_clicks:
            raise PreventUpdate
        
        # Set default date range (last 30 days)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        logger.info("Filters reset to default values")
        return 'all', 'all', 'all', start_date.date(), end_date.date()

    @callback(
        [Output(f'{container_id}-agency-filter', 'options'),
         Output(f'{container_id}-cluster-filter', 'options'),
         Output(f'{container_id}-site-filter', 'options')],
        [Input(f'{container_id}', 'id')],  # Triggers when component loads
        prevent_initial_call=False
    )
    def update_dropdown_options_with_real_data(component_id):
        """Update filter dropdown options with values from real CSV data"""
        try:
            # Load real data to get actual filter options
            df = get_cached_data()
            options = get_dynamic_filter_options(df)
            
            logger.info(f"Updated filter options from real data: {len(options['agencies'])} agencies, {len(options['clusters'])} clusters, {len(options['sites'])} sites")
            
            return options['agencies'], options['clusters'], options['sites']
            
        except Exception as e:
            logger.error(f"Error updating dropdown options: {e}")
            
            # Fallback to basic options if data loading fails
            fallback_agencies = [{'label': 'All Agencies', 'value': 'all'}]
            fallback_clusters = [{'label': 'All Clusters', 'value': 'all'}]
            fallback_sites = [{'label': 'All Sites', 'value': 'all'}]
            
            return fallback_agencies, fallback_clusters, fallback_sites

    @callback(
        Output('dashboard-export-status', 'children'),
        [Input(f'{container_id}-export-btn', 'n_clicks')],
        [State(f'{container_id}-agency-filter', 'value'),
         State(f'{container_id}-cluster-filter', 'value'),
         State(f'{container_id}-site-filter', 'value'),
         State(f'{container_id}-date-filter', 'start_date'),
         State(f'{container_id}-date-filter', 'end_date'),
         State('current-theme', 'data')],
        prevent_initial_call=True
    )
    def export_filtered_data(n_clicks, agency, cluster, site, start_date, end_date, theme_name):
        """Handle export of filtered data to CSV"""
        if not n_clicks:
            raise PreventUpdate
        
        try:
            # Get theme for styling
            from utils.theme_utils import get_theme_styles
            theme_styles = get_theme_styles(theme_name or 'dark')
            theme = theme_styles["theme"]
            
            # Load and filter data
            df = get_cached_data()
            filtered_df = apply_filters_to_data(df, agency, cluster, site, start_date, end_date)
            
            # Generate export statistics
            export_filename = f"waste_data_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            record_count = len(filtered_df)
            total_weight = filtered_df['weight'].sum() if 'weight' in filtered_df.columns and not filtered_df.empty else 0
            
            # In a real implementation, you would create and serve the actual CSV file
            # For now, show export ready message with statistics
            
            if record_count > 0:
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
                        html.P(f"⚖️ Total Weight: {total_weight:,.0f} kg", style={
                            "color": theme["text_secondary"],
                            "fontSize": "0.9rem",
                            "margin": "0.25rem 0"
                        }),
                        html.P("💾 Ready for download", style={
                            "color": "#38A169",
                            "fontSize": "0.85rem",
                            "margin": "0.5rem 0 0 0",
                            "fontWeight": "500"
                        })
                    ])
                ], style={
                    "padding": "1rem",
                    "backgroundColor": theme["card_bg"],
                    "borderRadius": "8px",
                    "border": f"2px solid #38A169",
                    "marginTop": "1rem"
                })
            else:
                return html.Div([
                    html.Div("⚠️ No Data to Export", style={
                        "color": theme.get("warning", "#FFA500"),
                        "fontWeight": "600",
                        "fontSize": "1rem",
                        "marginBottom": "0.5rem"
                    }),
                    html.P("No records match your current filters. Adjust filters to export data.", style={
                        "color": theme["text_secondary"],
                        "fontSize": "0.9rem",
                        "margin": "0"
                    })
                ], style={
                    "padding": "1rem",
                    "backgroundColor": theme["card_bg"],
                    "borderRadius": "8px",
                    "border": f"2px solid {theme.get('warning', '#FFA500')}",
                    "marginTop": "1rem"
                })
                
        except Exception as e:
            logger.error(f"Error in export: {e}")
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


# Alternative function for multiple container IDs
def register_multiple_filter_containers():
    """
    Register callbacks for multiple filter containers if you have them
    Call this instead of register_filter_container_callbacks() if you have multiple containers
    """
    
    # Register for analytics container (if it exists)
    try:
        register_filter_container_callbacks("analytics-filter-container")
        logger.info("Registered callbacks for analytics-filter-container")
    except Exception as e:
        logger.warning(f"Could not register analytics-filter-container: {e}")
    
    # Register for main container (if it exists)  
    try:
        register_filter_container_callbacks("main-filter-container")
        logger.info("Registered callbacks for main-filter-container")
    except Exception as e:
        logger.warning(f"Could not register main-filter-container: {e}")
    
    # Register for dashboard container (if it exists)
    try:
        register_filter_container_callbacks("dashboard-filter-container")
        logger.info("Registered callbacks for dashboard-filter-container")
    except Exception as e:
        logger.warning(f"Could not register dashboard-filter-container: {e}")


# CSV File Loading with Browser API (Alternative Implementation)
def setup_csv_file_loading():
    """
    Setup for loading CSV file using browser file API
    Add this to your main.py or wherever you initialize your app
    """
    
    # Add clientside callback to load CSV data from browser
    from dash import clientside_callback, ClientsideFunction, Input, Output
    
    clientside_callback(
        """
        function(trigger) {
            // Try to load CSV file using window.fs.readFile
            if (window.fs && window.fs.readFile) {
                try {
                    window.fs.readFile('data/waste_management_data_updated.csv', { encoding: 'utf8' })
                        .then(function(csvContent) {
                            console.log('Successfully loaded CSV file');
                            // You could store this in a global variable or process it
                            window.wasteManagementData = csvContent;
                        })
                        .catch(function(error) {
                            console.error('Error loading CSV file:', error);
                        });
                } catch (e) {
                    console.error('Error accessing file system:', e);
                }
            } else {
                console.warn('File system API not available');
            }
            return '';
        }
        """,
        Output('csv-loading-status', 'children'),
        Input('app-loading-trigger', 'id')
    )


# Integration Instructions for your main.py
INTEGRATION_CODE = '''
# Add this to your main.py imports:
from callbacks.filter_container_callbacks import register_filter_container_callbacks, register_multiple_filter_containers
from data_loader import refresh_cached_data

# Add this after your app initialization:
# Register filter container callbacks with real data
register_filter_container_callbacks("analytics-filter-container")  # For analytics tab
# OR use register_multiple_filter_containers() if you have multiple containers

# Add this hidden div to your layout for status updates:
html.Div(id='dashboard-export-status', children=[], style={'display': 'none'})
'''

print("Integration code for main.py:")
print(INTEGRATION_CODE)