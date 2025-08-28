# callbacks/public_landing_callbacks.py
"""
Enhanced Callbacks for Public Landing Page Auto-Rotation
Handles 15-second auto-rotation through agencies, clusters, and sites with full debugging
"""

from dash import callback, Input, Output, html, clientside_callback
import logging
from layouts.public_layout import (
    load_csv_visualization_data,
    get_rotation_data,
    get_enhanced_metric_cards_for_rotation,
    create_enhanced_metric_cards_grid
)
from utils.theme_utils import get_theme_styles

logger = logging.getLogger(__name__)

def register_public_landing_callbacks():
    """
    Register all public landing page callbacks
    Call this function during app initialization
    """
    
    @callback(
        Output('dynamic-cards-container', 'children'),
        [Input('auto-rotation-interval', 'n_intervals'),
         Input('current-theme', 'data')],
        prevent_initial_call=False
    )
    def update_enhanced_rotating_cards(n_intervals, theme_name):
        """
        Update metric cards with enhanced metrics and animations
        Cycles through all sites with their agency and cluster information
        """
        try:
            logger.info(f"🔄 Enhanced auto-rotation update #{n_intervals}")
            
            # Load CSV data
            df = load_csv_visualization_data()
            
            if df.empty:
                logger.warning("No CSV data available for rotation")
                theme_styles = get_theme_styles(theme_name or 'dark')
                return [
                    html.Div(
                        className="metric-card",
                        children=[
                            html.Div("❌", className="metric-icon"),
                            html.Div("No Data", className="metric-title"),
                            html.Div("Please check CSV file", className="metric-value"),
                            html.Div("data/csv_outputs_data_viz.csv", className="metric-unit"),
                            html.Div("CSV file not found or empty", className="debug-info")
                        ],
                        style={
                            "background": "rgba(220, 53, 69, 0.1)",
                            "border": "2px solid #dc3545",
                            "borderRadius": "8px",
                            "padding": "1rem",
                            "textAlign": "center"
                        }
                    ) for _ in range(8)
                ]
            
            # Get current rotation data based on interval count
            rotation_data = get_rotation_data(df, n_intervals)
            
            logger.info(f"📊 Current focus: {rotation_data.get('current_focus', 'Unknown')}")
            logger.info(f"🏢 Agency: {rotation_data.get('current_agency', 'Unknown')}")
            logger.info(f"🗺️ Cluster: {rotation_data.get('current_cluster', 'Unknown')}")
            logger.info(f"📍 Site: {rotation_data.get('current_site', 'Unknown')}")
            
            # Debug CSV data structure
            if not df.empty:
                logger.info(f"📋 CSV Columns: {list(df.columns)}")
                logger.info(f"📊 CSV Shape: {df.shape}")
                if 'net_weight_calculated' in df.columns:
                    weight_sample = df['net_weight_calculated'].head().tolist()
                    logger.info(f"⚖️ Weight Sample: {weight_sample}")
                else:
                    logger.warning("⚖️ No 'net_weight_calculated' column found in CSV")
            
            # Get theme styles
            theme_styles = get_theme_styles(theme_name or 'dark')
            
            # Get enhanced metric cards for current rotation
            metrics_data = get_enhanced_metric_cards_for_rotation(df, rotation_data, theme_styles)
            
            # Log debug info from Card 2 specifically
            if len(metrics_data) > 1:
                card2_debug = metrics_data[1].get('debug_text', 'No debug info')
                logger.info(f"🐛 Card 2 Debug: {card2_debug}")
            
            # Create enhanced cards grid
            cards_grid = create_enhanced_metric_cards_grid(metrics_data, theme_styles)
            
            # Return the children of the cards grid
            return cards_grid.children
            
        except Exception as e:
            logger.error(f"❌ Error updating enhanced rotating cards: {e}")
            import traceback
            traceback.print_exc()
            
            # Return fallback cards on error
            try:
                theme_styles = get_theme_styles(theme_name or 'dark')
                return [
                    html.Div(
                        className="metric-card",
                        children=[
                            html.Div("⚠️", className="metric-icon"),
                            html.Div("Error Loading", className="metric-title"),
                            html.Div(f"Card {i+1}", className="metric-value"),
                            html.Div("Please refresh", className="metric-unit"),
                            html.Div(f"Error: {str(e)[:100]}...", className="debug-info", 
                                    style={
                                        'fontSize': '0.7rem',
                                        'color': '#dc3545',
                                        'marginTop': '0.5rem',
                                        'padding': '0.25rem',
                                        'backgroundColor': 'rgba(220, 53, 69, 0.1)',
                                        'borderRadius': '4px',
                                        'wordBreak': 'break-word'
                                    }) if i == 1 else None
                        ],
                        style={
                            "background": "rgba(255, 193, 7, 0.1)",
                            "border": "2px solid #ffc107",
                            "borderRadius": "8px",
                            "padding": "1rem",
                            "textAlign": "center"
                        }
                    ) for i in range(8)
                ]
            except:
                # Ultimate fallback - basic HTML structure
                return [
                    html.Div(
                        className="metric-card",
                        children=[
                            html.Div("❌", className="metric-icon"),
                            html.Div("System Error", className="metric-title"),
                            html.Div("Critical Failure", className="metric-value"),
                            html.Div("Please refresh page", className="metric-unit")
                        ],
                        style={
                            "background": "rgba(220, 53, 69, 0.1)",
                            "border": "2px solid #dc3545",
                            "borderRadius": "8px",
                            "padding": "1rem",
                            "textAlign": "center"
                        }
                    ) for _ in range(8)
                ]

    # Clientside callback for smooth counter animations with Indian formatting
    clientside_callback(
        """
        function(children) {
            // Enhanced counter animation function with Indian number formatting
            function animateCounters() {
                const counters = document.querySelectorAll('.animated-number');
                counters.forEach(counter => {
                    const target = parseInt(counter.getAttribute('data-target') || counter.textContent.replace(/,/g, ''));
                    if (isNaN(target) || target === 0) {
                        counter.textContent = '0';
                        return;
                    }
                    
                    // Dynamic duration based on number size
                    const duration = Math.min(2500, Math.max(1000, Math.log10(target + 1) * 800));
                    const increment = target / (duration / 16); // 60fps
                    let current = 0;
                    
                    // Add loading class for visual feedback
                    counter.classList.add('loading-number');
                    
                    const timer = setInterval(() => {
                        current += increment;
                        if (current >= target) {
                            // Final value with Indian formatting
                            counter.textContent = formatIndianNumber(target);
                            counter.classList.remove('loading-number');
                            clearInterval(timer);
                        } else {
                            // Intermediate value with Indian formatting
                            counter.textContent = formatIndianNumber(Math.floor(current));
                        }
                    }, 16);
                });
            }
            
            // Indian number formatting function
            function formatIndianNumber(num) {
                if (num === 0) return "0";
                
                const numStr = num.toString();
                if (numStr.length <= 3) return numStr;
                
                // Indian formatting: last 3 digits, then groups of 2
                let result = numStr.slice(-3);
                let remaining = numStr.slice(0, -3);
                
                while (remaining.length > 0) {
                    if (remaining.length >= 2) {
                        result = remaining.slice(-2) + ',' + result;
                        remaining = remaining.slice(0, -2);
                    } else {
                        result = remaining + ',' + result;
                        remaining = '';
                    }
                }
                
                return result;
            }
            
            // Trigger animations after DOM is updated
            if (children && children.length > 0) {
                setTimeout(animateCounters, 300);
            }
            
            return window.dash_clientside.no_update;
        }
        """,
        Output('animation-trigger', 'data'),
        [Input('dynamic-cards-container', 'children')],
        prevent_initial_call=True
    )
    
    # Optional: Debug info callback for development
    @callback(
        Output('debug-info-display', 'children'),
        [Input('auto-rotation-interval', 'n_intervals')],
        prevent_initial_call=True
    )
    def update_debug_info(n_intervals):
        """
        Optional: Display rotation and debug information
        Add this component to your layout if you want to see debug info
        """
        try:
            df = load_csv_visualization_data()
            rotation_data = get_rotation_data(df, n_intervals)
            
            if df.empty:
                debug_status = "❌ No CSV data loaded"
            else:
                debug_status = f"✅ CSV: {len(df)} records, Current: {rotation_data.get('current_focus', 'Unknown')}"
            
            return html.Div([
                html.Span(f"Rotation #{n_intervals}: ", style={'fontWeight': 'bold', 'color': '#3182CE'}),
                html.Span(debug_status, style={'color': '#38A169'}),
                html.Span(f" | Next in 15s", style={'opacity': 0.7, 'marginLeft': '1rem'})
            ], style={
                'position': 'fixed',
                'top': '10px',
                'right': '10px',
                'background': 'rgba(0,0,0,0.9)',
                'color': 'white',
                'padding': '0.5rem 1rem',
                'borderRadius': '6px',
                'fontSize': '0.8rem',
                'zIndex': 1000,
                'border': '1px solid rgba(255,255,255,0.2)',
                'display': 'none'  # Hide by default, set to 'block' for debugging
            })
            
        except Exception as e:
            logger.error(f"Error updating debug info: {e}")
            return html.Div(
                f"Debug Error: {str(e)[:50]}...",
                style={
                    'position': 'fixed',
                    'top': '10px',
                    'right': '10px',
                    'background': 'rgba(220, 53, 69, 0.9)',
                    'color': 'white',
                    'padding': '0.5rem 1rem',
                    'borderRadius': '6px',
                    'fontSize': '0.8rem',
                    'zIndex': 1000
                }
            )
    
    logger.info("✅ Enhanced public landing page callbacks registered")
    logger.info("🔄 Auto-rotation enabled: 15-second intervals")
    logger.info("📊 Enhanced features: Agency/Cluster/Site rotation with debugging")
    logger.info("🎭 Animations enabled: Indian number formatting and icon effects")
    logger.info("📈 Histogram: Full-card 3-hour window visualization")

# Export callback registration function
__all__ = ['register_public_landing_callbacks']