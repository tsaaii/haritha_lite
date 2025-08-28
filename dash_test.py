"""
Dash Bootstrap Components 4×3 Grid Layout with Uniform Card Styling
Replicates the exact styling from public_layout_uniform.css
"""

import dash_bootstrap_components as dbc
from dash import html, dcc
import datetime

def create_uniform_card(icon, title, value=None, unit=None, dual_metrics=None, card_id=None):
    """
    Create a uniform metric card with exact styling from public_layout_uniform.css
    
    Args:
        icon: Font awesome icon class (e.g., "fas fa-chart-line")
        title: Card title text
        value: Single metric value (optional if using dual_metrics)
        unit: Single metric unit (optional if using dual_metrics)
        dual_metrics: Dict with 'left' and 'right' containing {'value': str, 'unit': str}
        card_id: Unique identifier for the card
    """
    
    # Single metric layout
    if value is not None and dual_metrics is None:
        content = [
            html.I(className=f"{icon} metric-icon"),
            html.H3(title, className="metric-title"),
            html.Div([
                html.Span(str(value), className="metric-value"),
                html.Span(unit or "", className="metric-unit")
            ])
        ]
    
    # Dual metrics layout
    elif dual_metrics is not None:
        content = [
            html.I(className=f"{icon} metric-icon"),
            html.H3(title, className="metric-title"),
            html.Div([
                html.Div([
                    html.Span(dual_metrics['left']['value'], className="metric-value"),
                    html.Span(dual_metrics['left']['unit'], className="metric-unit")
                ], className="metric-group"),
                html.Div([
                    html.Span(dual_metrics['right']['value'], className="metric-value"),
                    html.Span(dual_metrics['right']['unit'], className="metric-unit")
                ], className="metric-group")
            ], className="dual-metrics-container")
        ]
    
    # Placeholder layout
    else:
        content = [
            html.I(className=f"{icon} metric-icon"),
            html.H3(title, className="metric-title"),
            html.Div("Coming Soon", className="placeholder-text")
        ]
    
    return dbc.Card(
        content,
        className="metric-card",
        id=card_id,
        style={
            "cursor": "pointer",
            "height": "100%"
        }
    )

