# callbacks/drap_callbacks_drap.py
"""
DRAP Endpoint Callbacks
- Loader hide after 2 seconds
- Login → Dashboard
"""

from dash import callback, Output, Input, State, ctx
from dash.exceptions import PreventUpdate
from config.themes import THEMES, DEFAULT_THEME
import flask
import logging

logger = logging.getLogger(__name__)

DRAP_CREDENTIALS = {
    "username": "drap_admin",
    "password": "drap@2024"
}


def validate_drap_credentials(username, password):
    return (username == DRAP_CREDENTIALS["username"] and 
            password == DRAP_CREDENTIALS["password"])


def register_drap_callbacks(app):
    """Register DRAP callbacks"""
    
    # ========== HIDE LOADER AFTER 2 SECONDS ==========
    @app.callback(
        Output('drap-loading-screen', 'style'),
        Input('drap-loader-interval', 'n_intervals'),
        prevent_initial_call=True
    )
    def hide_drap_loader(n_intervals):
        """Hide the loader after interval fires"""
        if n_intervals and n_intervals >= 1:
            return {
                "position": "fixed",
                "top": "0",
                "left": "0",
                "width": "100%",
                "height": "100%",
                "background": "linear-gradient(135deg, #0D1B2A 0%, #1A1F2E 100%)",
                "display": "flex",
                "justifyContent": "center",
                "alignItems": "center",
                "zIndex": "9999",
                "opacity": "0",
                "pointerEvents": "none",
                "transition": "opacity 0.8s ease"
            }
        raise PreventUpdate
    
    # ========== LOGIN ==========
    @app.callback(
        [
            Output('drap-authenticated', 'data'),
            Output('drap-user-data', 'data'),
            Output('drap-login-error', 'children'),
            Output('drap-login-error', 'style'),
            Output('url', 'pathname', allow_duplicate=True)
        ],
        Input('drap-login-button', 'n_clicks'),
        [
            State('drap-username-input', 'value'),
            State('drap-password-input', 'value'),
            State('current-theme', 'data')
        ],
        prevent_initial_call=True
    )
    def handle_drap_login(n_clicks, username, password, theme_name):
        """Handle login"""
        if not n_clicks:
            raise PreventUpdate
        
        theme = THEMES.get(theme_name or DEFAULT_THEME, THEMES[DEFAULT_THEME])
        
        error_hidden = {"display": "none"}
        error_visible = {
            "display": "block",
            "backgroundColor": f"{theme.get('error', '#E53E3E')}20",
            "border": f"1px solid {theme.get('error', '#E53E3E')}",
            "borderRadius": "8px",
            "padding": "0.75rem 1rem",
            "marginBottom": "1rem",
            "color": theme.get("error", "#E53E3E"),
            "fontSize": "0.9rem",
            "textAlign": "center"
        }
        
        if not username or not password:
            return False, {}, "Please enter both username and password", error_visible, '/DRAP'
        
        if validate_drap_credentials(username, password):
            logger.info(f"DRAP login successful: {username}")
            from datetime import datetime
            user_data = {
                "username": username,
                "authenticated": True,
                "login_time": datetime.now().isoformat()
            }
            
            flask.session['drap_authenticated'] = True
            flask.session['drap_user'] = username
            flask.session['drap_user_data'] = user_data
            
            return True, user_data, "", error_hidden, '/DRAP/dashboard'
        else:
            logger.warning(f"DRAP login failed: {username}")
            return False, {}, "Invalid username or password", error_visible, '/DRAP'
    
    logger.info("✅ DRAP callbacks registered")