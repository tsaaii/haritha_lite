# components/cards/stat_card.py
"""
Statistics Card Component
Reusable card for displaying key metrics
"""

from dash import html

def create_stat_card(icon, title, value, unit, theme_styles, size="normal"):
    """
    Create a statistics card component
    
    Args:
        icon (str): Emoji or icon for the card
        title (str): Card title/label
        value (str): Main value to display
        unit (str): Unit or description
        theme_styles (dict): Theme styling dictionary
        size (str): "small", "normal", or "large"
        
    Returns:
        html.Div: Statistics card component
    """
    theme = theme_styles["theme"]
    
    # Size configurations
    size_config = {
        "small": {
            "icon_size": "2rem",
            "value_size": "1.8rem",
            "title_size": "1rem",
            "unit_size": "0.8rem",
            "padding": "1rem"
        },
        "normal": {
            "icon_size": "3rem",
            "value_size": "2.5rem", 
            "title_size": "1.125rem",
            "unit_size": "0.875rem",
            "padding": "1.5rem"
        },
        "large": {
            "icon_size": "4rem",
            "value_size": "3.5rem",
            "title_size": "1.5rem",
            "unit_size": "1rem",
            "padding": "2rem"
        }
    }
    
    config = size_config.get(size, size_config["normal"])
    
    return html.Div(
        className="stat-card",
        style={
            "backgroundColor": theme["card_bg"],
            "borderRadius": "12px",
            "border": f"2px solid {theme['accent_bg']}",
            "boxShadow": "0 4px 20px rgba(0, 0, 0, 0.2)",
            "padding": config["padding"],
            "textAlign": "center",
            "transition": "transform 0.2s ease, box-shadow 0.2s ease",
            "cursor": "default"
        },
        children=[
            html.Div(
                icon,
                style={
                    "fontSize": config["icon_size"],
                    "marginBottom": "0.5rem",
                    "display": "block"
                }
            ),
            html.H2(
                value,
                style={
                    "fontSize": config["value_size"],
                    "fontWeight": "800",
                    "color": theme["brand_primary"],
                    "margin": "0.5rem 0",
                    "lineHeight": "1.2"
                }
            ),
            html.P(
                title,
                style={
                    "fontSize": config["title_size"],
                    "color": theme["text_secondary"],
                    "fontWeight": "600",
                    "margin": "0.5rem 0 0 0"
                }
            ),
            html.P(
                unit,
                style={
                    "fontSize": config["unit_size"],
                    "color": theme["success"],
                    "fontWeight": "500",
                    "margin": "0"
                }
            )
        ]
    )

def create_trend_stat_card(icon, title, value, unit, trend_value, trend_direction, theme_styles):
    """
    Create a statistics card with trend indicator
    
    Args:
        icon (str): Emoji or icon
        title (str): Card title
        value (str): Main value
        unit (str): Unit description
        trend_value (str): Trend percentage/value
        trend_direction (str): "up", "down", or "neutral"
        theme_styles (dict): Theme styling
        
    Returns:
        html.Div: Trend statistics card
    """
    theme = theme_styles["theme"]
    
    # Trend styling
    trend_colors = {
        "up": theme["success"],
        "down": theme["error"],
        "neutral": theme["warning"]
    }
    
    trend_icons = {
        "up": "↗️",
        "down": "↘️", 
        "neutral": "➡️"
    }
    
    trend_color = trend_colors.get(trend_direction, theme["info"])
    trend_icon = trend_icons.get(trend_direction, "➡️")
    
    return html.Div(
        className="trend-stat-card",
        style={
            "backgroundColor": theme["card_bg"],
            "borderRadius": "12px",
            "border": f"2px solid {theme['accent_bg']}",
            "boxShadow": "0 4px 20px rgba(0, 0, 0, 0.2)",
            "padding": "1.5rem",
            "textAlign": "center",
            "transition": "transform 0.2s ease, box-shadow 0.2s ease",
            "position": "relative",
            "overflow": "hidden"
        },
        children=[
            # Trend indicator badge
            html.Div(
                [trend_icon, f" {trend_value}"],
                style={
                    "position": "absolute",
                    "top": "1rem",
                    "right": "1rem",
                    "backgroundColor": trend_color,
                    "color": "white",
                    "padding": "0.25rem 0.5rem",
                    "borderRadius": "12px",
                    "fontSize": "0.8rem",
                    "fontWeight": "600"
                }
            ),
            
            html.Div(
                icon,
                style={
                    "fontSize": "3rem",
                    "marginBottom": "0.5rem"
                }
            ),
            html.H2(
                value,
                style={
                    "fontSize": "2.5rem",
                    "fontWeight": "800",
                    "color": theme["brand_primary"],
                    "margin": "0.5rem 0",
                    "lineHeight": "1.2"
                }
            ),
            html.P(
                title,
                style={
                    "fontSize": "1.125rem",
                    "color": theme["text_secondary"],
                    "fontWeight": "600",
                    "margin": "0.5rem 0 0 0"
                }
            ),
            html.P(
                unit,
                style={
                    "fontSize": "0.875rem",
                    "color": theme["success"],
                    "fontWeight": "500",
                    "margin": "0"
                }
            )
        ]
    )

def create_metric_grid(metrics_data, theme_styles, columns=4):
    """
    Create a grid of metric cards
    
    Args:
        metrics_data (list): List of metric dictionaries
        theme_styles (dict): Theme styling
        columns (int): Number of columns for grid
        
    Returns:
        html.Div: Grid of metric cards
    """
    return html.Div(
        style={
            "display": "grid",
            "gridTemplateColumns": f"repeat(auto-fit, minmax(250px, 1fr))",
            "gap": "1.5rem",
            "margin": "2rem 0"
        },
        children=[
            create_stat_card(
                icon=metric.get("icon", "📊"),
                title=metric.get("title", "Metric"),
                value=metric.get("value", "0"),
                unit=metric.get("unit", ""),
                theme_styles=theme_styles,
                size=metric.get("size", "normal")
            ) for metric in metrics_data
        ]
    )

def create_compact_stat_card(icon, title, value, theme_styles):
    """
    Create a compact version of stat card for smaller spaces
    """
    theme = theme_styles["theme"]
    
    return html.Div(
        style={
            "backgroundColor": theme["card_bg"],
            "borderRadius": "8px",
            "border": f"1px solid {theme['accent_bg']}",
            "padding": "1rem",
            "display": "flex",
            "alignItems": "center",
            "gap": "1rem",
            "transition": "all 0.2s ease"
        },
        children=[
            html.Div(
                icon,
                style={
                    "fontSize": "2rem",
                    "flexShrink": "0"
                }
            ),
            html.Div([
                html.H3(
                    value,
                    style={
                        "fontSize": "1.5rem",
                        "fontWeight": "700",
                        "color": theme["brand_primary"],
                        "margin": "0",
                        "lineHeight": "1.2"
                    }
                ),
                html.P(
                    title,
                    style={
                        "fontSize": "0.9rem",
                        "color": theme["text_secondary"],
                        "margin": "0",
                        "fontWeight": "500"
                    }
                )
            ])
        ]
    )