def create_4x3_grid_layout(theme_name="dark"):
    """
    Create a 4×3 grid layout using Dash Bootstrap Components
    with exact styling from public_layout_uniform.css
    """
    
    # Theme CSS variables (replicate from your theme system)
    theme_styles = {
        "dark": {
            "--primary-bg": "#0f172a",
            "--secondary-bg": "#1e293b", 
            "--accent-bg": "#334155",
            "--card-bg": "#475569",
            "--text-primary": "#f8fafc",
            "--text-secondary": "#cbd5e1",
            "--brand-primary": "#3b82f6",
            "--border-light": "#64748b",
            "--success": "#10b981",
            "--warning": "#f59e0b", 
            "--error": "#ef4444",
            "--info": "#06b6d4"
        },
        "light": {
            "--primary-bg": "#ffffff",
            "--secondary-bg": "#f8fafc",
            "--accent-bg": "#e2e8f0", 
            "--card-bg": "#f1f5f9",
            "--text-primary": "#1e293b",
            "--text-secondary": "#64748b",
            "--brand-primary": "#3b82f6",
            "--border-light": "#cbd5e1",
            "--success": "#10b981",
            "--warning": "#f59e0b",
            "--error": "#ef4444", 
            "--info": "#06b6d4"
        }
    }
    
    # Sample cards data - replace with your actual data
    cards_data = [
        {
            "icon": "fas fa-chart-line",
            "title": "Total Progress",
            "dual_metrics": {
                "left": {"value": "85%", "unit": "Complete"},
                "right": {"value": "15%", "unit": "Remaining"}
            },
            "card_id": "total-progress-card"
        },
        {
            "icon": "fas fa-clock",
            "title": "Timeline Status", 
            "dual_metrics": {
                "left": {"value": "30", "unit": "Days Left"},
                "right": {"value": "75%", "unit": "On Track"}
            },
            "card_id": "timeline-card"
        },
        {
            "icon": "fas fa-users",
            "title": "Team Performance",
            "dual_metrics": {
                "left": {"value": "24", "unit": "Active"},
                "right": {"value": "92%", "unit": "Efficiency"}
            },
            "card_id": "team-card"
        },
        {
            "icon": "fas fa-target",
            "title": "Goals Achieved",
            "value": "127",
            "unit": "Completed",
            "card_id": "goals-card"
        },
        {
            "icon": "fas fa-dollar-sign", 
            "title": "Budget Status",
            "dual_metrics": {
                "left": {"value": "$45K", "unit": "Used"},
                "right": {"value": "$15K", "unit": "Remaining"}
            },
            "card_id": "budget-card"
        },
        {
            "icon": "fas fa-exclamation-triangle",
            "title": "Issues Resolved",
            "value": "98%",
            "unit": "Success Rate",
            "card_id": "issues-card"
        },
        {
            "icon": "fas fa-chart-bar",
            "title": "Performance Score",
            "value": "9.2",
            "unit": "Rating",
            "card_id": "performance-card"
        },
        {
            "icon": "fas fa-calendar-check",
            "title": "Milestones",
            "dual_metrics": {
                "left": {"value": "8", "unit": "Complete"},
                "right": {"value": "2", "unit": "Pending"}
            },
            "card_id": "milestones-card"
        },
        # Placeholder cards for remaining slots
        {
            "icon": "fas fa-plus",
            "title": "New Metric",
            "card_id": "placeholder-1"
        },
        {
            "icon": "fas fa-cog",
            "title": "Configuration", 
            "card_id": "placeholder-2"
        },
        {
            "icon": "fas fa-bell",
            "title": "Notifications",
            "card_id": "placeholder-3"
        },
        {
            "icon": "fas fa-info-circle",
            "title": "Information",
            "card_id": "placeholder-4"
        }
    ]
    
    # Create hero section
    hero_section = html.Div(
        className="hero-section",
        children=[
            html.Div(
                className="hero-content",
                children=[
                    # Left Logo
                    html.Div([
                        html.Img(
                            src="/assets/img/left.png",
                            alt="Left Organization Logo",
                            className="responsive-logo"
                        )
                    ]),
                    
                    # Title Section
                    html.Div([
                        html.H1(
                            "Swaccha Andhra Corporation",
                            className="hero-title"
                        ),
                        html.P(
                            "Real Time Legacy Waste Remediation Progress Tracker",
                            className="hero-subtitle"
                        )
                    ], className="hero-title-section"),
                    
                    # Right Logo
                    html.Div([
                        html.Img(
                            src="/assets/img/right.png", 
                            alt="Right Organization Logo",
                            className="responsive-logo"
                        )
                    ])
                ]
            )
        ]
    )
    
    # Create 4×3 cards grid using Bootstrap
    cards_grid = dbc.Container([
        dbc.Row([
            dbc.Col(
                create_uniform_card(**card_data),
                xs=6, sm=6, md=3, lg=3, xl=3,
                className="mb-4"
            ) for card_data in cards_data[:4]  # First row - 4 cards
        ], className="g-3"),
        dbc.Row([
            dbc.Col(
                create_uniform_card(**card_data),
                xs=6, sm=6, md=3, lg=3, xl=3,
                className="mb-4"
            ) for card_data in cards_data[4:8]  # Second row - 4 cards
        ], className="g-3"),
        dbc.Row([
            dbc.Col(
                create_uniform_card(**card_data),
                xs=6, sm=6, md=3, lg=3, xl=3,
                className="mb-4"
            ) for card_data in cards_data[8:12]  # Third row - 4 cards
        ], className="g-3")
    ], fluid=True, className="cards-grid h-100")
    
    # Main layout with exact CSS structure
    layout = html.Div(
        className="public-layout",
        style=theme_styles.get(theme_name, theme_styles["dark"]),
        children=[
            # Load the uniform CSS
            html.Link(
                rel="stylesheet",
                href="/assets/css/public_layout_uniform.css"
            ),
            html.Link(
                rel="stylesheet", 
                href="/assets/css/uniform_cards.css"
            ),
            # FontAwesome for icons
            html.Link(
                rel="stylesheet",
                href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"
            ),
            
            # Main content
            html.Div([
                hero_section,
                cards_grid
            ], className="main-content")
        ]
    )
    
    return layout

