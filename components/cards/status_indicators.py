# components/cards/status_indicator.py
"""
Status Indicator Component
Shows system status with color coding
"""

from dash import html

def create_status_indicator(label, status, color_key, theme, size="normal"):
    """
    Create a status indicator component
    
    Args:
        label (str): Status label
        status (str): Status text
        color_key (str): Theme color key (success, warning, error, info)
        theme (dict): Theme configuration
        size (str): "small", "normal", or "large"
        
    Returns:
        html.Div: Status indicator component
    """
    
    # Size configurations
    size_config = {
        "small": {
            "padding": "0.5rem 0.75rem",
            "min_width": "120px",
            "dot_size": "1rem",
            "label_size": "0.8rem",
            "status_size": "0.7rem"
        },
        "normal": {
            "padding": "0.75rem 1rem",
            "min_width": "150px",
            "dot_size": "1.25rem",
            "label_size": "0.875rem",
            "status_size": "0.75rem"
        },
        "large": {
            "padding": "1rem 1.5rem",
            "min_width": "180px",
            "dot_size": "1.5rem",
            "label_size": "1rem",
            "status_size": "0.875rem"
        }
    }
    
    config = size_config.get(size, size_config["normal"])
    
    return html.Div(
        className="status-indicator",
        style={
            "display": "flex",
            "alignItems": "center",
            "padding": config["padding"],
            "backgroundColor": theme["card_bg"],
            "borderRadius": "8px",
            "border": f"2px solid {theme[color_key]}",
            "minWidth": config["min_width"],
            "margin": "0.5rem",
            "transition": "all 0.2s ease",
            "cursor": "default"
        },
        children=[
            html.Span(
                "●",
                style={
                    "color": theme[color_key],
                    "fontSize": config["dot_size"],
                    "marginRight": "0.75rem",
                    "animation": "pulse 2s infinite" if status.lower() in ["active", "online", "processing"] else "none"
                }
            ),
            html.Div([
                html.Div(
                    label,
                    style={
                        "fontSize": config["label_size"],
                        "color": theme["text_secondary"],
                        "fontWeight": "500",
                        "lineHeight": "1.2"
                    }
                ),
                html.Div(
                    status.upper(),
                    style={
                        "fontSize": config["status_size"],
                        "color": theme[color_key],
                        "fontWeight": "700",
                        "lineHeight": "1.2"
                    }
                )
            ])
        ]
    )

def create_detailed_status_indicator(label, status, color_key, theme, details=None, timestamp=None):
    """
    Create detailed status indicator with additional information
    
    Args:
        label (str): Status label
        status (str): Status text
        color_key (str): Theme color key
        theme (dict): Theme configuration
        details (str): Additional details text
        timestamp (str): Last updated timestamp
        
    Returns:
        html.Div: Detailed status indicator
    """
    return html.Div(
        className="detailed-status-indicator",
        style={
            "backgroundColor": theme["card_bg"],
            "border": f"2px solid {theme[color_key]}",
            "borderRadius": "12px",
            "padding": "1rem",
            "margin": "0.5rem",
            "transition": "all 0.2s ease"
        },
        children=[
            # Header with status
            html.Div(
                style={
                    "display": "flex",
                    "alignItems": "center",
                    "marginBottom": "0.5rem" if details or timestamp else "0"
                },
                children=[
                    html.Span(
                        "●",
                        style={
                            "color": theme[color_key],
                            "fontSize": "1.5rem",
                            "marginRight": "0.75rem"
                        }
                    ),
                    html.Div([
                        html.H4(
                            label,
                            style={
                                "fontSize": "1rem",
                                "color": theme["text_primary"],
                                "fontWeight": "600",
                                "margin": "0"
                            }
                        ),
                        html.P(
                            status.upper(),
                            style={
                                "fontSize": "0.8rem",
                                "color": theme[color_key],
                                "fontWeight": "700",
                                "margin": "0"
                            }
                        )
                    ])
                ]
            ),
            
            # Details section
            html.Div([
                html.P(
                    details,
                    style={
                        "fontSize": "0.85rem",
                        "color": theme["text_secondary"],
                        "margin": "0.5rem 0",
                        "lineHeight": "1.4"
                    }
                ) if details else None,
                
                html.P(
                    f"Last updated: {timestamp}",
                    style={
                        "fontSize": "0.75rem",
                        "color": theme["text_muted"] if "text_muted" in theme else theme["text_secondary"],
                        "margin": "0",
                        "fontStyle": "italic"
                    }
                ) if timestamp else None
            ]) if details or timestamp else None
        ]
    )

def create_status_grid(status_data, theme, columns=4):
    """
    Create a grid of status indicators
    
    Args:
        status_data (list): List of status dictionaries
        theme (dict): Theme configuration
        columns (int): Number of columns
        
    Returns:
        html.Div: Grid of status indicators
    """
    return html.Div(
        style={
            "display": "flex",
            "flexWrap": "wrap",
            "gap": "1rem",
            "justifyContent": "flex-start"
        },
        children=[
            create_status_indicator(
                label=status.get("label", "Status"),
                status=status.get("status", "Unknown"),
                color_key=status.get("color_key", "info"),
                theme=theme,
                size=status.get("size", "normal")
            ) for status in status_data
        ]
    )

def create_compact_status_bar(status_items, theme):
    """
    Create a compact horizontal status bar
    
    Args:
        status_items (list): List of status items
        theme (dict): Theme configuration
        
    Returns:
        html.Div: Compact status bar
    """
    return html.Div(
        style={
            "display": "flex",
            "gap": "1rem",
            "padding": "0.5rem 1rem",
            "backgroundColor": theme["accent_bg"],
            "borderRadius": "8px",
            "alignItems": "center",
            "flexWrap": "wrap"
        },
        children=[
            html.Div(
                style={
                    "display": "flex",
                    "alignItems": "center",
                    "gap": "0.5rem"
                },
                children=[
                    html.Span(
                        "●",
                        style={
                            "color": theme[item.get("color_key", "info")],
                            "fontSize": "1rem"
                        }
                    ),
                    html.Span(
                        f"{item.get('label', 'Status')}: {item.get('status', 'Unknown')}",
                        style={
                            "fontSize": "0.85rem",
                            "color": theme["text_primary"],
                            "fontWeight": "500"
                        }
                    )
                ]
            ) for item in status_items
        ]
    )