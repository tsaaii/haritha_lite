# callbacks/filterable_callbacks.py
"""
Callbacks for Filterable Container Component
Handles real-time filtering, data updates, and chart generation
"""

from dash import callback, Input, Output, State, dash_table, html, ctx
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Import the filterable container functions
from components.data.filterable_container import (
    load_sample_waste_data,
    create_data_table,
    create_summary_charts,
    create_status_pie_chart,
    create_daily_trend_chart,
    create_location_bar_chart,
    create_priority_chart
)

@callback(
    [Output('filtered-data-table-container', 'children'),
     Output('filtered-data-charts', 'children'),
     Output('filtered-data-summary', 'children'),
     Output('filter-summary', 'children')],
    [Input('text-search-filter', 'value'),
     Input('date-range-filter', 'start_date'),
     Input('date-range-filter', 'end_date'),
     Input('location-filter', 'value'),
     Input('cluster-filter', 'value'),
     Input('status-filter', 'value'),
     Input('priority-filter', 'value'),
     Input('weight-range-filter', 'value'),
     Input('efficiency-range-filter', 'value'),
     Input('clear-all-filters-btn', 'n_clicks')],
    [State('current-theme', 'data')],
    prevent_initial_call=False
)
def update_filtered_data(text_search, start_date, end_date, locations, clusters, 
                        statuses, priorities, weight_range, efficiency_range, 
                        clear_clicks, theme_name):
    """
    Main callback to filter data and update all components
    """
    # Get theme
    from utils.theme_utils import get_theme_styles
    theme_styles = get_theme_styles(theme_name or 'dark')
    theme = theme_styles["theme"]
    
    try:
        # Load base data
        df = load_sample_waste_data()
        
        # Check if clear filters was clicked
        if ctx.triggered and ctx.triggered[0]['prop_id'] == 'clear-all-filters-btn.n_clicks':
            if clear_clicks and clear_clicks > 0:
                # Return unfiltered data with clear filter message
                filter_summary = create_filter_summary_display(
                    len(df), len(df), "All filters cleared", theme
                )
                return (
                    create_data_table(df, theme),
                    create_summary_charts(df, theme),
                    create_data_summary_stats(df, theme),
                    filter_summary
                )
        
        # Apply filters
        filtered_df = apply_all_filters(
            df, text_search, start_date, end_date, locations, clusters,
            statuses, priorities, weight_range, efficiency_range
        )
        
        # Create filter summary
        active_filters = count_active_filters(
            text_search, start_date, end_date, locations, clusters,
            statuses, priorities, weight_range, efficiency_range, df
        )
        
        filter_summary = create_filter_summary_display(
            len(df), len(filtered_df), active_filters, theme
        )
        
        # Update components
        updated_table = create_data_table(filtered_df, theme)
        updated_charts = create_summary_charts(filtered_df, theme)
        updated_summary = create_data_summary_stats(filtered_df, theme)
        
        logger.info(f"Filtered data: {len(df)} -> {len(filtered_df)} records")
        
        return updated_table, updated_charts, updated_summary, filter_summary
        
    except Exception as e:
        logger.error(f"Error in filtering callback: {e}")
        # Return error state
        error_component = html.Div(
            f"Error filtering data: {str(e)}",
            style={"color": theme["error"], "padding": "1rem", "textAlign": "center"}
        )
        return error_component, error_component, error_component, error_component