def create_bootstrap_app():
    """
    Create a complete Dash app with Bootstrap components and uniform styling
    """
    import dash
    
    # Initialize Dash app with Bootstrap
    app = dash.Dash(
        __name__,
        external_stylesheets=[
            dbc.themes.BOOTSTRAP,
            "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"
        ],
        suppress_callback_exceptions=True
    )
    
    # Set the layout
    app.layout = create_4x3_grid_layout("dark")
    
    return app

# Example usage and callbacks
def register_card_callbacks(app):
    """
    Register callbacks for card interactions
    """
    from dash import callback, Input, Output, State
    
    # Example callback for card clicks
    @app.callback(
        Output('card-click-output', 'children'),
        [Input(f'{card_id}', 'n_clicks') for card_id in [
            'total-progress-card', 'timeline-card', 'team-card', 'goals-card',
            'budget-card', 'issues-card', 'performance-card', 'milestones-card'
        ]],
        prevent_initial_call=True
    )
    def handle_card_clicks(*args):
        """Handle card click events"""
        ctx = dash.callback_context
        
        if not ctx.triggered:
            return "No card clicked yet"
            
        card_id = ctx.triggered[0]['prop_id'].split('.')[0]
        return f"Card clicked: {card_id}"

# CSS Injection for exact styling replication
CUSTOM_CSS = """
/* Replicate exact styles from public_layout_uniform.css */

.public-layout {
    min-height: 100vh;
    max-height: 100vh;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    background: var(--primary-bg);
    color: var(--text-primary);
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    width: 100vw;
    margin: 0;
    padding: 0;
}

.main-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    padding: 0;
    gap: clamp(0.25rem, 1vh, 0.5rem);
    overflow: hidden;
    width: 100%;
    margin: 0;
}

.cards-grid {
    flex: 1;
    display: grid !important;
    grid-template-columns: repeat(4, 1fr) !important;
    grid-template-rows: repeat(3, 1fr) !important;
    row-gap: clamp(0.75rem, 1.5vh, 1.25rem) !important;
    column-gap: clamp(1rem, 2vh, 1.5rem) !important;
    padding: clamp(0.75rem, 2vh, 1.5rem) !important;
    overflow: hidden !important;
    width: 100% !important;
    height: 100% !important;
    position: relative;
    z-index: 1;
}

.cards-grid .row {
    display: contents !important;
}

.cards-grid .col {
    display: flex !important;
    align-items: stretch !important;
}

/* Override Bootstrap grid behavior for uniform cards */
.cards-grid .col-xs-6,
.cards-grid .col-sm-6, 
.cards-grid .col-md-3,
.cards-grid .col-lg-3,
.cards-grid .col-xl-3 {
    flex: none !important;
    max-width: none !important;
    padding: 0 !important;
    margin: 0 !important;
}

/* Uniform card styling - exact replication */
.metric-card {
    background: linear-gradient(135deg, var(--accent-bg) 0%, var(--card-bg) 100%) !important;
    border-radius: clamp(8px, 1.5vh, 12px) !important;
    border: 2px solid rgba(255, 255, 255, 0.1) !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
    padding: clamp(1rem, 2.5vh, 1.8rem) !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: flex-start !important;
    text-align: center !important;
    transition: all 0.2s ease !important;
    cursor: pointer !important;
    position: relative !important;
    overflow: hidden !important;
    aspect-ratio: 4 / 3 !important;
    min-height: 160px !important;
    width: 100% !important;
    box-sizing: border-box !important;
}

.metric-card:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2) !important;
    border-color: var(--brand-primary) !important;
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .cards-grid {
        grid-template-columns: repeat(2, 1fr) !important;
        grid-template-rows: repeat(6, 1fr) !important;
    }
}

@media (max-width: 480px) {
    .cards-grid {
        grid-template-columns: 1fr !important;
        grid-template-rows: repeat(12, 1fr) !important;
    }
}
"""

if __name__ == "__main__":
    # Example of how to run the app
    app = create_bootstrap_app()
    
    # Add custom CSS
    app.index_string = f'''
    <!DOCTYPE html>
    <html>
        <head>
            {{%metas%}}
            <title>{{%title%}}</title>
            {{%favicon%}}
            {{%css%}}
            <style>
                {CUSTOM_CSS}
            </style>
        </head>
        <body>
            {{%app_entry%}}
            <footer>
                {{%config%}}
                {{%scripts%}}
                {{%renderer%}}
            </footer>
        </body>
    </html>
    '''
    
    register_card_callbacks(app)
    app.run_server(debug=True)