# callbacks/reports_callbacks.py
"""
Reports Page Callbacks
Handles filter interactions and report generation
"""

from dash import callback, Input, Output, State, html, ctx
from dash.exceptions import PreventUpdate
from datetime import datetime, timedelta
from config.themes import THEMES, DEFAULT_THEME

def register_reports_callbacks(app):
    """Register all reports-related callbacks"""
    
    @app.callback(
        [Output('start-date-picker', 'date'),
         Output('end-date-picker', 'date')],
        [Input('date-7days-btn', 'n_clicks'),
         Input('date-30days-btn', 'n_clicks'),
         Input('date-90days-btn', 'n_clicks'),
         Input('date-year-btn', 'n_clicks')],
        prevent_initial_call=True
    )
    def handle_quick_date_selection(days_7, days_30, days_90, year):
        """Handle quick date range button clicks"""
        if not ctx.triggered:
            raise PreventUpdate
        
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        end_date = datetime.now().date()
        
        if button_id == 'date-7days-btn':
            start_date = end_date - timedelta(days=7)
        elif button_id == 'date-30days-btn':
            start_date = end_date - timedelta(days=30)
        elif button_id == 'date-90days-btn':
            start_date = end_date - timedelta(days=90)
        elif button_id == 'date-year-btn':
            start_date = datetime(end_date.year, 1, 1).date()
        else:
            raise PreventUpdate
        
        return start_date, end_date
    
    @app.callback(
        Output('cluster-filter', 'options'),
        [Input('agency-filter', 'value')]
    )
    def update_cluster_options(selected_agency):
        """Update cluster options based on selected agency"""
        if not selected_agency or selected_agency == 'all':
            return [
                {'label': 'All Clusters', 'value': 'all'},
                {'label': 'Coastal Cluster', 'value': 'coastal'},
                {'label': 'Central Cluster', 'value': 'central'},
                {'label': 'Northern Cluster', 'value': 'northern'},
                {'label': 'Southern Cluster', 'value': 'southern'},
                {'label': 'Eastern Cluster', 'value': 'eastern'},
                {'label': 'Western Cluster', 'value': 'western'}
            ]
        
        # Agency-specific clusters (example logic)
        agency_clusters = {
            'swaccha_ap': [
                {'label': 'All Clusters', 'value': 'all'},
                {'label': 'Central Cluster', 'value': 'central'},
                {'label': 'Coastal Cluster', 'value': 'coastal'},
                {'label': 'Northern Cluster', 'value': 'northern'}
            ],
            'municipal_corp': [
                {'label': 'All Clusters', 'value': 'all'},
                {'label': 'Urban Central', 'value': 'urban_central'},
                {'label': 'Metropolitan', 'value': 'metropolitan'}
            ],
            'district_collector': [
                {'label': 'All Clusters', 'value': 'all'},
                {'label': 'Administrative Zone A', 'value': 'admin_a'},
                {'label': 'Administrative Zone B', 'value': 'admin_b'}
            ]
        }
        
        return agency_clusters.get(selected_agency, [{'label': 'All Clusters', 'value': 'all'}])
    
    @app.callback(
        Output('site-filter', 'options'),
        [Input('agency-filter', 'value'),
         Input('cluster-filter', 'value')]
    )
    def update_site_options(selected_agency, selected_cluster):
        """Update site options based on selected agency and cluster"""
        base_sites = [
            {'label': 'All Sites', 'value': 'all'},
            {'label': 'Visakhapatnam Central', 'value': 'vsk_central'},
            {'label': 'Vijayawada Junction', 'value': 'vjw_junction'},
            {'label': 'Guntur Main', 'value': 'gnt_main'},
            {'label': 'Tirupati Temple', 'value': 'ttp_temple'},
            {'label': 'Kurnool District', 'value': 'knl_district'},
            {'label': 'Anantapur Rural', 'value': 'atp_rural'},
            {'label': 'Nellore Coastal', 'value': 'nlr_coastal'},
            {'label': 'Kadapa Mining', 'value': 'kdp_mining'},
            {'label': 'Chittoor Border', 'value': 'ctr_border'}
        ]
        
        # Filter sites based on cluster selection
        if selected_cluster == 'coastal':
            return [
                {'label': 'All Coastal Sites', 'value': 'all'},
                {'label': 'Visakhapatnam Central', 'value': 'vsk_central'},
                {'label': 'Nellore Coastal', 'value': 'nlr_coastal'}
            ]
        elif selected_cluster == 'central':
            return [
                {'label': 'All Central Sites', 'value': 'all'},
                {'label': 'Vijayawada Junction', 'value': 'vjw_junction'},
                {'label': 'Guntur Main', 'value': 'gnt_main'}
            ]
        
        return base_sites
    
    @app.callback(
        Output('filter-status', 'children'),
        [Input('agency-filter', 'value'),
         Input('cluster-filter', 'value'),
         Input('site-filter', 'value'),
         Input('start-date-picker', 'date'),
         Input('end-date-picker', 'date')]
    )
    def update_filter_status(agency, cluster, site, start_date, end_date):
        """Update filter status display"""
        active_filters = []
        
        if agency and agency != 'all':
            active_filters.append(f"Agency: {agency}")
        
        if cluster and cluster != 'all':
            active_filters.append(f"Cluster: {cluster}")
        
        if site and site != 'all':
            active_filters.append(f"Site: {site}")
        
        if start_date and end_date:
            active_filters.append(f"Date: {start_date} to {end_date}")
        
        if not active_filters:
            return "No filters applied"
        
        return f"Active filters: {', '.join(active_filters)}"
    
    @app.callback(
        [Output('agency-filter', 'value'),
         Output('cluster-filter', 'value'),
         Output('site-filter', 'value')],
        [Input('reset-filters-btn', 'n_clicks')],
        prevent_initial_call=True
    )
    def reset_filters(reset_clicks):
        """Reset all filters to default values"""
        if not reset_clicks:
            raise PreventUpdate
        
        return None, None, None
    
    @app.callback(
        Output('apply-filters-btn', 'style'),
        [Input('agency-filter', 'value'),
         Input('cluster-filter', 'value'),
         Input('site-filter', 'value'),
         Input('start-date-picker', 'date'),
         Input('end-date-picker', 'date')],
        [State('current-theme', 'data')]
    )
    def update_apply_button_style(agency, cluster, site, start_date, end_date, theme_name):
        """Update apply button style based on filter state"""
        theme = THEMES.get(theme_name, THEMES[DEFAULT_THEME])
        
        # Check if any filters are applied
        has_filters = any([
            agency and agency != 'all',
            cluster and cluster != 'all',
            site and site != 'all',
            start_date,
            end_date
        ])
        
        base_style = {
            'background': theme['brand_primary'] if has_filters else theme['border_medium'],
            'color': 'white' if has_filters else theme['text_secondary'],
            'border': 'none',
            'padding': '0.5rem 1.5rem',
            'borderRadius': '6px',
            'fontSize': '0.9rem',
            'fontWeight': '600',
            'cursor': 'pointer' if has_filters else 'not-allowed',
            'transition': 'all 0.2s ease',
            'boxShadow': '0 2px 6px rgba(0, 0, 0, 0.2)' if has_filters else 'none',
            'opacity': 1 if has_filters else 0.6
        }
        
        return base_style
    
    @app.callback(
        Output('generate-report-btn', 'children'),
        [Input('apply-filters-btn', 'n_clicks')],
        [State('agency-filter', 'value'),
         State('cluster-filter', 'value'),
         State('site-filter', 'value'),
         State('start-date-picker', 'date'),
         State('end-date-picker', 'date')],
        prevent_initial_call=True
    )
    def handle_apply_filters(apply_clicks, agency, cluster, site, start_date, end_date):
        """Handle apply filters button click"""
        if not apply_clicks:
            raise PreventUpdate
        
        # Simulate report generation
        filter_count = len([f for f in [agency, cluster, site, start_date, end_date] if f and f != 'all'])
        
        if filter_count > 0:
            return f"📊 Generate Report ({filter_count} filters)"
        else:
            return "📊 Generate Report"
    
    @app.callback(
        Output('export-data-btn', 'style'),
        [Input('apply-filters-btn', 'n_clicks')],
        [State('current-theme', 'data')],
        prevent_initial_call=True
    )
    def update_export_button_after_filter(apply_clicks, theme_name):
        """Update export button style after filters are applied"""
        if not apply_clicks:
            raise PreventUpdate
        
        theme = THEMES.get(theme_name, THEMES[DEFAULT_THEME])
        
        return {
            'background': theme['success'],
            'color': 'white',
            'border': 'none',
            'padding': '0.75rem 1.5rem',
            'borderRadius': '8px',
            'fontSize': '1rem',
            'fontWeight': '600',
            'cursor': 'pointer',
            'transition': 'all 0.2s ease',
            'boxShadow': '0 2px 8px rgba(0, 0, 0, 0.2)'
        }

    @app.callback(
        Output('filter-status', 'style'),
        [Input('apply-filters-btn', 'n_clicks')],
        [State('current-theme', 'data')],
        prevent_initial_call=True
    )
    def update_filter_status_style(apply_clicks, theme_name):
        """Update filter status style when filters are applied"""
        if not apply_clicks:
            raise PreventUpdate
        
        theme = THEMES.get(theme_name, THEMES[DEFAULT_THEME])
        
        return {
            'color': theme['success'],
            'fontSize': '0.9rem',
            'fontWeight': '600',
            'background': f"{theme['success']}15",
            'padding': '0.5rem 1rem',
            'borderRadius': '6px',
            'border': f"1px solid {theme['success']}50"
        }