def apply_all_filters(df, text_search, start_date, end_date, locations, clusters,
                     statuses, priorities, weight_range, efficiency_range):
    """Apply all filters to the dataframe"""
    
    filtered_df = df.copy()
    
    # Text search filter
    if text_search and text_search.strip():
        search_cols = ['source_location', 'Vehicle No', 'Operator', 'Supervisor', 'Material Name']
        search_mask = pd.Series([False] * len(filtered_df))
        
        for col in search_cols:
            if col in filtered_df.columns:
                search_mask = search_mask | filtered_df[col].astype(str).str.contains(
                    text_search.strip(), case=False, na=False
                )
        
        filtered_df = filtered_df[search_mask]
    
    # Date range filter
    if start_date and end_date and 'Date' in filtered_df.columns:
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        filtered_df = filtered_df[
            (filtered_df['Date'] >= start_date) & 
            (filtered_df['Date'] <= end_date)
        ]
    
    # Location filter
    if locations and 'source_location' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['source_location'].isin(locations)]
    
    # Cluster filter
    if clusters and 'Cluster' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['Cluster'].isin(clusters)]
    
    # Status filter
    if statuses and 'Status' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['Status'].isin(statuses)]
    
    # Priority filter
    if priorities and 'Priority' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['Priority'].isin(priorities)]
    
    # Weight range filter
    if weight_range and 'Net Weight' in filtered_df.columns:
        min_weight, max_weight = weight_range
        filtered_df = filtered_df[
            (filtered_df['Net Weight'] >= min_weight) & 
            (filtered_df['Net Weight'] <= max_weight)
        ]
    
    # Efficiency range filter
    if efficiency_range and 'Efficiency (%)' in filtered_df.columns:
        min_eff, max_eff = efficiency_range
        filtered_df = filtered_df[
            (filtered_df['Efficiency (%)'] >= min_eff) & 
            (filtered_df['Efficiency (%)'] <= max_eff)
        ]
    
    return filtered_df

def count_active_filters(text_search, start_date, end_date, locations, clusters,
                        statuses, priorities, weight_range, efficiency_range, df):
    """Count and describe active filters"""
    filters = []
    
    if text_search and text_search.strip():
        filters.append(f"Text: '{text_search.strip()}'")
    
    if start_date and end_date:
        filters.append(f"Date: {start_date} to {end_date}")
    
    if locations:
        filters.append(f"Locations: {len(locations)} selected")
    
    if clusters:
        filters.append(f"Clusters: {len(clusters)} selected")
    
    if statuses:
        filters.append(f"Status: {len(statuses)} selected")
    
    if priorities:
        filters.append(f"Priority: {len(priorities)} selected")
    
    if weight_range and 'Net Weight' in df.columns:
        min_w, max_w = weight_range
        df_min, df_max = df['Net Weight'].min(), df['Net Weight'].max()
        if min_w > df_min or max_w < df_max:
            filters.append(f"Weight: {min_w:,.0f} - {max_w:,.0f} kg")
    
    if efficiency_range:
        min_e, max_e = efficiency_range
        if min_e > 0 or max_e < 100:
            filters.append(f"Efficiency: {min_e}% - {max_e}%")
    
    return filters

def create_filter_summary_display(total_records, filtered_records, active_filters, theme):
    """Create filter summary display"""
    
    if isinstance(active_filters, str):
        # Clear filters message
        return html.Div([
            html.Span("🔄 ", style={"fontSize": "1.2rem", "marginRight": "0.5rem"}),
            html.Span(
                active_filters,
                style={
                    "fontSize": "1rem",
                    "fontWeight": "600",
                    "color": theme["success"]
                }
            ),
            html.Span(
                f" • Showing all {total_records:,} records",
                style={
                    "fontSize": "0.9rem",
                    "color": theme["text_secondary"],
                    "marginLeft": "1rem"
                }
            )
        ], style={"display": "flex", "alignItems": "center"})
    
    # Regular filter summary
    filter_count = len(active_filters) if active_filters else 0
    
    return html.Div([
        # Summary stats
        html.Div([
            html.Span("📊 ", style={"fontSize": "1.2rem", "marginRight": "0.5rem"}),
            html.Span(
                f"Showing {filtered_records:,} of {total_records:,} records",
                style={
                    "fontSize": "1rem",
                    "fontWeight": "700",
                    "color": theme["text_primary"]
                }
            ),
            html.Span(
                f" ({(filtered_records/total_records*100):.1f}%)" if total_records > 0 else "",
                style={
                    "fontSize": "0.9rem",
                    "color": theme["brand_primary"],
                    "fontWeight": "600",
                    "marginLeft": "0.5rem"
                }
            )
        ], style={"marginBottom": "0.5rem"}),
        
        # Active filters
        html.Div([
            html.Span("🔍 ", style={"fontSize": "1rem", "marginRight": "0.5rem"}),
            html.Span(
                f"{filter_count} active filter{'s' if filter_count != 1 else ''}" if filter_count > 0 else "No filters applied",
                style={
                    "fontSize": "0.9rem",
                    "fontWeight": "600",
                    "color": theme["warning"] if filter_count > 0 else theme["text_secondary"]
                }
            )
        ]) if filter_count != len(active_filters) or filter_count == 0 else None,
        
        # Filter details
        html.Div([
            html.Div(
                f"• {filter_desc}",
                style={
                    "fontSize": "0.8rem",
                    "color": theme["text_secondary"],
                    "marginLeft": "1.5rem",
                    "marginBottom": "0.2rem"
                }
            ) for filter_desc in (active_filters[:5] if active_filters else [])
        ]) if active_filters and len(active_filters) > 0 else None,
        
        # Show more filters indicator
        html.Div(
            f"... and {len(active_filters) - 5} more",
            style={
                "fontSize": "0.8rem",
                "color": theme["text_muted"] if "text_muted" in theme else theme["text_secondary"],
                "marginLeft": "1.5rem",
                "fontStyle": "italic"
            }
        ) if active_filters and len(active_filters) > 5 else None
    ])

