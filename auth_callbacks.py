"""
Authentication callbacks for username/password login
"""

from dash import callback, Input, Output, State, ctx, html
from dash.exceptions import PreventUpdate
import flask
from flask import session
from auth_utils import validate_credentials, get_quick_login_credentials, create_user_session
import time


@callback(
    [Output('username-input', 'value'),
     Output('password-input', 'value')],
    [Input('quick-admin-btn', 'n_clicks'),
     Input('quick-demo-btn', 'n_clicks'),
     Input('quick-viewer-btn', 'n_clicks')],
    prevent_initial_call=True
)
def handle_quick_login_buttons(admin_clicks, demo_clicks, viewer_clicks):
    """Handle quick login buttons to auto-fill credentials"""
    if not ctx.triggered:
        raise PreventUpdate
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id == 'quick-admin-btn' and admin_clicks:
        creds = get_quick_login_credentials("admin")
        return creds["username"], creds["password"]
    elif button_id == 'quick-demo-btn' and demo_clicks:
        creds = get_quick_login_credentials("demo")
        return creds["username"], creds["password"]
    elif button_id == 'quick-viewer-btn' and viewer_clicks:
        creds = get_quick_login_credentials("viewer")
        return creds["username"], creds["password"]
    
    raise PreventUpdate


@callback(
    [Output('login-status-message', 'children'),
     Output('login-status-message', 'style'),
     Output('url', 'pathname', allow_duplicate=True)],
    [Input('credentials-login-btn', 'n_clicks'),
     Input('password-input', 'n_submit')],  # Allow Enter key to submit
    [State('username-input', 'value'),
     State('password-input', 'value'),
     State('login-status-message', 'style')],
    prevent_initial_call=True
)
def handle_credentials_login(login_clicks, password_submit, username, password, current_style):
    """Handle username/password authentication"""
    if not ctx.triggered:
        raise PreventUpdate
    
    # Check if login button was clicked or Enter was pressed in password field
    trigger = ctx.triggered[0]
    if not ((trigger['prop_id'] == 'credentials-login-btn.n_clicks' and login_clicks) or
            (trigger['prop_id'] == 'password-input.n_submit' and password_submit)):
        raise PreventUpdate
    
    # Validate input
    if not username or not password:
        error_style = current_style.copy() if current_style else {}
        error_style.update({
            "color": "#ef4444",
            "fontSize": "0.9rem",
            "marginBottom": "1rem",
            "minHeight": "20px",
            "textAlign": "center"
        })
        return "Please enter both username and password", error_style, '/login'
    
    # Authenticate user
    success, message, user_data = validate_credentials(username.strip(), password)
    
    if success:
        # Create user session
        session_data = create_user_session(user_data)
        
        # Store session data in Flask session
        session['swaccha_session_id'] = f"cred_{username}_{int(time.time())}"
        session['user_data'] = session_data
        session['authenticated'] = True
        session['auth_method'] = 'credentials'
        session['username'] = username
        session['role'] = user_data.get('role', 'user')
        session['permissions'] = user_data.get('permissions', [])
        
        # Success style
        success_style = current_style.copy() if current_style else {}
        success_style.update({
            "color": "#10b981",
            "fontSize": "0.9rem",
            "marginBottom": "1rem",
            "minHeight": "20px",
            "textAlign": "center"
        })
        
        # Redirect to admin dashboard
        return f"Login successful! Welcome, {username}", success_style, '/dashboard'
    
    else:
        # Error style
        error_style = current_style.copy() if current_style else {}
        error_style.update({
            "color": "#ef4444",
            "fontSize": "0.9rem",
            "marginBottom": "1rem",
            "minHeight": "20px",
            "textAlign": "center"
        })
        return message, error_style, '/login'


@callback(
    Output('credentials-login-btn', 'style'),
    [Input('username-input', 'value'),
     Input('password-input', 'value')],
    [State('credentials-login-btn', 'style')],
    prevent_initial_call=True
)
def update_login_button_style(username, password, current_style):
    """Update login button style based on input state"""
    if not current_style:
        # Default style if none provided
        current_style = {
            "width": "100%",
            "padding": "12px 20px",
            "backgroundColor": "#3182ce",
            "color": "white",
            "border": "none",
            "borderRadius": "8px",
            "fontSize": "1rem",
            "fontWeight": "600",
            "cursor": "pointer",
            "transition": "all 0.2s ease",
            "display": "flex",
            "alignItems": "center",
            "justifyContent": "center",
            "marginBottom": "1rem",
            "boxShadow": "0 4px 12px #3182ce44"
        }
    
    new_style = current_style.copy()
    
    # Enable/disable button based on input
    if username and password:
        new_style.update({
            "backgroundColor": "#3182ce",
            "cursor": "pointer",
            "opacity": "1"
        })
    else:
        new_style.update({
            "backgroundColor": "#9ca3af",
            "cursor": "not-allowed",
            "opacity": "0.6"
        })
    
    return new_style


@callback(
    [Output('username-input', 'style'),
     Output('password-input', 'style')],
    [Input('username-input', 'value'),
     Input('password-input', 'value')],
    [State('username-input', 'style'),
     State('password-input', 'style')],
    prevent_initial_call=True
)
def update_input_styles(username, password, username_style, password_style):
    """Update input field styles for better UX"""
    
    # Default styles if none provided
    default_input_style = {
        "width": "100%",
        "padding": "12px 16px",
        "border": "2px solid #e5e7eb",
        "borderRadius": "8px",
        "fontSize": "1rem",
        "backgroundColor": "#ffffff",
        "color": "#374151",
        "outline": "none",
        "transition": "all 0.2s ease",
        "marginBottom": "1rem"
    }
    
    username_style = username_style or default_input_style.copy()
    password_style = password_style or default_input_style.copy()
    
    # Update username input style
    if username:
        username_style.update({
            "borderColor": "#10b981",
            "boxShadow": "0 0 0 3px rgba(16, 185, 129, 0.1)"
        })
    else:
        username_style.update({
            "borderColor": "#e5e7eb",
            "boxShadow": "none"
        })
    
    # Update password input style
    if password:
        password_style.update({
            "borderColor": "#10b981",
            "boxShadow": "0 0 0 3px rgba(16, 185, 129, 0.1)"
        })
    else:
        password_style.update({
            "borderColor": "#e5e7eb",
            "boxShadow": "none"
        })
    
    return username_style, password_style


# Additional callback to handle session validation
@callback(
    Output('session-validation', 'children'),
    [Input('url', 'pathname')],
    prevent_initial_call=True
)
def validate_session(pathname):
    """Validate user session for protected routes"""
    if pathname in ['/admin', '/analytics', '/reports']:
        # Check if user is authenticated
        if not session.get('authenticated', False):
            # Redirect to login if not authenticated
            return html.Script("""
                window.location.href = '/login';
            """)
    
    return ""


# Logout callback
@callback(
    Output('url', 'search', allow_duplicate=True),
    [Input('overlay-logout-btn', 'n_clicks')],
    prevent_initial_call=True
)
def handle_logout(logout_clicks):
    """Handle user logout"""
    if logout_clicks:
        # Clear session
        session.clear()
        
        # Redirect to public page with logout parameter
        return "?logout=true"
    
    raise PreventUpdate