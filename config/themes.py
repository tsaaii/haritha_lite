# config/themes.py
"""
Theme configurations for Swaccha Andhra Dashboard
Centralized theme management
"""

# Theme configurations
THEMES = {
    "dark": {
        "name": "Dark Mode",
        "icon": "🌙",
        "primary_bg": "#0A0E1A",
        "secondary_bg": "#0D1B2A",
        "accent_bg": "#1A1F2E",
        "card_bg": "#2D3748",
        "text_primary": "#FFFFFF",
        "text_secondary": "#A0AEC0",
        "border_light": "#2D3748",
        "border_medium": "#4A5568",
        "brand_primary": "#eb9534",
        "success": "#38A169",
        "warning": "#DD6B20",
        "error": "#E53E3E",
        "info": "#eb9534"
    },
    "light": {
        "name": "Light Mode",
        "icon": "☀️",
        "primary_bg": "#FFFFFF",
        "secondary_bg": "#F7FAFC",
        "accent_bg": "#EDF2F7",
        "card_bg": "#FFFFFF",
        "text_primary": "#1A202C",
        "text_secondary": "#4A5568",
        "border_light": "#E2E8F0",
        "border_medium": "#CBD5E0",
        "brand_primary": "#eb9534",
        "success": "#38A169",
        "warning": "#D69E2E",
        "error": "#E53E3E",
        "info": "#eb9534"
    },
    "high_contrast": {
        "name": "High Contrast",
        "icon": "🔳",
        "primary_bg": "#000000",
        "secondary_bg": "#000000",
        "accent_bg": "#1A1A1A",
        "card_bg": "#000000",
        "text_primary": "#FFFFFF",
        "text_secondary": "#FFFFFF",
        "border_light": "#FFFFFF",
        "border_medium": "#FFFFFF",
        "brand_primary": "#4A90E2",
        "success": "#00FF00",
        "warning": "#FFD700",
        "error": "#FF4444",
        "info": "#00BFFF"
    },
    "swaccha_green": {
        "name": "Swaccha Green",
        "icon": "🌿",
        "primary_bg": "#0D1B0F",
        "secondary_bg": "#1A2F1D",
        "accent_bg": "#264829",
        "card_bg": "#2D5A31",
        "text_primary": "#FFFFFF",
        "text_secondary": "#B8E6C1",
        "border_light": "#2D5A31",
        "border_medium": "#4F7F53",
        "brand_primary": "#4CAF50",
        "success": "#81C784",
        "warning": "#FFA726",
        "error": "#EF5350",
        "info": "#42A5F5"
    }
}

DEFAULT_THEME = "dark"

def get_theme(theme_name=None):
    """Get theme configuration by name"""
    if theme_name is None:
        theme_name = DEFAULT_THEME
    return THEMES.get(theme_name, THEMES[DEFAULT_THEME])

def get_available_themes():
    """Get list of all available themes"""
    return list(THEMES.keys())

def get_theme_display_info():
    """Get theme display information for UI"""
    return [(key, theme["name"], theme["icon"]) for key, theme in THEMES.items()]