def create_data_summary_stats(df, theme):
    """Create summary statistics cards"""
    if df.empty:
        return html.Div(
            "No data available for summary",
            style={"color": theme["text_secondary"], "textAlign": "center", "padding": "1rem"}
        )
    
    # Calculate summary stats
    total_weight = df['Net Weight'].sum() if 'Net Weight' in df.columns else 0
    avg_weight = df['Net Weight'].mean() if 'Net Weight' in df.columns else 0
    total_records = len(df)
    avg_efficiency = df['Efficiency (%)'].mean() if 'Efficiency (%)' in df.columns else 0
    
    # Status distribution
    status_counts = df['Status'].value_counts().to_dict() if 'Status' in df.columns else {}
    
    # Priority distribution
    priority_counts = df['Priority'].value_counts().to_dict() if 'Priority' in df.columns else {}
    
    return html.Div([
        # Main stats grid
        html.Div(
            style={
                "display": "grid",
                "gridTemplateColumns": "repeat(auto-fit, minmax(200px, 1fr))",
                "gap": "1rem",
                "marginBottom": "1.5rem"
            },
            children=[
                create_stat_card("📊", "Total Records", f"{total_records:,}", "entries", theme),
                create_stat_card("⚖️", "Total Weight", f"{total_weight/1000:.1f}", "tons", theme),
                create_stat_card("📈", "Avg Weight", f"{avg_weight:.0f}", "kg", theme),
                create_stat_card("🎯", "Avg Efficiency", f"{avg_efficiency:.1f}", "%", theme)
            ]
        ),
        
        # Status and Priority breakdown
        html.Div(
            style={
                "display": "grid",
                "gridTemplateColumns": "1fr 1fr",
                "gap": "1rem"
            },
            children=[
                # Status breakdown
                html.Div([
                    html.H4(
                        "🚦 Status Breakdown",
                        style={
                            "color": theme["text_primary"],
                            "fontSize": "1rem",
                            "fontWeight": "600",
                            "marginBottom": "0.5rem"
                        }
                    ),
                    html.Div([
                        html.Div([
                            html.Span(
                                status,
                                style={
                                    "fontSize": "0.85rem",
                                    "color": theme["text_secondary"],
                                    "fontWeight": "500"
                                }
                            ),
                            html.Span(
                                f"{count:,}",
                                style={
                                    "fontSize": "0.85rem",
                                    "color": theme["brand_primary"],
                                    "fontWeight": "700",
                                    "marginLeft": "auto"
                                }
                            )
                        ], style={
                            "display": "flex",
                            "justifyContent": "space-between",
                            "padding": "0.25rem 0"
                        }) for status, count in status_counts.items()
                    ])
                ], style={
                    "backgroundColor": theme["accent_bg"],
                    "padding": "1rem",
                    "borderRadius": "8px",
                    "border": f"1px solid {theme.get('border_light', theme['accent_bg'])}"
                }),
                
                # Priority breakdown
                html.Div([
                    html.H4(
                        "⚡ Priority Breakdown",
                        style={
                            "color": theme["text_primary"],
                            "fontSize": "1rem",
                            "fontWeight": "600",
                            "marginBottom": "0.5rem"
                        }
                    ),
                    html.Div([
                        html.Div([
                            html.Span(
                                priority,
                                style={
                                    "fontSize": "0.85rem",
                                    "color": theme["text_secondary"],
                                    "fontWeight": "500"
                                }
                            ),
                            html.Span(
                                f"{count:,}",
                                style={
                                    "fontSize": "0.85rem",
                                    "color": theme["warning"] if priority == "High" else theme["brand_primary"],
                                    "fontWeight": "700",
                                    "marginLeft": "auto"
                                }
                            )
                        ], style={
                            "display": "flex",
                            "justifyContent": "space-between",
                            "padding": "0.25rem 0"
                        }) for priority, count in priority_counts.items()
                    ])
                ], style={
                    "backgroundColor": theme["accent_bg"],
                    "padding": "1rem",
                    "borderRadius": "8px",
                    "border": f"1px solid {theme.get('border_light', theme['accent_bg'])}"
                })
            ]
        )
    ])

