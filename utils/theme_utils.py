# utils/theme_utils.py
"""
Theme utility functions
Handles theme styling and CSS generation
"""

from config.themes import THEMES, DEFAULT_THEME

def get_theme_styles(theme_name=None):
    """Generate style dictionaries for a theme"""
    if theme_name is None:
        theme_name = DEFAULT_THEME
        
    theme = THEMES.get(theme_name, THEMES[DEFAULT_THEME])
    
    return {
        "body_style": {
            "fontFamily": "Inter, sans-serif",
            "backgroundColor": theme["primary_bg"],
            "color": theme["text_primary"],
            "margin": "0",
            "padding": "0",
            "lineHeight": "1.6"
        },
        "container_style": {
            "minHeight": "100vh",
            "display": "flex",
            "flexDirection": "column",
            "backgroundColor": theme["primary_bg"]
        },
        "main_content_style": {
            "flex": "1",
            "padding": "2rem",
            "paddingBottom": "5rem",
            "backgroundColor": theme["primary_bg"],
            "color": theme["text_primary"]
        },
        "hero_style": {
            "background": f"linear-gradient(135deg, {theme['secondary_bg']} 0%, {theme['accent_bg']} 100%)",
            "borderRadius": "12px",
            "boxShadow": "0 8px 32px rgba(0, 0, 0, 0.3)",
            "textAlign": "center",
            "padding": "2rem 0",
            "margin": "1rem 0"
        },
        "card_style": {
            "backgroundColor": theme["card_bg"],
            "borderRadius": "12px",
            "border": f"2px solid {theme['accent_bg']}",
            "boxShadow": "0 4px 20px rgba(0, 0, 0, 0.2)",
            "padding": "1.5rem",
            "textAlign": "center",
            "transition": "transform 0.2s ease, box-shadow 0.2s ease"
        },
        "status_section_style": {
            "backgroundColor": theme["accent_bg"],
            "border": f"2px solid {theme['card_bg']}",
            "borderRadius": "8px",
            "padding": "1.5rem",
            "margin": "1rem 0"
        },
        "theme": theme
    }

def get_hover_overlay_css():
    """Get CSS for hover overlay functionality"""
    return """
        /* Hover overlay system */
        #hover-trigger-area:hover + #overlay-banner,
        #overlay-banner:hover {
            transform: translateY(0) !important;
            opacity: 1 !important;
            pointer-events: auto !important;
        }
        
        /* Smooth hover animations */
        .overlay-banner {
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }
        
        /* Button hover effects in overlay */
        #overlay-banner button:hover {
            transform: translateY(-2px) scale(1.05) !important;
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4) !important;
        }
        
        /* Theme button hover effects */
        #overlay-banner button[id^="theme-"]:hover {
            transform: scale(1.2) !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
        }
        
        /* Navigation button hover effects */
        #nav-overview:hover, #nav-analytics:hover, #nav-reports:hover {
            background: var(--brand-primary, #3182CE) !important;
            color: white !important;
            border-color: var(--brand-primary, #3182CE) !important;
        }
        
        /* Admin login button special effect */
        #admin-login-btn:hover {
            transform: translateY(-3px) !important;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.5) !important;
            filter: brightness(1.1) !important;
        }
        
        /* Mobile responsive overlay */
        @media (max-width: 768px) {
            #overlay-banner {
                flex-direction: column !important;
                gap: 1rem !important;
                padding: 1rem !important;
                max-height: 60vh !important;
                overflow-y: auto !important;
            }
            
            #overlay-banner > div {
                flex-direction: column !important;
                gap: 0.75rem !important;
                width: 100% !important;
                align-items: center !important;
            }
            
            #overlay-banner button {
                font-size: 0.9rem !important;
                padding: 0.5rem 1rem !important;
            }
        }
        
        /* TV/Large screen optimizations */
        @media (min-width: 1920px) {
            #overlay-banner {
                padding: 1.5rem 3rem 2rem 3rem !important;
                font-size: 1.2rem !important;
            }
            
            #overlay-banner button {
                font-size: 1.2rem !important;
                padding: 0.8rem 1.5rem !important;
            }
        }
        
        /* Subtle hover indicator */
        #hover-trigger-area::after {
            content: '⬇ Hover here for navigation';
            position: absolute;
            top: 5px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(49, 130, 206, 0.9);
            color: white;
            padding: 0.25rem 0.75rem;
            border-radius: 12px;
            font-size: 0.7rem;
            font-weight: 600;
            opacity: 0;
            transition: opacity 0.3s ease;
            pointer-events: none;
            white-space: nowrap;
        }
        
        #hover-trigger-area:hover::after {
            opacity: 1;
        }
    """


def get_theme_css_variables(theme_name):
    """Generate CSS variables for the current theme"""
    theme = THEMES[theme_name]
    
    return f"""
    :root {{
        --primary-bg: {theme['primary_bg']};
        --card-bg: {theme['card_bg']};
        --accent-bg: {theme['accent_bg']};
        --text-primary: {theme['text_primary']};
        --text-secondary: {theme['text_secondary']};
        --brand-primary: {theme['brand_primary']};
        --border-light: {theme.get('border_light', theme['accent_bg'])};
    }}
    """



def inject_theme_css_variables(theme_name):
    """Inject CSS variables for current theme"""
    theme = THEMES[theme_name]
    
    css_variables = f"""
    <style>
    :root {{
        --primary-bg: {theme['primary_bg']};
        --card-bg: {theme['card_bg']};
        --accent-bg: {theme['accent_bg']};
        --text-primary: {theme['text_primary']};
        --text-secondary: {theme['text_secondary']};
        --brand-primary: {theme['brand_primary']};
        --border-light: {theme.get('border_light', theme['accent_bg'])};
    }}
    </style>
    """
    return css_variables