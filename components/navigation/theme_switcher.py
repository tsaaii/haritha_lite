# components/navigation/theme_switcher.py
"""
Theme Switcher Component
Handles theme selection UI
"""

from dash import html
from config.themes import THEMES

def create_theme_switcher(current_theme="dark"):
    """
    Create theme switcher component for overlay banner
    
    Args:
        current_theme (str): Currently active theme
        
    Returns:
        html.Div: Theme switcher component
    """
    theme = THEMES[current_theme]
    
    return html.Div(
        style={
            "display": "flex",
            "flexDirection": "column",
            "alignItems": "center",
            "gap": "0.5rem"
        },
        children=[
            html.Div(
                "🎨 Themes",
                style={
                    "color": theme["text_secondary"],
                    "fontSize": "0.8rem",
                    "fontWeight": "600"
                }
            ),
            html.Div(
                style={
                    "display": "flex",
                    "gap": "0.3rem",
                    "backgroundColor": theme["card_bg"],
                    "padding": "0.4rem",
                    "borderRadius": "10px",
                    "border": f"2px solid {theme['accent_bg']}",
                    "alignItems": "center",
                    "justifyContent": "center"
                },
                children=[
                    html.Button(
                        theme_data["icon"],
                        id=f"theme-{theme_key}",
                        title=theme_data["name"],
                        style={
                            "background": theme["brand_primary"] if theme_key == current_theme else "transparent",
                            "border": f"2px solid {theme['brand_primary']}" if theme_key == current_theme else "1px solid transparent",
                            "color": "white" if theme_key == current_theme else theme["text_primary"],
                            "fontSize": "1.1rem",
                            "padding": "0.5rem",
                            "cursor": "pointer",
                            "borderRadius": "6px",
                            "transition": "all 0.2s ease",
                            "width": "36px",
                            "height": "36px",
                            "display": "flex",
                            "alignItems": "center",
                            "justifyContent": "center",
                            "flexShrink": "0"
                        }
                    ) for theme_key, theme_data in THEMES.items()
                ]
            )
        ]
    )

def create_simple_theme_switcher(current_theme="dark", orientation="horizontal"):
    """
    Create a simple theme switcher without labels
    
    Args:
        current_theme (str): Currently active theme
        orientation (str): "horizontal" or "vertical"
        
    Returns:
        html.Div: Simple theme switcher
    """
    theme = THEMES[current_theme]
    
    return html.Div(
        style={
            "display": "flex",
            "flexDirection": "row" if orientation == "horizontal" else "column",
            "gap": "0.5rem",
            "backgroundColor": theme["card_bg"],
            "padding": "0.5rem",
            "borderRadius": "8px",
            "border": f"2px solid {theme['accent_bg']}"
        },
        children=[
            html.Button(
                theme_data["icon"],
                id=f"simple-theme-{theme_key}",
                title=theme_data["name"],
                style={
                    "background": theme["brand_primary"] if theme_key == current_theme else "transparent",
                    "border": "none",
                    "color": "white" if theme_key == current_theme else theme["text_primary"],
                    "fontSize": "1.2rem",
                    "padding": "0.5rem",
                    "cursor": "pointer",
                    "borderRadius": "6px",
                    "transition": "all 0.2s ease",
                    "width": "40px",
                    "height": "40px",
                    "display": "flex",
                    "alignItems": "center",
                    "justifyContent": "center"
                }
            ) for theme_key, theme_data in THEMES.items()
        ]
    )