def create_stat_card(icon, title, value, unit, theme):
    """Create a small stat card"""
    return html.Div([
        html.Div(
            icon,
            style={
                "fontSize": "1.5rem",
                "marginBottom": "0.5rem",
                "textAlign": "center"
            }
        ),
        html.Div(
            value,
            style={
                "fontSize": "1.5rem",
                "fontWeight": "800",
                "color": theme["brand_primary"],
                "textAlign": "center",
                "lineHeight": "1"
            }
        ),
        html.Div(
            title,
            style={
                "fontSize": "0.8rem",
                "color": theme["text_secondary"],
                "fontWeight": "600",
                "textAlign": "center",
                "marginTop": "0.25rem"
            }
        ),
        html.Div(
            unit,
            style={
                "fontSize": "0.7rem",
                "color": theme["success"],
                "fontWeight": "500",
                "textAlign": "center"
            }
        )
    ], style={
        "backgroundColor": theme["card_bg"],
        "borderRadius": "8px",
        "border": f"1px solid {theme['accent_bg']}",
        "padding": "1rem",
        "textAlign": "center",
        "boxShadow": "0 2px 8px rgba(0, 0, 0, 0.1)"
    })

@callback(
    [Output('text-search-filter', 'value'),
     Output('date-range-filter', 'start_date'),
     Output('date-range-filter', 'end_date'),
     Output('location-filter', 'value'),
     Output('cluster-filter', 'value'),
     Output('status-filter', 'value'),
     Output('priority-filter', 'value'),
     Output('weight-range-filter', 'value'),
     Output('efficiency-range-filter', 'value')],
    [Input('clear-all-filters-btn', 'n_clicks')],
    prevent_initial_call=True
)
def clear_all_filters(n_clicks):
    """Clear all filter values when clear button is clicked"""
    if n_clicks and n_clicks > 0:
        # Get default weight range from data
        df = load_sample_waste_data()
        max_weight = int(df['Net Weight'].max()) if 'Net Weight' in df.columns and not df.empty else 10000
        
        return (
            "",  # text search
            None,  # start date
            None,  # end date
            [],  # locations
            [],  # clusters
            [],  # statuses
            [],  # priorities
            [0, max_weight],  # weight range
            [0, 100]  # efficiency range
        )
    
    # Return current values (no change)
    return [None] * 9

# Export callback functions
__all__ = [
    'update_filtered_data',
    'clear_all_filters',
    'apply_all_filters',
    'create_data_summary_stats'
]