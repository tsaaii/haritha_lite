"""
BULLETPROOF Main Application with Google OAuth and Unauthorized Access Handling
COMPLETELY FIXED - Resolved all callback conflicts and JavaScript errors
DASHBOARD CODE MOVED TO admin_dashboard.py
"""

import dash
from dash import html, dcc, callback, Input, Output, State, ctx, clientside_callback
from dash.exceptions import PreventUpdate
import flask
from flask import request, redirect, session
import urllib.parse
import os
import logging
import time
from datetime import datetime,timedelta
from flask import session, redirect, request
from utils.theme_utils import get_theme_styles
import json
import subprocess
import threading
from config.themes import THEMES, DEFAULT_THEME
from utils.theme_utils import get_hover_overlay_css
from simple_legacy_report import legacy_bp
from flask_bootstrap import Bootstrap
#from layouts.public_layout import build_public_layout
from layouts.login_layout import build_login_layout
from site_dashboard import site_dashboard_bp
from file_watcher import start_file_monitoring, stop_file_monitoring

# Ã¢ÂÅ’ REMOVED: from callbacks.filter_container_callbacks import register_filter_container_callbacks
from data_loader import get_cached_data, refresh_cached_data
from services.auth_service import auth_service
# Ã¢ÂÅ’ REMOVED: from callbacks.dashboard_filter_callbacks import register_dashboard_filter_callbacks
# Ã¢Å“â€¦ FIXED: Import dashboard routes but with custom registration to avoid conflicts
# Ã¢Å“â€¦ ONLY IMPORT: The consolidated callbacks
#from callbacks.consolidated_filter_callbacks import register_all_callbacks
from layouts.public_layout_uniform import build_public_layout

from pathlib import Path

# app = dash.Dash(__name__)
# app.layout = html.Div([
#     dcc.Store(id='current-theme', data=DEFAULT_THEME),
#     dcc.Store(id='user-authenticated', data=False),
#     dcc.Store(id='current-page', data='public_landing'),
#     dcc.Location(id='url', refresh=False),
#     html.Div(id="main-layout")
# ])

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import Google OAuth utilities with error handling
try:
    from utils.google_auth import get_google_auth_manager
    google_auth_manager = get_google_auth_manager()
    GOOGLE_AUTH_AVAILABLE = True
    print("Ã¢Å“â€¦ Google OAuth utilities loaded successfully")
    print(f"Ã¢Å“â€¦ Auth manager type: {type(google_auth_manager).__name__}")
    
    # Test if it's the real GoogleAuthManager or MockGoogleAuth
    if hasattr(google_auth_manager, 'client_secrets_file'):
        print("Ã¢Å“â€¦ Real GoogleAuthManager detected")
        REAL_OAUTH_AVAILABLE = True
    else:
        print("Ã¢Å¡ Ã¯Â¸Â MockGoogleAuth detected - client_secrets.json missing or invalid")
        REAL_OAUTH_AVAILABLE = False
        
except Exception as e:
    print(f"Ã¢ÂÅ’ Google OAuth utilities not available: {e}")
    google_auth_manager = None
    GOOGLE_AUTH_AVAILABLE = False
    REAL_OAUTH_AVAILABLE = False

# Initialize Dash app
server = flask.Flask(__name__)
server.secret_key = 'your-secret-key-change-this-in-production'

# Enhanced session configuration
server.config.update(
    SESSION_COOKIE_SECURE=False,  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    PERMANENT_SESSION_LIFETIME=timedelta(hours=1)
)



app = dash.Dash(
    __name__, 
    server=server,
    suppress_callback_exceptions=True, 
    title="Swachha Andhra  Dashboard",
    external_stylesheets=[
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap",
        "/assets/dashboard.css",                    # This works (200/304)
        "/assets/dashboard_filters.css",            # This works (304)
        "/assets/style.css",                        # This works (304)
        "/assets/css/public_layout_consolidated.css" # This works (304)
    ],
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"},
        {"name": "theme-color", "content": "#0D1B2A"},
        {"name": "description", "content": "Real-time cleanliness monitoring dashboard"}
    ]
)

# Enhanced PWA configuration - SIMPLIFIED RELIABLE APPROACH
app.index_string = f'''
<!DOCTYPE html>
<html lang="en">
    <head>
        {{%metas%}}
        <title>{{%title%}}</title>
        {{%favicon%}}
        {{%css%}}
        <link rel="manifest" href="/assets/manifest.json">
        <style>
            {get_hover_overlay_css()}
            
            /* Enhanced Google OAuth styling */
            #google-login-btn, #google-login-btn-alt {{
                position: relative;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            }}
            
            #google-login-btn:hover, #google-login-btn-alt:hover {{
                background-color: #3367d6 !important;
                box-shadow: 0 8px 25px rgba(66, 133, 244, 0.5) !important;
                transform: translateY(-2px) scale(1.02) !important;
            }}
            
            /* Loading screen */
            .pwa-loading {{
                position: fixed; top: 0; left: 0; width: 100%; height: 100%;
                background: linear-gradient(135deg, #0D1B2A 0%, #1A1F2E 100%);
                display: flex; justify-content: center; align-items: center; 
                z-index: 9999; opacity: 1; transition: opacity 0.8s ease;
            }}
            .pwa-loading.hidden {{ opacity: 0; pointer-events: none; }}
        </style>
    </head>
    <body>
        <!-- Loading Screen -->

<div id="pwa-loading" class="pwa-loading">
    <div style="text-align: center; color: white; position: relative;">
        <!-- Logo container with aura -->
        <div style="position: relative; display: inline-block; margin-bottom: 1rem;">
            <!-- Your right.png logo -->
            <img src="/assets/img/right.png" alt="Logo" style="
                width: 80px; 
                height: 80px; 
                object-fit: contain; 
                filter: drop-shadow(0 4px 15px rgba(255,255,255,0.3));
                animation: logoFloat 2s ease-in-out infinite;
                position: relative;
                z-index: 2;
            ">
            
            <!-- Aura rings -->
            <div style="
                position: absolute;
                top: 50%; left: 50%;
                width: 100px; height: 100px;
                margin: -50px 0 0 -50px;
                border: 2px solid rgba(49,130,206,0.6);
                border-radius: 50%;
                animation: auraExpand 2s linear infinite;
            "></div>
            <div style="
                position: absolute;
                top: 50%; left: 50%;
                width: 120px; height: 120px;
                margin: -60px 0 0 -60px;
                border: 2px solid rgba(56,178,172,0.4);
                border-radius: 50%;
                animation: auraExpand 2s linear infinite 0.5s;
            "></div>
            <div style="
                position: absolute;
                top: 50%; left: 50%;
                width: 140px; height: 140px;
                margin: -70px 0 0 -70px;
                border: 2px solid rgba(72,187,120,0.3);
                border-radius: 50%;
                animation: auraExpand 2s linear infinite 1s;
            "></div>
        </div>
        
        <div style="font-size: 2rem; font-weight: 900;">స్వర్ణ ఆంధ్ర స్వచ్ఛ ఆంధ్ర</div>
        <div style="font-size: 1.2rem; color: #A0AEC0;">Loading Dashboard...</div>
    </div>
</div>        

        
        {{%app_entry%}}
        {{%config%}}
        {{%scripts%}}
        {{%renderer%}}
        
        <script>
            // Loading screen
            window.addEventListener('load', function() {{
                setTimeout(() => {{
                    const loading = document.getElementById('pwa-loading');
                    if (loading) loading.classList.add('hidden');
                }}, 1500);
            }});
            
            // RELIABLE EVENT DELEGATION APPROACH - FIXED with clean navigation
            document.addEventListener('click', function(e) {{
                console.log('Ã°Å¸Å½Â¯ Click detected on:', e.target.id, e.target.className);
                
                // Handle Admin Login button - FORCE clean navigation
                if (e.target.id === 'admin-login-btn') {{
                    e.preventDefault();
                    e.stopPropagation();
                    console.log('Ã°Å¸â€Â Admin login button clicked - navigating to clean /login');
                    window.location.replace('/login');  // Clean URL without parameters
                    return false;
                }}
                
                // Handle Google OAuth buttons
                if (e.target.id === 'google-login-btn' || e.target.id === 'google-login-btn-alt') {{
                    e.preventDefault();
                    e.stopPropagation();
                    console.log('Ã°Å¸â€Âµ Google OAuth button clicked - redirecting to /oauth/login');
                    window.location.replace('/oauth/login');
                    return false;
                }}
                
                // Handle logout button
                if (e.target.id === 'overlay-logout-btn') {{
                    e.preventDefault();
                    e.stopPropagation();
                    console.log('Ã°Å¸Å¡Âª Logout button clicked - redirecting to /?logout=true');
                    window.location.replace('/?logout=true');
                    return false;
                }}
                
                // Handle clicks on spans inside the buttons (for nested elements)
                const parentButton = e.target.closest('#admin-login-btn, #google-login-btn, #google-login-btn-alt, #overlay-logout-btn');
                if (parentButton) {{
                    e.preventDefault();
                    e.stopPropagation();
                    
                    if (parentButton.id === 'admin-login-btn') {{
                        console.log('Ã°Å¸â€Â Admin login button (nested click) - navigating to clean /login');
                        window.location.replace('/login');  // Clean URL without parameters
                    }} else if (parentButton.id === 'google-login-btn' || parentButton.id === 'google-login-btn-alt') {{
                        console.log('Ã°Å¸â€Âµ Google OAuth button (nested click) - redirecting to /oauth/login');
                        window.location.replace('/oauth/login');
                    }} else if (parentButton.id === 'overlay-logout-btn') {{
                        console.log('Ã°Å¸Å¡Âª Logout button (nested click) - redirecting to /?logout=true');
                        window.location.replace('/?logout=true');
                    }}
                    return false;
                }}
            }});
        </script>
    </body>
</html>
'''
start_file_monitoring()
# Ã¢Å“â€¦ CUSTOM DASHBOARD ROUTE REGISTRATION - AVOIDS CONFLICTS
def register_custom_dashboard_routes(server):
    """Register dashboard routes without conflicts"""
    
    @server.route('/dashboard/csv-relationships')
    def csv_relationships():
        """API endpoint to get CSV data relationships for cascading filters"""
        if not session.get('swaccha_session_id'):
            return {'error': 'Authentication required'}, 401
        
        try:
            from data_loader import get_cached_data
            df = get_cached_data()
            
            if df.empty:
                return flask.jsonify({
                    'agency_clusters': {},
                    'cluster_sites': {},
                    'message': 'No CSV data available'
                })
            
            # Build relationships from CSV data
            agency_clusters = {}
            cluster_sites = {}
            
            # Group by agency to get clusters
            if 'agency' in df.columns and 'cluster' in df.columns:
                grouped = df.groupby('agency')['cluster'].unique()
                for agency, clusters in grouped.items():
                    agency_clusters[agency] = list(clusters)
            
            # Group by cluster to get sites
            if 'cluster' in df.columns and 'site' in df.columns:
                grouped = df.groupby('cluster')['site'].unique()
                for cluster, sites in grouped.items():
                    cluster_sites[cluster] = list(sites)
            
            logger.info(f"Ã¢Å“â€¦ CSV relationships: {len(agency_clusters)} agencies, {len(cluster_sites)} clusters")
            
            return flask.jsonify({
                'agency_clusters': agency_clusters,
                'cluster_sites': cluster_sites,
                'total_records': len(df)
            })
            
        except Exception as e:
            logger.error(f"Ã¢ÂÅ’ Error getting CSV relationships: {e}")
            return flask.jsonify({
                'error': 'Error processing CSV data',
                'message': str(e)
            }), 500
    
    @server.route('/dashboard/filtered-csv-data')
    def filtered_csv_data():
        """API endpoint to get filtered CSV data - RENAMED TO AVOID CONFLICT"""
        if not session.get('swaccha_session_id'):
            return {'error': 'Authentication required'}, 401
        
        try:
            from data_loader import get_cached_data, filter_data
            
            # Get filter parameters from request
            agency = request.args.get('agency', 'all')
            cluster = request.args.get('cluster', 'all')
            site = request.args.get('site', 'all')
            start_date = request.args.get('start_date')
            end_date = request.args.get('end_date')
            
            # Load and filter CSV data
            df = get_cached_data()
            
            if df.empty:
                return flask.jsonify({
                    "error": "No CSV data available",
                    "message": "Please upload a CSV file"
                })
            
            # Apply filters
            filtered_df = filter_data(df, agency, cluster, site, start_date, end_date)
            
            # Calculate statistics using correct column names from your CSV
            record_count = len(filtered_df)
            
            # Use 'Net Weight' column (as per your CSV structure)
            total_weight = 0
            if 'Net Weight' in filtered_df.columns and not filtered_df.empty:
                total_weight = filtered_df['Net Weight'].sum()
            elif 'weight' in filtered_df.columns and not filtered_df.empty:
                total_weight = filtered_df['weight'].sum()
            
            # Use 'Vehicle No' column (as per your CSV structure)
            vehicle_count = 0
            if 'Vehicle No' in filtered_df.columns and not filtered_df.empty:
                vehicle_count = filtered_df['Vehicle No'].nunique()
            elif 'vehicle' in filtered_df.columns and not filtered_df.empty:
                vehicle_count = filtered_df['vehicle'].nunique()
            
            filter_response = {
                "agency": agency,
                "cluster": cluster,
                "site": site,
                "start_date": start_date,
                "end_date": end_date,
                "record_count": record_count,
                "total_weight": f"{total_weight:,.0f} kg",
                "vehicle_count": vehicle_count,
                "timestamp": time.time(),
                "source": "CSV Data with Cascading Filters",
                "total_records_available": len(df)
            }
            
            logger.info(f"Ã¢Å“â€¦ Filtered CSV data: {record_count} records from {len(df)} total")
            
            return flask.jsonify(filter_response)
            
        except Exception as e:
            logger.error(f"Ã¢ÂÅ’ Error filtering CSV data: {e}")
            return flask.jsonify({
                "error": "Error processing CSV data",
                "message": str(e)
            }), 500

# Enhanced Flask routes for Google OAuth

@callback(
    Output('current-theme', 'data'),
    [
        Input('theme-dark', 'n_clicks'),
        Input('theme-light', 'n_clicks'),
        Input('theme-high_contrast', 'n_clicks'),
        Input('theme-swaccha_green', 'n_clicks')
    ],
    [State('current-theme', 'data')],  # Add current theme as state
    prevent_initial_call=True
)
def update_theme_with_session_sync(dark_clicks, light_clicks, contrast_clicks, green_clicks, current_theme):
    """
    Handle theme switching from overlay banner with Flask session synchronization
    FIXED: Prevents reset to dark theme
    """
    if not ctx.triggered:
        return current_theme or DEFAULT_THEME  # Return current theme instead of default
    
    # Check if any button was actually clicked (not just initialized)
    triggered_prop = ctx.triggered[0]
    if triggered_prop['value'] is None or triggered_prop['value'] == 0:
        return current_theme or DEFAULT_THEME
    
    button_id = triggered_prop['prop_id'].split('.')[0]
    theme_map = {
        'theme-dark': 'dark',
        'theme-light': 'light', 
        'theme-high_contrast': 'high_contrast',
        'theme-swaccha_green': 'swaccha_green'
    }
    
    new_theme = theme_map.get(button_id, current_theme or DEFAULT_THEME)
    
    # Only update if it's actually different
    if new_theme != current_theme:
        try:
            session['current_theme'] = new_theme
            logger.info(f"Theme successfully changed: {current_theme} Ã¢â€ â€™ {new_theme}")
        except Exception as e:
            logger.warning(f"Could not sync theme to Flask session: {e}")
    
    return new_theme
# Optional: Add a clientside callback for immediate CSS variable updates
clientside_callback(
    """
    function(theme_name) {
        if (!theme_name) return window.dash_clientside.no_update;
        
        console.log('Ã°Å¸Å½Â¨ Updating theme to:', theme_name);
        
        // Define theme colors - COMPLETE THEME DEFINITIONS
        const themes = {
            'dark': {
                '--primary-bg': '#0D1B2A',
                '--secondary-bg': '#1B263B', 
                '--accent-bg': '#415A77',
                '--card-bg': '#1B263B',
                '--text-primary': '#E0E1DD',
                '--text-secondary': '#778DA9',
                '--brand-primary': '#3182CE',
                '--border-light': '#415A77',
                '--success': '#38A169',
                '--warning': '#DD6B20', 
                '--error': '#E53E3E',
                '--info': '#3182CE'
            },
            'light': {
                '--primary-bg': '#FFFFFF',
                '--secondary-bg': '#F8F9FA',
                '--accent-bg': '#E2E8F0', 
                '--card-bg': '#FFFFFF',
                '--text-primary': '#2D3748',
                '--text-secondary': '#4A5568',
                '--brand-primary': '#3182CE',
                '--border-light': '#E2E8F0',
                '--success': '#38A169',
                '--warning': '#DD6B20',
                '--error': '#E53E3E', 
                '--info': '#3182CE'
            },
            'high_contrast': {
                '--primary-bg': '#000000',
                '--secondary-bg': '#1A1A1A',
                '--accent-bg': '#333333',
                '--card-bg': '#1A1A1A', 
                '--text-primary': '#FFFFFF',
                '--text-secondary': '#CCCCCC',
                '--brand-primary': '#FFFF00',
                '--border-light': '#333333',
                '--success': '#00FF00',
                '--warning': '#FFA500',
                '--error': '#FF0000',
                '--info': '#FFFF00'
            },
            'swaccha_green': {
                '--primary-bg': '#064E3B',
                '--secondary-bg': '#065F46',
                '--accent-bg': '#047857',
                '--card-bg': '#065F46',
                '--text-primary': '#ECFDF5', 
                '--text-secondary': '#A7F3D0',
                '--brand-primary': '#10B981',
                '--border-light': '#047857',
                '--success': '#10B981',
                '--warning': '#F59E0B',
                '--error': '#EF4444',
                '--info': '#06B6D4'
            }
        };
        
        const themeVars = themes[theme_name];
        if (themeVars) {
            const root = document.documentElement;
            
            // Apply all CSS variables
            Object.keys(themeVars).forEach(key => {
                root.style.setProperty(key, themeVars[key]);
            });
            
            console.log('Ã¢Å“â€¦ Theme CSS variables updated successfully');
            
            // Also update theme attribute on body for additional styling
            document.body.setAttribute('data-theme', theme_name);
            
        } else {
            console.warn('Ã¢Å¡ Ã¯Â¸Â Theme not found:', theme_name);
        }
        
        return window.dash_clientside.no_update;
    }
    """,
    Output('current-theme', 'data', allow_duplicate=True),
    Input('current-theme', 'data'),
    prevent_initial_call=True
)


@server.route('/', methods=['POST'])
def handle_theme_change():
    """Handle theme change requests from the frontend"""
    try:
        data = request.get_json()
        if data and 'theme' in data:
            session['current_theme'] = data['theme']
            return {{"status": "success", "theme": data['theme']}}
    except:
        pass
    return {{"status": "error"}}

def generate_static_html_content(theme_name):
    """Generate static HTML version of your layout for faster loading"""
    from layouts.public_layout import get_eight_metric_cards
    
    metrics = get_eight_metric_cards()
    
    # Generate hero section
    hero_html = '''
    <div class="hero-section">
        <div class="hero-content">
            <div style="display: flex; align-items: center;">
                <img src="/assets/img/left.png" alt="Left Logo" style="height: 60px;">
            </div>
            <div class="hero-title-section">
                <h1>Swachha Andhra Corporation</h1>
                <p>Real Time Legacy Waste Remediation Progress Tracker</p>
            </div>
            <div style="display: flex; align-items: center;">
                <img src="/assets/img/right.png" alt="Right Logo" style="height: 60px;">
            </div>
        </div>
    </div>
    '''

    
@server.route('/analytics')  
def analytics_dashboard():
    """Full analytics with charts (uses your existing callbacks)"""
    #from layouts.enhanced_public_landing_bkp import build_enhanced_public_landing
    
    # Get theme and auth data
    theme_name = session.get('current_theme', 'dark')
    is_authenticated = session.get('authenticated', False)
    user_data = session.get('user_data', None)
    
    # Uses your existing public_landing_callbacks.py
    return build_enhanced_public_landing(theme_name, is_authenticated, user_data)


@server.route('/test/overlay')
def test_overlay():
    """Test overlay components"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Overlay Test</title>
        <style>
            body { font-family: Arial; margin: 40px; background: #0D1B2A; color: white; }
            .test-area { 
                height: 100px; 
                background: #3182CE; 
                text-align: center; 
                line-height: 100px;
                margin: 20px 0;
            }
        </style>
    </head>
    <body>
        <h1>Ã°Å¸Â§Âª Hover Overlay Test</h1>
        <div class="test-area">Hover at the very top of this page to test overlay</div>
        <p>The overlay should appear when you hover at the top edge of the page.</p>
        <p><a href="/" style="color: #68D391;">Ã¢â€ Â Back to Dashboard</a></p>
        
        <script>
            // Check if hover overlay CSS is loaded
            const styles = Array.from(document.styleSheets).map(sheet => {
                try {
                    return Array.from(sheet.cssRules).map(rule => rule.cssText).join('\\n');
                } catch(e) {
                    return 'Cannot access stylesheet';
                }
            }).join('\\n');
            
            if (styles.includes('hover-trigger-area') || styles.includes('overlay-banner')) {
                console.log('Ã¢Å“â€¦ Hover overlay CSS detected');
            } else {
                console.log('Ã¢ÂÅ’ Hover overlay CSS not found');
            }
        </script>
    </body>
    </html>
    """

@server.route('/test/flask')
def test_flask():
    """Test if Flask routes are working"""
    return "Flask routes are working! OAuth status: " + str(GOOGLE_AUTH_AVAILABLE)

@server.route('/test-public')
def test_public_layouts():
    # Test normal layout
    normal = build_public_layout("dark")
    
    # Test loading state
    loading = create_loading_layout()
    
    # Test error state
    error = create_error_layout("Network connection failed")
    
    return normal  # or loading/error for testing


@server.route('/oauth/status')
def oauth_status():
    """Check OAuth configuration status"""
    if GOOGLE_AUTH_AVAILABLE and google_auth_manager:
        try:
            test_url, test_state = google_auth_manager.get_authorization_url('http://localhost:8050//oauth/callback')
            return flask.jsonify({
                'available': True,
                'configured': True,
                'message': 'Google OAuth is ready'
            })
        except Exception as e:
            return flask.jsonify({
                'available': True,
                'configured': False,
                'message': f'OAuth config error: {str(e)}'
            })
    else:
        return flask.jsonify({
            'available': False,
            'configured': False,
            'message': 'Google OAuth not available'
        })

@server.route('/oauth/login')
def oauth_login():
    """Initiate OAuth login"""
    try:
        from utils.simple_oauth import get_oauth_manager
        oauth_manager = get_oauth_manager()
        
        logger.info(f"Ã°Å¸â€Â OAuth login attempt - configured: {oauth_manager.is_available()}")
        
        if not oauth_manager.is_available():
            logger.info("Ã¢Å¡ Ã¯Â¸Â OAuth not configured - creating demo session")
            success, message, session_data = oauth_manager.create_demo_session()
            
            if success:
                flask.session['swaccha_session_id'] = session_data['session_id']
                flask.session['user_data'] = session_data
                logger.info("Ã¢Å“â€¦ Demo OAuth session created successfully")
                return redirect('/dashboard')
            else:
                logger.error(f"Ã¢ÂÅ’ Demo session creation failed: {message}")
                return redirect('/login?error=demo_oauth_failed')
        
        # Real OAuth flow
        try:
            auth_url, state = oauth_manager.get_authorization_url()
            
            flask.session.permanent = True
            flask.session['oauth_state'] = state
            flask.session['oauth_timestamp'] = time.time()
            
            logger.info(f"Ã°Å¸â€â€” Redirecting to Google OAuth: {auth_url[:100]}...")
            return redirect(auth_url)
            
        except Exception as e:
            logger.error(f"Ã¢ÂÅ’ OAuth URL generation failed: {e}")
            # Fallback to demo
            success, message, session_data = oauth_manager.create_demo_session()
            if success:
                flask.session['swaccha_session_id'] = session_data['session_id']
                flask.session['user_data'] = session_data
                return redirect('/dashboard')
            else:
                return redirect('/login?error=oauth_fallback_failed')
        
    except Exception as e:
        logger.error(f"Ã¢ÂÅ’ Critical OAuth error: {e}")
        return redirect('/login?error=oauth_critical_error')

@server.route('/oauth/callback')
def oauth_callback():
    """Handle OAuth callback"""
    try:
        from utils.simple_oauth import get_oauth_manager
        
        oauth_manager = get_oauth_manager()
        
        # Get callback parameters
        code = request.args.get('code')
        state = request.args.get('state')
        error = request.args.get('error')
        
        logger.info(f"Ã°Å¸â€œÂ¥ OAuth callback - code: {'Ã¢Å“â€¦' if code else 'Ã¢ÂÅ’'}, state: {'Ã¢Å“â€¦' if state else 'Ã¢ÂÅ’'}, error: {error or 'None'}")
        
        if error:
            logger.error(f"Ã¢ÂÅ’ OAuth error from Google: {error}")
            return redirect(f'/login?error=oauth_denied&details={error}')
        
        if not code:
            logger.error("Ã¢ÂÅ’ No authorization code received")
            return redirect('/login?error=oauth_no_code')
        
        # Exchange code for tokens
        logger.info("Ã°Å¸â€â€ž Starting token exchange...")
        token_response = oauth_manager.exchange_code_for_tokens(code)
        
        if 'error' in token_response:
            logger.error(f"Ã¢ÂÅ’ Token exchange failed: {token_response['error']}")
            return redirect('/login?error=token_exchange_failed')
        
        # Get access token
        access_token = token_response.get('access_token')
        if not access_token:
            logger.error("Ã¢ÂÅ’ No access token in response")
            return redirect('/login?error=no_access_token')
        
        # Get user information
        logger.info("Ã°Å¸â€˜Â¤ Fetching user information...")
        user_info = oauth_manager.get_user_info(access_token)
        
        if 'error' in user_info:
            logger.error(f"Ã¢ÂÅ’ Failed to get user info: {user_info['error']}")
            return redirect('/login?error=user_info_failed')
        
        # Authenticate user
        logger.info(f"Ã°Å¸â€Â Authenticating user: {user_info.get('email', 'unknown')}")
        success, message, session_data = oauth_manager.authenticate_user(user_info)
        
        if success:
            # Store session
            flask.session['swaccha_session_id'] = session_data['session_id']
            flask.session['user_data'] = session_data
            
            logger.info(f"Ã¢Å“â€¦ OAuth login successful for: {user_info.get('email')}")
            return redirect('/dashboard')
        else:
            logger.warning(f"Ã¢ÂÅ’ User authorization failed: {message}")
            return redirect(f'/login?error=unauthorized&message={urllib.parse.quote(message)}')
            
    except Exception as e:
        logger.error(f"Ã¢ÂÅ’ OAuth callback critical error: {e}")
        return redirect('/login?error=oauth_callback_error')

@server.route('/debug/oauth')
def debug_oauth():
    """OAuth debug page"""
    try:
        from utils.simple_oauth import get_oauth_manager
        import json
        
        oauth_manager = get_oauth_manager()
        debug_info = oauth_manager.get_debug_info()
        
        # Additional system checks
        system_info = {
            'python_version': f"{__import__('sys').version_info.major}.{__import__('sys').version_info.minor}",
            'platform': __import__('platform').system(),
            'cwd': os.getcwd(),
            'client_secrets_path': os.path.abspath('client_secrets.json') if os.path.exists('client_secrets.json') else 'Not found'
        }
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Ã°Å¸â€Â§ OAuth Debug Center</title>
            <style>
                body {{ 
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; 
                    margin: 0; padding: 0; background: #0D1B2A; color: #fff; 
                }}
                .container {{ max-width: 1200px; margin: 0 auto; padding: 40px 20px; }}
                .header {{ text-align: center; margin-bottom: 40px; }}
                .section {{ 
                    margin: 30px 0; padding: 25px; background: #1A1F2E; 
                    border-radius: 16px; border: 2px solid #3182CE; 
                }}
                .status {{ 
                    padding: 15px; margin: 10px 0; border-radius: 10px; 
                    display: flex; align-items: center; gap: 15px;
                }}
                .good {{ background: #2D5A31; border: 2px solid #38A169; }}
                .bad {{ background: #5A2D2D; border: 2px solid #E53E3E; }}
                .warning {{ background: #5A4D2D; border: 2px solid #DD6B20; }}
                .icon {{ font-size: 24px; }}
                .details {{ flex: 1; }}
                .label {{ font-weight: 600; font-size: 16px; }}
                .desc {{ font-size: 14px; opacity: 0.8; margin-top: 5px; }}
                pre {{ 
                    background: #000; padding: 20px; border-radius: 12px; 
                    overflow-x: auto; font-size: 13px; line-height: 1.4;
                }}
                .btn {{ 
                    display: inline-block; padding: 15px 30px; margin: 10px 5px; 
                    background: #3182CE; color: white; text-decoration: none; 
                    border-radius: 10px; font-weight: 600; transition: all 0.2s;
                }}
                .btn:hover {{ background: #2C5AA0; transform: translateY(-2px); }}
                .btn.success {{ background: #38A169; }}
                .btn.warning {{ background: #DD6B20; }}
                h1, h2 {{ color: #3182CE; }}
                .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
                @media (max-width: 768px) {{ .grid {{ grid-template-columns: 1fr; }} }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Ã°Å¸â€Â§ OAuth Debug Center</h1>
                    <p>Complete OAuth configuration and testing dashboard</p>
                </div>
                
                <div class="section">
                    <h2>Ã°Å¸Å¡Â¦ System Status</h2>
                    
                    <div class="status {'good' if debug_info.get('oauth_configured') else 'bad'}">
                        <div class="icon">{'Ã¢Å“â€¦' if debug_info.get('oauth_configured') else 'Ã¢ÂÅ’'}</div>
                        <div class="details">
                            <div class="label">OAuth Configuration</div>
                            <div class="desc">
                                {'Properly configured with client_secrets.json' if debug_info.get('oauth_configured') else 'Missing or invalid client_secrets.json file'}
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="grid">
                    <div class="section">
                        <h2>Ã°Å¸Â§Âª Quick Tests</h2>
                        <a href="/oauth/login" class="btn success">Ã°Å¸â€â€” Test OAuth Flow</a>
                        <p><em>Tests the complete OAuth login process</em></p>
                        
                        <a href="/login" class="btn">Ã°Å¸â€œâ€¹ Login Page</a>
                        <p><em>Go to the main login page</em></p>
                        
                        <a href="/" class="btn">Ã°Å¸Â  Dashboard</a>
                        <p><em>Return to main dashboard</em></p>
                    </div>
                </div>
                
                <div class="section">
                    <h2>Ã¢Å¡â„¢Ã¯Â¸Â Configuration Details</h2>
                    <pre>{json.dumps(debug_info, indent=2, default=str)}</pre>
                </div>
                
                <div class="section">
                    <h2>Ã°Å¸â€“Â¥Ã¯Â¸Â System Information</h2>
                    <pre>{json.dumps(system_info, indent=2, default=str)}</pre>
                </div>
            </div>
        </body>
        </html>
        """
        return html
        
    except Exception as e:
        logger.error(f"Debug page error: {e}")
        return f"""
        <html><body style="font-family: monospace; background: #1a1a1a; color: #fff; padding: 40px;">
            <h1>Ã¢ÂÅ’ Debug Error</h1>
            <p>Error loading debug info: {str(e)}</p>
            <p><a href="/" style="color: #3182CE;">Ã¢â€ Â Back to Dashboard</a></p>
        </body></html>
        """

# BULLETPROOF App Layout - All components guaranteed to exist
app.layout = html.Div([
    # Core stores
    dcc.Store(id='current-theme', data=DEFAULT_THEME),
    dcc.Store(id='user-authenticated', data=False),
    dcc.Store(id='current-page', data='public_landing'),
    dcc.Store(id='user-session-data', data={}),
    dcc.Store(id='auth-error-message', data=''),
    dcc.Location(id='url', refresh=False),
    dcc.Interval(id='session-check-interval', interval=30*1000, n_intervals=0),
    
    # Main layout container
    html.Div(id="main-layout"),
    dcc.Download(id="download-link"),
    
    # Analytics export status div (required by consolidated callbacks)
    html.Div(id='analytics-export-status', children=[], style={'display': 'none'}),
    html.Div(id='filtered-data-display', children=[], style={'display': 'none'}),
    html.Div(id='analytics-filter-container-status', children=[], style={'display': 'none'}),
    html.Div(id='analytics-filter-container-status-text', children=[], style={'display': 'none'}),
    
    # BULLETPROOF: All possible callback components in hidden container
    html.Div(
        style={"display": "none"},
        children=[
            # Navigation buttons (exist in hover overlay - all layouts)
            html.Button("Admin Login", id="admin-login-btn"),
            html.Button("Overview", id="overlay-nav-overview"),
            html.Button("Analytics", id="overlay-nav-analytics"),
            html.Button("Reports", id="overlay-nav-reports"),
            
            # Theme buttons (exist in hover overlay - all layouts)
            html.Button("Dark", id="theme-dark"),
            html.Button("Light", id="theme-light"),
            html.Button("High Contrast", id="theme-high_contrast"),
            html.Button("Swaccha Green", id="theme-swaccha_green"),
            
            # Login page buttons (only exist when on login page)
            html.Button("Back to Public", id="back-to-public-btn"),
            html.Button("Google Login", id="google-login-btn"),
            html.Button("Google Login Alt", id="google-login-btn-alt"),   
            html.Button("Demo Login", id="demo-login-btn"),
            html.Button("Admin Account", id="admin-account-btn"),
            html.Button("Dev Account", id="dev-account-btn"),
            html.Button("Viewer Account", id="viewer-account-btn"),
            html.Button("PIN Login", id="pin-login-btn"),
            html.Button("Manual Login", id="manual-login-btn"),
            html.Button("OAuth Debug", id="oauth-debug-btn"),
            html.Button("OAuth Test", id="oauth-test-btn"),
            dcc.Input(id="access-pin", type="password"),
            dcc.Input(id="manual-email", type="email"),
            
            # Admin dashboard buttons (only exist when authenticated)
            html.Button("Quick Reports", id="quick-reports-btn"),
            html.Button("Quick Settings", id="quick-settings-btn"),
            html.Button("Overlay Logout", id="overlay-logout-btn"),
            
            # Tab navigation buttons (exist in admin dashboard only)
            html.Button("Dashboard Tab", id="tab-dashboard"),
            html.Button("Analytics Tab", id="tab-analytics"), 
            html.Button("Reports Tab", id="tab-reports"),
            html.Button("Reviews Tab", id="tab-reviews"),
            html.Button("Upload Tab", id="tab-upload"),
            
            # Tab content container
            html.Div(id="tab-content"),
            
            # Placeholder page buttons
            html.Button("Back to Dashboard", id="back-to-dashboard-btn"),
            
            # Unauthorized page components
            html.Button("Manual Redirect", id="manual-redirect-btn"),
            html.Button("Login Redirect", id="login-redirect-btn"),
            html.Div(id="countdown-display"),
            dcc.Interval(id='unauthorized-redirect-timer', interval=5000, n_intervals=0, max_intervals=1),
            dcc.Interval(id='unauthorized-countdown-timer', interval=1000, n_intervals=0, max_intervals=5),
            
            # Filter components needed by consolidated callbacks
            html.Button("Apply", id="analytics-filter-container-apply-btn"),
            html.Button("Reset", id="analytics-filter-container-reset-btn"),
            html.Button("Export", id="analytics-filter-container-export-btn"),
            html.Div(id="analytics-filter-container"),
            html.Div(id="analytics-filter-container-loading"),  # Loading indicator
            dcc.Dropdown(id="analytics-filter-container-agency-filter"),
            dcc.Dropdown(id="analytics-filter-container-cluster-filter"),
            dcc.Dropdown(id="analytics-filter-container-site-filter"),
            dcc.DatePickerRange(id="analytics-filter-container-date-filter")
        ]
    )
])

# Replace your existing site route handler in main.py with this improved version

from datetime import datetime
import traceback

@server.route('/site/')
def handle_site_list():
    """Handle site list page - no authentication required"""
    print(f"SITE LIST REQUESTED")
    
    try:
        # Import your site functions
        from site_dashboard import get_sites_from_api
        sites = get_sites_from_api()
        
        sites_html = ""
        for site in sites:
            sites_html += f"""
            <div class="col-md-4 mb-3">
                <div class="site-card">
                    <h5>{site.title()}</h5>
                    <p>Andhra Pradesh District</p>
                    <a href="/site/{site}" class="btn-primary">View Dashboard</a>
                    <a href="/site/{site}/api/data" class="btn-secondary">API Data</a>
                </div>
            </div>
            """
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Site List - Swachha Dashboard</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                body {{ 
                    font-family: 'Inter', sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    padding: 20px;
                }}
                .container {{
                    background: white;
                    border-radius: 12px;
                    padding: 2rem;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                    max-width: 1200px;
                    margin: 0 auto;
                }}
                .site-card {{
                    border: 1px solid #dee2e6;
                    border-radius: 8px;
                    padding: 1.5rem;
                    margin-bottom: 1rem;
                    transition: transform 0.2s;
                }}
                .site-card:hover {{
                    transform: translateY(-2px);
                    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                }}
                .btn-primary, .btn-secondary {{
                    background: #3b82f6;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 6px;
                    color: white;
                    text-decoration: none;
                    display: inline-block;
                    margin: 3px;
                }}
                .btn-secondary {{ background: #6b7280; }}
                .btn-primary:hover {{ background: #2563eb; color: white; text-decoration: none; }}
                .btn-secondary:hover {{ background: #4b5563; color: white; text-decoration: none; }}
                .alert-success {{
                    background: #d4edda;
                    border: 1px solid #c3e6cb;
                    color: #155724;
                    padding: 1rem;
                    border-radius: 8px;
                    margin-bottom: 2rem;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Available Sites ({len(sites)} total)</h1>
                
                <div class="alert-success">
                    <strong>âœ… Public Access Working!</strong> No login required for site data.
                </div>
                
                <a href="/" class="btn-primary mb-3">â† Back to Main Dashboard</a>
                
                <div class="row">
                    {sites_html}
                </div>
            </div>
            
            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
        </body>
        </html>
        """
        
        response = flask.make_response(html_content)
        response.headers['Content-Type'] = 'text/html; charset=utf-8'
        response.headers['Cache-Control'] = 'no-cache'
        return response
        
    except Exception as e:
        print(f"ERROR in site list: {e}")
        return f"<html><body><h1>Error loading sites</h1><p>{str(e)}</p></body></html>", 500

@server.route('/site/<site_name>')
def handle_individual_site(site_name):
    """Handle individual site dashboard - using your exact HTML template"""
    print(f"SITE DASHBOARD REQUESTED: {site_name}")
    
    try:
        # Import your site processing function
        from site_dashboard import process_site_data, get_sites_from_api
        
        # Validate site exists
        available_sites = get_sites_from_api()
        if site_name not in available_sites:
            return f"<html><body><h1>Site Not Found</h1><p>Site '{site_name}' not found. Available: {', '.join(available_sites)}</p></body></html>", 404
        
        # Get REAL site data
        target_date = datetime.now().strftime('%Y-%m-%d')
        site_data = process_site_data(site_name, target_date)
        
        print(f"LOADED SITE DATA FOR {site_name}: {site_data.get('total_trips', 0)} trips")
        
        # Your exact HTML template
        html_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ site_name }} Dashboard - Haritha Weighbridge</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary-gradient: linear-gradient(135deg, #eb9534 0%, #DD6B20 100%);
            --secondary-gradient: linear-gradient(135deg, #38A169 0%, #2D7D32 100%);
            --success-gradient: linear-gradient(135deg, #38A169 0%, #2F855A 100%);
            --warning-gradient: linear-gradient(135deg, #DD6B20 0%, #C05621 100%);
            --info-gradient: linear-gradient(135deg, #3182CE 0%, #2C5282 100%);
            --purple-gradient: linear-gradient(135deg, #805AD5 0%, #6B46C1 100%);
            
            --primary-bg: #F8F9FA;
            --secondary-bg: #FFFFFF;
            --card-bg: #FFFFFF;
            --card-hover: #F1F5F9;
            --border-color: #E2E8F0;
            --shadow-light: 0 2px 8px rgba(0, 0, 0, 0.08);
            --shadow-medium: 0 4px 16px rgba(0, 0, 0, 0.12);
            --shadow-heavy: 0 8px 32px rgba(0, 0, 0, 0.16);
            
            --text-primary: #1A202C;
            --text-secondary: #4A5568;
            --text-muted: #718096;
            --text-on-color: #FFFFFF;
            
            --accent-orange: #eb9534;
            --accent-green: #38A169;
            --accent-blue: #3182CE;
            --accent-purple: #805AD5;
            --accent-red: #E53E3E;
            --accent-teal: #319795;
            --accent-pink: #D53F8C;
            --accent-indigo: #5A67D8;
        }
        
        * {
            box-sizing: border-box;
        }
        
        body {
            background: var(--primary-bg);
            color: var(--text-primary);
            font-family: 'Inter', sans-serif;
            margin: 0;
            min-height: 100vh;
            overflow-x: hidden;
        }
        
        .dashboard-header {
            background: var(--primary-gradient);
            padding: 2rem 0;
            margin-bottom: 2rem;
            position: relative;
            overflow: hidden;
            box-shadow: var(--shadow-medium);
        }
        
        .dashboard-header::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 200"><path d="M0,100 C50,150 100,50 200,100 C300,150 400,50 500,100 C600,150 700,50 800,100 C900,150 950,50 1000,100 L1000,200 L0,200 Z" fill="rgba(255,255,255,0.2)"/></svg>') repeat-x;
            background-size: 1000px 200px;
            opacity: 0.4;
        }
        
        .site-header-content {
            position: relative;
            z-index: 2;
        }
        
        .status-indicator {
            display: inline-flex;
            align-items: center;
            padding: 0.5rem 1.2rem;
            border-radius: 50px;
            font-weight: 500;
            font-size: 0.875rem;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.3);
            color: white;
        }
        
        .status-active {
            background: var(--success-gradient);
            border-color: var(--accent-green);
        }
        
        .status-inactive {
            background: var(--warning-gradient);
            border-color: var(--accent-orange);
        }
        
        .metric-card {
            background: var(--card-bg);
            border-radius: 16px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            border: 1px solid var(--border-color);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
            box-shadow: var(--shadow-light);
            height: 180px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        
        .metric-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: var(--primary-gradient);
            opacity: 0;
            transition: opacity 0.3s ease;
            border-radius: 16px 16px 0 0;
        }
        
        .metric-card:hover {
            transform: translateY(-4px);
            background: var(--card-hover);
            border-color: var(--accent-orange);
            box-shadow: var(--shadow-heavy);
        }
        
        .metric-card:hover::before {
            opacity: 1;
        }
        
        .metric-card:nth-child(1) { border-left: 4px solid var(--accent-orange); }
        .metric-card:nth-child(2) { border-left: 4px solid var(--accent-green); }
        .metric-card:nth-child(3) { border-left: 4px solid var(--accent-blue); }
        .metric-card:nth-child(4) { border-left: 4px solid var(--accent-purple); }
        
        .metric-value {
            font-size: 2.25rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }
        
        .metric-card:nth-child(1) .metric-value { color: var(--accent-orange); }
        .metric-card:nth-child(2) .metric-value { color: var(--accent-green); }
        .metric-card:nth-child(3) .metric-value { color: var(--accent-blue); }
        .metric-card:nth-child(4) .metric-value { color: var(--accent-purple); }
        
        .metric-label {
            color: var(--text-secondary);
            font-size: 0.875rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 0.5rem;
        }
        
        .metric-sublabel {
            color: var(--text-muted);
            font-size: 0.75rem;
        }
        
        .progress-circle {
            width: 80px;
            height: 80px;
            position: relative;
            margin: 0 auto 0.5rem auto;
        }
        
        .progress-ring {
            transform: rotate(-90deg);
            width: 100%;
            height: 100%;
        }
        
        .progress-ring-bg {
            fill: none;
            stroke: var(--border-color);
            stroke-width: 8;
        }
        
        .progress-ring-fill {
            fill: none;
            stroke: url(#gradient);
            stroke-width: 8;
            stroke-linecap: round;
            stroke-dasharray: 283;
            stroke-dashoffset: 283;
            transition: stroke-dashoffset 0.5s ease-in-out;
        }
        
        .progress-text {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 1.2rem;
            font-weight: 700;
            color: var(--accent-orange);
        }
        .chart-container {
            height: 300px;
            position: relative;
            background: var(--card-bg);
            border-radius: 12px;
            padding: 1rem;
            border: 1px solid var(--border-color);
            box-shadow: var(--shadow-light);
        }
        
        .material-item {
            background: linear-gradient(135deg, rgba(235, 149, 52, 0.05) 0%, rgba(235, 149, 52, 0.02) 100%);
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 0.75rem;
            border-left: 4px solid var(--accent-orange);
            transition: all 0.2s ease;
            border: 1px solid rgba(235, 149, 52, 0.1);
        }
        
        .material-item:hover {
            background: linear-gradient(135deg, rgba(235, 149, 52, 0.08) 0%, rgba(235, 149, 52, 0.05) 100%);
            transform: translateX(4px);
            box-shadow: var(--shadow-light);
        }
        
        .material-item:nth-child(odd) {
            border-left-color: var(--accent-green);
            background: linear-gradient(135deg, rgba(56, 161, 105, 0.05) 0%, rgba(56, 161, 105, 0.02) 100%);
            border: 1px solid rgba(56, 161, 105, 0.1);
        }
        
        .material-item:nth-child(odd):hover {
            background: linear-gradient(135deg, rgba(56, 161, 105, 0.08) 0%, rgba(56, 161, 105, 0.05) 100%);
        }
        
        .vehicle-card {
            background: var(--card-bg);
            border-radius: 12px;
            padding: 1.25rem;
            margin-bottom: 1rem;
            border: 1px solid var(--border-color);
            transition: all 0.2s ease;
            box-shadow: var(--shadow-light);
        }
        
        .vehicle-card:hover {
            background: var(--card-hover);
            border-color: var(--accent-blue);
            box-shadow: var(--shadow-medium);
            transform: translateY(-2px);
        }
        
        .vehicle-card:nth-child(odd) {
            border-left: 4px solid var(--accent-teal);
        }
        
        .vehicle-card:nth-child(even) {
            border-left: 4px solid var(--accent-purple);
        }
        
        .alert-card {
            background: linear-gradient(135deg, rgba(235, 149, 52, 0.08) 0%, rgba(221, 107, 32, 0.05) 100%);
            border: 2px solid rgba(235, 149, 52, 0.2);
            border-radius: 12px;
            padding: 1rem;
            margin-bottom: 0.75rem;
            box-shadow: var(--shadow-light);
        }
        
        .back-btn {
            background: var(--secondary-gradient);
            border: 2px solid var(--accent-green);
            color: white;
            padding: 0.75rem 1.5rem;
            border-radius: 50px;
            text-decoration: none;
            transition: all 0.3s ease;
            box-shadow: var(--shadow-light);
            font-weight: 500;
        }
        
        .back-btn:hover {
            background: var(--warning-gradient);
            color: white;
            transform: translateY(-2px);
            box-shadow: var(--shadow-medium);
            border-color: var(--accent-orange);
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }
        
        .section-title {
            color: var(--text-primary);
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 1.5rem;
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }
        
        .section-icon {
            width: 32px;
            height: 32px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 14px;
        }
        
        .section-title:nth-of-type(1) .section-icon { background: var(--primary-gradient); }
        .section-title:nth-of-type(2) .section-icon { background: var(--info-gradient); }
        .section-title:nth-of-type(3) .section-icon { background: var(--purple-gradient); }
        .section-title:nth-of-type(4) .section-icon { background: var(--secondary-gradient); }
        
        .info-badge {
            display: inline-flex;
            align-items: center;
            padding: 0.4rem 1rem;
            background: rgba(255, 255, 255, 0.9);
            border-radius: 20px;
            font-size: 0.8rem;
            color: var(--text-secondary);
            margin-bottom: 0.5rem;
            border: 1px solid rgba(255, 255, 255, 0.5);
            backdrop-filter: blur(10px);
            font-weight: 500;
        }
        
        .info-badge:nth-child(3) {
            background: linear-gradient(135deg, rgba(56, 161, 105, 0.2) 0%, rgba(56, 161, 105, 0.1) 100%);
            border-color: var(--accent-green);
            color: var(--accent-green);
        }
        
        .info-badge:nth-child(4) {
            background: linear-gradient(135deg, rgba(49, 151, 149, 0.2) 0%, rgba(49, 151, 149, 0.1) 100%);
            border-color: var(--accent-teal);
            color: var(--accent-teal);
        }
        
        @media (max-width: 768px) {
            .dashboard-header {
                padding: 1.5rem 0;
            }
            
            .metric-value {
                font-size: 1.875rem;
            }
            
            .stats-grid {
                grid-template-columns: 1fr;
                gap: 1rem;
            }
            
            .metric-card {
                padding: 1.25rem;
            }
        }
    </style>
</head>
<body>
    <!-- Header -->
    <div class="dashboard-header">
        <div class="container">
            <div class="site-header-content">
                <div class="row align-items-center">
                    <div class="col-md-8">
                        <h1 class="display-5 fw-bold mb-2">{{ site_name }} Dashboard</h1>
                        <div class="info-badge mb-2">
                            <i class="fas fa-building me-2"></i>
                            Contractor: {{ contractor }}
                        </div>
                        <div class="info-badge">
                            <i class="fas fa-layer-group me-2"></i>
                            Cluster: {{ cluster }}
                        </div>
                    </div>
                    <div class="col-md-4 text-end">
                        <div class="mb-3">
                            <span class="status-indicator status-{{ status_class }}">
                                <i class="fas fa-circle me-2" style="font-size: 0.5rem;"></i>
                                {{ status }}
                            </span>
                        </div>
                        <a href="/site/" class="back-btn">
                            <i class="fas fa-arrow-left me-2"></i>Back to Sites
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Main Content -->
    <div class="container">
        <!-- Project Progress Section -->
        <div class="row mb-4">
            <div class="col-12">
                <h2 class="section-title">
                    <div class="section-icon">
                        <i class="fas fa-tasks"></i>
                    </div>
                    Project Progress
                </h2>
            </div>
        </div>
        
        <div class="row mb-4">
            <div class="col-lg-3 col-md-6">
                <div class="metric-card">
                    <div class="metric-value">{{ total_quantity_given }}</div>
                    <div class="metric-label">Total Quantity Given</div>
                    <div class="metric-sublabel">MT allocated for remediation</div>
                </div>
            </div>
            <div class="col-lg-3 col-md-6">
                <div class="metric-card">
                    <div class="metric-value">{{ total_remediated }}</div>
                    <div class="metric-label">Total Remediated</div>
                    <div class="metric-sublabel">MT processed to date</div>
                </div>
            </div>
            <div class="col-lg-3 col-md-6">
                <div class="metric-card text-center">
                    <div class="progress-circle mx-auto mb-3">
                        <svg class="progress-ring" viewBox="0 0 100 100">
                            <defs>
                                <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                                    <stop offset="0%" style="stop-color:#eb9534;stop-opacity:1" />
                                    <stop offset="100%" style="stop-color:#DD6B20;stop-opacity:1" />
                                </linearGradient>
                            </defs>
                            <circle class="progress-ring-bg" cx="50" cy="50" r="45"></circle>
                            <circle class="progress-ring-fill" cx="50" cy="50" r="45" 
                                    style="stroke-dashoffset: {{ progress_offset }};"></circle>
                        </svg>
                        <div class="progress-text">{{ completion_percentage }}%</div>
                    </div>
                    <div class="metric-label">Completion Rate</div>
                </div>
            </div>
            <div class="col-lg-3 col-md-6">
                <div class="metric-card">
                    <div class="metric-value">{{ target_quantity_per_day }} MT</div>
                    <div class="metric-label">Target Per Day</div>
                    <div class="metric-sublabel">Daily quantity target</div>
                </div>
            </div>
        </div>

        <!-- Daily Operations Section -->
        <div class="row mb-4">
            <div class="col-12">
                <h2 class="section-title">
                    <div class="section-icon">
                        <i class="fas fa-chart-line"></i>
                    </div>
                    Today's Operations
                </h2>
            </div>
        </div>

        <div class="stats-grid">
            <div class="metric-card">
                <div class="metric-value">{{ total_trips }}</div>
                <div class="metric-label">Total Trips Today</div>
                <div class="metric-sublabel">Vehicle movements processed</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{{ total_inward }} MT</div>
                <div class="metric-label">Inward Material</div>
                <div class="metric-sublabel">Legacy/MSW received</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{{ total_outward }} MT</div>
                <div class="metric-label">Outward Material</div>
                <div class="metric-sublabel">Processed material dispatched</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{{ total_net_weight }} MT</div>
                <div class="metric-label">Total Weight Processed</div>
                <div class="metric-sublabel">{{ avg_weight_per_trip }} MT average per trip</div>
            </div>
        </div>

        <div class="row">
            <!-- Material Breakdown -->
            <div class="col-lg-6 mb-4">
                <h3 class="section-title">
                    <div class="section-icon">
                        <i class="fas fa-chart-pie"></i>
                    </div>
                    Material Analysis
                </h3>
                
                <div class="metric-card">
                    <!-- Material breakdown content first -->
                    
                    <!-- Inward/Outward flow moved to bottom -->
                    <div class="row mt-4">
                        <div class="col-6">
                            <div class="text-center">
                                <div class="h4 text-success mb-1">{{ inward_percentage }}%</div>
                                <div class="small text-muted">Inward Flow</div>
                            </div>
                        </div>
                        <div class="col-6">
                            <div class="text-center">
                                <div class="h4 text-info mb-1">{{ outward_percentage }}%</div>
                                <div class="small text-muted">Outward Flow</div>
                            </div>
                        </div>
                    </div>
                </div>

            <!-- Recent Vehicles -->
            <div class="col-lg-6 mb-4">
                <h3 class="section-title">
                    <div class="section-icon">
                        <i class="fas fa-truck"></i>
                    </div>
                    Recent Vehicles
                </h3>
                
                <div style="max-height: 500px; overflow-y: auto;">
                    {{ recent_vehicles_html }}
                </div>
            </div>
        </div>

        <!-- Alerts Section -->
        {{ alerts_html }}

        <!-- System Info -->
        <div class="row mb-4">
            <div class="col-12">
                <div class="metric-card">
                    <div class="row text-center">
                        <div class="col-md-3">
                            <i class="fas fa-database fa-2x text-info mb-2 d-block"></i>
                            <div class="fw-bold">{{ todays_record_count }}</div>
                            <small class="text-muted">Records Today</small>
                        </div>
                        <div class="col-md-3">
                            <i class="fas fa-clock fa-2x text-warning mb-2 d-block"></i>
                            <div class="fw-bold">{{ last_updated }}</div>
                            <small class="text-muted">Last Updated</small>
                        </div>
                        <div class="col-md-3">
                            <i class="fas fa-calendar fa-2x text-success mb-2 d-block"></i>
                            <div class="fw-bold">{{ target_date }}</div>
                            <small class="text-muted">Data Date</small>
                        </div>
                        <div class="col-md-3">
                            <i class="fas fa-server fa-2x text-primary mb-2 d-block"></i>
                            <div class="fw-bold">{{ total_historical_records }}</div>
                            <small class="text-muted">Total Records</small>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Scripts -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Auto-refresh data every 5 minutes
        setInterval(refreshData, 300000);
        
        function refreshData() {
            console.log('Refreshing dashboard data...');
            fetch('/site/{{ site_name }}/api/data')
                .then(response => response.json())
                .then(data => {
                    updateDashboard(data);
                    console.log('Data refreshed successfully');
                })
                .catch(error => {
                    console.error('Error refreshing data:', error);
                });
        }
        
        function updateDashboard(data) {
            // Update progress circle
            const completionPercentage = data.completion_percentage || 0;
            const progressFill = document.querySelector('.progress-ring-fill');
            if (progressFill) {
                const offset = 283 - (283 * completionPercentage / 100);
                progressFill.style.strokeDashoffset = offset;
            }
            
            const progressText = document.querySelector('.progress-text');
            if (progressText) {
                progressText.textContent = completionPercentage.toFixed(1) + '%';
            }
        }
        
        // Add smooth scroll and interaction effects
        document.addEventListener('DOMContentLoaded', function() {
            // Animate progress circle on load
            setTimeout(() => {
                const progressFill = document.querySelector('.progress-ring-fill');
                if (progressFill) {
                    progressFill.style.transition = 'stroke-dashoffset 2s ease-in-out';
                }
            }, 500);
            
            // Add hover effects for cards
            document.querySelectorAll('.metric-card').forEach(card => {
                card.addEventListener('mouseenter', function() {
                    this.style.transform = 'translateY(-4px)';
                });
                
                card.addEventListener('mouseleave', function() {
                    this.style.transform = 'translateY(0)';
                });
            });
        });
    </script>
</body>
</html>'''
        
        # Helper functions to format dynamic content
        def format_material_breakdown():
            material_breakdown = site_data.get('material_breakdown', {})
            if not material_breakdown:
                return '''
                <div class="text-center text-muted py-4">
                    <i class="fas fa-inbox fa-2x mb-3 d-block"></i>
                    No material data available
                </div>
                '''
            
            items = []
            for material, data in material_breakdown.items():
                items.append(f'''
                <div class="material-item">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <div class="fw-semibold">{material}</div>
                            <small class="text-muted">{data.get("count", 0)} trips</small>
                        </div>
                        <div class="text-end">
                            <div class="fw-bold">{(data.get("weight", 0)/1000):.1f} MT</div>
                        </div>
                    </div>
                </div>
                ''')
            return ''.join(items)
        
        def format_recent_vehicles():
            recent_vehicles = site_data.get('recent_vehicles', [])
            if not recent_vehicles:
                return '''
                <div class="text-center text-muted py-4">
                    <i class="fas fa-road fa-2x mb-3 d-block"></i>
                    No recent vehicle activity
                </div>
                '''
            
            vehicles = []
            for vehicle in recent_vehicles:
                vehicles.append(f'''
                <div class="vehicle-card">
                    <div class="d-flex justify-content-between align-items-start">
                        <div>
                            <div class="fw-semibold mb-1">{vehicle.get("vehicle_no", "N/A")}</div>
                            <div class="small text-muted">Ticket: {vehicle.get("ticket_no", "N/A")}</div>
                            <div class="small text-info">{vehicle.get("time", "N/A")}</div>
                        </div>
                        <div class="text-end">
                            <div class="fw-bold">{(vehicle.get("weight", 0)/1000):.1f} MT</div>
                            <span class="badge" style="background: var(--primary-gradient); font-size: 0.7rem;">
                                {vehicle.get("material", "N/A")}
                            </span>
                        </div>
                    </div>
                </div>
                ''')
            return ''.join(vehicles)
        
        def format_alerts():
            alerts = site_data.get('alerts', [])
            if not alerts:
                return ''
            
            alert_items = ''.join([f'<div class="alert-card">{alert}</div>' for alert in alerts])
            return f'''
            <div class="row mb-4">
                <div class="col-12">
                    <h3 class="section-title">
                        <div class="section-icon">
                            <i class="fas fa-bell"></i>
                        </div>
                        System Status
                    </h3>
                    {alert_items}
                </div>
            </div>
            '''
        
        # Prepare template data with safe defaults
        template_data = {
            'site_name': site_name.title(),
            'contractor': site_data.get('contractor', 'Not specified'),
            'cluster': site_data.get('cluster', 'Not specified'),
            'status': site_data.get('status', 'Unknown'),
            'status_class': 'active' if site_data.get('status') == 'Active' else 'inactive',
            'total_quantity_given': f"{site_data.get('total_quantity_given', 0):,}",
            'total_remediated': f"{site_data.get('total_remediated', 0):,}",
            'completion_percentage': f"{site_data.get('completion_percentage', 0):.1f}",
            'progress_offset': site_data.get('progress_offset', 283),
            'target_quantity_per_day': f"{site_data.get('target_quantity_per_day', 0):.1f}",
            'total_trips': site_data.get('total_trips', 0),
            'total_inward': site_data.get('total_inward', 0),
            'total_outward': site_data.get('total_outward', 0),
            'total_net_weight': site_data.get('total_net_weight', 0),
            'avg_weight_per_trip': site_data.get('avg_weight_per_trip', 0),
            'inward_percentage': f"{site_data.get('inward_percentage', 0):.1f}",
            'outward_percentage': f"{site_data.get('outward_percentage', 0):.1f}",
            'todays_record_count': site_data.get('todays_record_count', 0),
            'last_updated': site_data.get('last_updated', 'Unknown'),
            'target_date': target_date,
            'total_historical_records': site_data.get('total_historical_records', 0),
            'material_breakdown_html': format_material_breakdown(),
            'recent_vehicles_html': format_recent_vehicles(),
            'alerts_html': format_alerts(),
        }
        
        # Simple template replacement
        html_content = html_template
        for key, value in template_data.items():
            placeholder = f'{{{{ {key} }}}}'
            html_content = html_content.replace(placeholder, str(value))
        
        response = flask.make_response(html_content)
        response.headers['Content-Type'] = 'text/html; charset=utf-8'
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        
        print(f"RETURNING BEAUTIFUL UI HTML FOR: {site_name}")
        return response
        
    except Exception as e:
        print(f"ERROR loading site data for {site_name}: {e}")
        print(f"TRACEBACK: {traceback.format_exc()}")
        return f"""
        <html><body style="padding: 2rem; font-family: monospace;">
            <h1>Error Loading Site Data</h1>
            <p><strong>Site:</strong> {site_name}</p>
            <p><strong>Error:</strong> {str(e)}</p>
            <p><a href="/site/">â† Back to Site List</a></p>
            <pre>{traceback.format_exc()}</pre>
        </body></html>
        """, 500

# API endpoints should be handled by your site_dashboard blueprint
# Make sure your blueprint is registered AFTER these routes
# so that /site/<name>/api/data goes to the blueprint, not the catch-all above

# 1. Page routing and authentication
# Find your route_and_authenticate function and add this case

@callback(
    [Output('current-page', 'data'),
     Output('user-authenticated', 'data'), 
     Output('user-session-data', 'data'),
     Output('auth-error-message', 'data')],
    [Input('url', 'pathname'), Input('url', 'search')],
    prevent_initial_call=False
)
def route_and_authenticate(pathname, search):
    """Core routing - FIXED: Flask routes get priority"""
    if pathname:
        pathname = urllib.parse.unquote(pathname)
    
    print(f"ROUTE DEBUG: {pathname}")
    
    # CRITICAL: Let Flask handle these routes completely
    flask_prefixes = ['/site/', '/legacy/', '/oauth/', '/debug/', '/test/', '/api/', '/_ah/', '/dashboard/csv-', '/dashboard/filtered-']
    
    if pathname and any(pathname.startswith(prefix) for prefix in flask_prefixes):
        print(f"FLASK ROUTE: {pathname} - Dash will not interfere")
        raise PreventUpdate
    
    # Handle logout
    params = {}
    if search:
        params = dict(urllib.parse.parse_qsl(search.lstrip('?')))
    
    if params.get('logout') == 'true':
        flask.session.clear()
        return 'public_landing', False, {}, 'Logged out successfully.'
    
    # Session check
    session_id = flask.session.get('swaccha_session_id')
    user_data = flask.session.get('user_data', {})
    is_authenticated = bool(session_id)
    
    # Dash-only routes
    if not pathname or pathname == '/':
        return 'public_landing', is_authenticated, user_data, ''
    elif pathname == '/login':
        return 'login', is_authenticated, user_data, params.get('error', '')
    elif pathname == '/dashboard':
        if is_authenticated:
            return 'admin_dashboard', True, user_data, ''
        else:
            return 'unauthorized_access', False, {}, 'Please log in.'
    else:
        return 'public_landing', is_authenticated, user_data, ''
    

@callback(
    Output('main-layout', 'children'),
    [Input('current-theme', 'data'),
     Input('user-authenticated', 'data'),
     Input('current-page', 'data'),
     Input('user-session-data', 'data'),
     Input('auth-error-message', 'data')]
)
def render_layout(theme_name, is_authenticated, current_page, user_data, error_message):
    """Render appropriate layout - FIXED: No site_redirect"""
    theme_name = theme_name or DEFAULT_THEME
    is_authenticated = bool(is_authenticated)
    current_page = current_page or 'public_landing'
    user_data = user_data or {}
    error_message = error_message or ''
    
    print(f"DEBUG: Rendering layout - page: {current_page}, theme: {theme_name}, authenticated: {is_authenticated}")
    
    try:
        # REMOVED: No more site_redirect handling - Flask handles site routes directly
        
        if current_page == 'login':
            layout = build_login_layout(theme_name, error_message)
            print("DEBUG: Login layout rendered")
            return layout
        elif current_page == 'unauthorized_access':
            layout = create_unauthorized_layout(theme_name)
            return layout
        elif current_page == 'admin_dashboard' and is_authenticated:
            layout = build_enhanced_dashboard(theme_name, user_data)
            return layout
        else:
            # Default to public layout
            layout = build_public_layout(theme_name, is_authenticated, user_data)
            return layout
    except Exception as e:
        print(f"ERROR: Layout build failed: {e}")
        return build_public_layout(DEFAULT_THEME, False, {})

# 3. MOST IMPORTANT: Update the Flask routes in admin_dashboard.py to check access:

# In admin_dashboard.py, update these routes:

# 4. Basic navigation
@callback(
    Output('url', 'pathname'),
    [Input('admin-login-btn', 'n_clicks'),
     Input('overlay-nav-overview', 'n_clicks'),
     Input('overlay-nav-analytics', 'n_clicks'),
     Input('overlay-nav-reports', 'n_clicks')],
    prevent_initial_call=True
)
def handle_navigation(login_clicks, overview_clicks, analytics_clicks, reports_clicks):
    """Handle basic navigation - FIXED to clear logout parameter"""
    if not ctx.triggered:
        raise PreventUpdate
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if ctx.triggered[0]['value'] in [None, 0]:
        raise PreventUpdate
    
    print(f"DEBUG: Navigation button clicked: {button_id}")
    
    routes = {
        'admin-login-btn': '/login',
        'overlay-nav-overview': '/',
        'overlay-nav-analytics': '/analytics', 
        'overlay-nav-reports': '/reports'
    }
    return routes.get(button_id, '/')

def setup_site_dashboard(server):
    """Setup site dashboard with Bootstrap"""
    
    # Register the blueprint
    server.register_blueprint(site_dashboard_bp)
    
    print("Site Dashboard Blueprint registered")
    print(" Available routes:")
    print("   - Site List: http://localhost:8050/site/")
    print("   - Site Dashboard: http://localhost:8050/site/{site_name}")
    print("   - Site Analytics: http://localhost:8050/site/{site_name}/analytics")

# Add these routes to your main.py for debugging

@server.route('/_ah/health')
def health_check():
    """App Engine health check"""
    return {'status': 'healthy', 'timestamp': time.time()}, 200

@server.route('/debug/routes')
def debug_routes():
    """Show all registered Flask routes"""
    routes = []
    for rule in server.url_map.iter_rules():
        routes.append({
            'endpoint': rule.endpoint,
            'methods': list(rule.methods),
            'rule': str(rule),
            'blueprint': getattr(rule, 'blueprint', None)
        })
    return flask.jsonify({
        'total_routes': len(routes),
        'routes': routes,
        'blueprints': list(server.blueprints.keys()),
        'environment': os.getenv('GAE_ENV', 'local')
    })

@server.route('/test/routing')
def test_routing():
    """Test if Flask routing is working"""
    return flask.jsonify({
        'message': 'Flask routing is working!',
        'request_url': flask.request.url,
        'request_path': flask.request.path,
        'method': flask.request.method,
        'host': flask.request.host,
        'environment': os.getenv('GAE_ENV', 'local')
    })

@server.route('/test/site-redirect')
def test_site_redirect():
    """Test redirect to site route"""
    return flask.redirect('/site/visag')

# Add logging to see what's happening with routes
@server.before_request
def log_request():
    """Log every request for debugging"""
    print(f"REQUEST: {flask.request.method} {flask.request.url}")
    print(f"PATH: {flask.request.path}")
    print(f"ENDPOINT: {flask.request.endpoint}")

@server.after_request  
def log_response(response):
    """Log response info"""
    print(f"RESPONSE: {response.status_code} for {flask.request.path}")
    return response

def setup_legacy_report(server):
    """Setup legacy report with Bootstrap"""
    
    # Initialize Bootstrap
    bootstrap = Bootstrap(server)
    
    # Register the blueprint
    server.register_blueprint(legacy_bp)
    
    # Add route redirect from your existing /legacy-report
    @server.route('/legacy-report')
    def legacy_report_redirect():
        """Simple redirect to Flask dashboard"""
        if not session.get('swaccha_session_id'):
            return redirect('/login')
        return redirect('/legacy/report')
    
    print("Ã¢Å“â€¦ Legacy Report Blueprint registered")
    print("Ã¢Å“â€¦ Bootstrap initialized")
    print("Ã°Å¸â€œÅ  Available at: /legacy/report")

def start_streamlit_server():
    """Start Streamlit server in background thread"""
    try:
        # Start Streamlit on port 8051
        subprocess.Popen([
            "streamlit", "run", "legacy_report.py", 
            "--server.port=8051", 
            "--server.headless=true",
            "--server.address=0.0.0.0",
            "--server.enableCORS=false"
        ])
        print("Ã¢Å“â€¦ Streamlit legacy-report started on http://localhost:8051")
    except Exception as e:
        print(f"Ã¢ÂÅ’ Failed to start Streamlit: {e}")

@callback(
    Output('url', 'pathname', allow_duplicate=True),
    [Input('magic-view-go-btn', 'n_clicks')],
    [State('site-selector-dropdown', 'value')],
    prevent_initial_call=True
)
def navigate_to_site_dashboard(n_clicks, selected_site):
    """Navigate to Flask site dashboard"""
    if not n_clicks or not selected_site:
        raise PreventUpdate
    
    # Redirect to Flask route instead of Dash
    return f'/site/{selected_site}'

@callback(
    Output('main-layout', 'children', allow_duplicate=True),
    [Input('username-password-login-btn', 'n_clicks'),
     Input('demo-login-btn', 'n_clicks')],
    [State('username-input', 'value'),
     State('password-input', 'value')],
    prevent_initial_call=True
)
def handle_login_with_refresh(username_clicks, demo_clicks, username, password):
    """Handle login and force page refresh on success"""
    if not ctx.triggered:
        raise PreventUpdate
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    triggered_value = ctx.triggered[0]['value']
    
    if triggered_value in [None, 0]:
        raise PreventUpdate
    
    print(f"DEBUG: Login attempt - {button_id}")
    
    # USERNAME/PASSWORD LOGIN
    if button_id == 'username-password-login-btn':
        if not username or not password:
            print("DEBUG: Missing credentials")
            # Show error message
            return html.Div([
                html.Div("Ã¢ÂÅ’ Please enter both username and password", 
                        style={'color': 'red', 'textAlign': 'center', 'padding': '1rem'}),
                build_login_layout(DEFAULT_THEME, 'missing_credentials')
            ])
        
        if validate_user_credentials(username, password):
            role = get_user_role_by_username(username)
            create_demo_session(username, f"User {username}", role)
            print(f"DEBUG: Login successful for {username} - REFRESHING PAGE")
            
            # Return success page with immediate refresh
            return html.Div([
                html.Div([
                    html.H1("Ã¢Å“â€¦ Login Successful!", 
                           style={'color': 'green', 'textAlign': 'center', 'marginBottom': '1rem'}),
                    html.P(f"Welcome, {username}!", 
                           style={'textAlign': 'center', 'fontSize': '1.2rem', 'marginBottom': '1rem'}),
                    html.P("Loading your dashboard...", 
                           style={'textAlign': 'center', 'marginBottom': '2rem'}),
                    html.Div("Ã°Å¸â€â€ž", style={'textAlign': 'center', 'fontSize': '3rem'})
                ], style={
                    'padding': '3rem',
                    'backgroundColor': '#f0f9ff',
                    'borderRadius': '12px',
                    'margin': '2rem auto',
                    'maxWidth': '500px',
                    'border': '2px solid green'
                }),
                # FORCE IMMEDIATE PAGE REFRESH
                dcc.Location(id='success-redirect', refresh=True, href='/legacy/report')
            ])
        else:
            print(f"DEBUG: Invalid credentials for {username}")
            return html.Div([
                html.Div("Ã¢ÂÅ’ Invalid username or password", 
                        style={'color': 'red', 'textAlign': 'center', 'padding': '1rem'}),
                build_login_layout(DEFAULT_THEME, 'invalid_credentials')
            ])
    
    # DEMO LOGIN
    elif button_id == 'demo-login-btn':
        create_demo_session('demo_user', 'Demo User', 'administrator')
        print("DEBUG: Demo login successful - REFRESHING PAGE")
        
        return html.Div([
            html.Div([
                html.H1("Ã¢Å“â€¦ Demo Login Successful!", 
                       style={'color': 'green', 'textAlign': 'center', 'marginBottom': '1rem'}),
                html.P("Welcome, Demo User!", 
                       style={'textAlign': 'center', 'fontSize': '1.2rem', 'marginBottom': '1rem'}),
                html.P("Loading legacy report dashboard...", 
                       style={'textAlign': 'center', 'marginBottom': '2rem'}),
                html.Div("Ã°Å¸â€â€ž", style={'textAlign': 'center', 'fontSize': '3rem'})
            ], style={
                'padding': '3rem',
                'backgroundColor': '#f0f9ff',
                'borderRadius': '12px',
                'margin': '2rem auto',
                'maxWidth': '500px',
                'border': '2px solid green'
            }),
            # FORCE IMMEDIATE PAGE REFRESH
            dcc.Location(id='demo-success-redirect', refresh=True, href='/legacy/report')
        ])
    
    raise PreventUpdate


# ALTERNATIVE: Even simpler with just JavaScript
@callback(
    Output('login-redirect-script', 'children'),
    [Input('username-password-login-btn', 'n_clicks'),
     Input('demo-login-btn', 'n_clicks')],
    [State('username-input', 'value'),
     State('password-input', 'value')],
    prevent_initial_call=True
)
def login_and_redirect(username_clicks, demo_clicks, username, password):
    """Validate login and return JavaScript redirect"""
    if not ctx.triggered:
        raise PreventUpdate
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # USERNAME/PASSWORD LOGIN
    if button_id == 'username-password-login-btn':
        if username and password and validate_user_credentials(username, password):
            role = get_user_role_by_username(username)
            create_demo_session(username, f"User {username}", role)
            print(f"DEBUG: Login successful, executing redirect script")
            # Return JavaScript that immediately redirects
            return html.Script("window.location.href = '/legacy/report';")
    
    # DEMO LOGIN
    elif button_id == 'demo-login-btn':
        create_demo_session('demo_user', 'Demo User', 'administrator')
        print("DEBUG: Demo login successful, executing redirect script")
        return html.Script("window.location.href = '/legacy/report';")
    
    return ""

def create_logout_success_handler():
    """Create component to handle logout success"""
    return html.Div([
        html.Div(id='logout-success-message', style={'display': 'none'}),
        html.Script("""
            // Check for logout success in URL
            const urlParams = new URLSearchParams(window.location.search);
            if (urlParams.get('logout') === 'success') {
                // Show success message
                const successDiv = document.createElement('div');
                successDiv.innerHTML = `
                    <div class="alert alert-success alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3" 
                         style="z-index: 9999; max-width: 400px;">
                        <div class="d-flex align-items-center">
                            <i class="fas fa-check-circle me-2 text-success"></i>
                            <div>
                                <strong>Logged out successfully!</strong>
                                <br><small>Welcome back to the main page</small>
                            </div>
                        </div>
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                `;
                document.body.appendChild(successDiv);
                
                // Auto-remove after 5 seconds
                setTimeout(function() {
                    if (successDiv.parentNode) {
                        successDiv.remove();
                    }
                }, 5000);
                
                // Clean URL (remove logout parameter)
                const newUrl = window.location.href.split('?')[0];
                window.history.replaceState({}, document.title, newUrl);
            }
        """)
    ])
# 5. Login actions - NO GOOGLE OAUTH OR LOGOUT (handled by JavaScript)
@callback(
    Output('url', 'pathname', allow_duplicate=True),
    [Input('demo-login-btn', 'n_clicks'),
     Input('admin-account-btn', 'n_clicks'),
     Input('dev-account-btn', 'n_clicks'),
     Input('viewer-account-btn', 'n_clicks'),
     Input('pin-login-btn', 'n_clicks'),
     Input('manual-login-btn', 'n_clicks'),
     Input('username-password-login-btn', 'n_clicks'),
     Input('back-to-public-btn', 'n_clicks')],
    [State('access-pin', 'value'),
     State('manual-email', 'value'),
     State('username-input', 'value'),
     State('password-input', 'value'),
     State('current-page', 'data'),
     State('url', 'pathname')],  # Ã¢Å“â€¦ ADD: Current pathname to prevent loops
    prevent_initial_call=True
)
def handle_login_actions_enhanced(demo_clicks, admin_clicks, dev_clicks, 
                                viewer_clicks, pin_clicks, manual_clicks, 
                                username_password_clicks, back_clicks,
                                access_pin, manual_email, username, password,
                                current_page, current_pathname):  # Ã¢Å“â€¦ ADD: current_pathname
    """Handle all login actions with DIRECT redirect to Flask route - FIXED to prevent loops"""
    if not ctx.triggered or current_page != 'login':
        raise PreventUpdate
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    triggered_value = ctx.triggered[0]['value']
    
    if triggered_value in [None, 0]:
        raise PreventUpdate
    
    # Ã¢Å“â€¦ PREVENT LOOPS: Check if already on target page
    if current_pathname == '/legacy/report':
        print("DEBUG: Already on legacy report page, preventing loop")
        raise PreventUpdate
    
    print(f"DEBUG: Enhanced login action - {button_id} (value: {triggered_value})")
    
    # Ã¢Å“â€¦ ADD: Debouncing - only process if click count is reasonable
    if triggered_value > 10:  # Prevent excessive clicking
        print("DEBUG: Too many clicks detected, ignoring")
        raise PreventUpdate
    
    # Navigation
    if button_id == 'back-to-public-btn':
        return '/'
    
    # Ã¢Å“â€¦ USERNAME/PASSWORD LOGIN
    elif button_id == 'username-password-login-btn':
        if not username or not password:
            print("DEBUG: Missing credentials")
            return '/login?error=missing_credentials'
        
        if validate_user_credentials(username, password):
            role = get_user_role_by_username(username)
            create_demo_session(username, f"User {username}", role)
            print(f"DEBUG: Username/password login successful for {username} Ã¢â€ â€™ REDIRECTING to /legacy/report")
            return '/legacy/report'
        else:
            print(f"DEBUG: Invalid credentials for {username}")
            return '/login?error=invalid_credentials'
    
    # Ã¢Å“â€¦ OTHER LOGIN METHODS
    elif button_id == 'demo-login-btn':
        create_demo_session('demo_user', 'Demo User', 'administrator')
        print("DEBUG: Demo login successful Ã¢â€ â€™ REDIRECTING to /legacy/report")
        return '/legacy/report'
    
    elif button_id == 'admin-account-btn':
        create_demo_session('admin', 'Administrator', 'administrator')
        print("DEBUG: Admin login successful Ã¢â€ â€™ REDIRECTING to /legacy/report")
        return '/legacy/report'
    
    elif button_id == 'dev-account-btn':
        create_demo_session('developer', 'Developer', 'administrator')
        print("DEBUG: Developer login successful Ã¢â€ â€™ REDIRECTING to /legacy/report")
        return '/legacy/report'
    
    elif button_id == 'viewer-account-btn':
        create_demo_session('viewer', 'Viewer', 'viewer')
        print("DEBUG: Viewer login successful Ã¢â€ â€™ REDIRECTING to /legacy/report")
        return '/legacy/report'
    
    elif button_id == 'pin-login-btn':
        pins = {
            '1234': ('admin', 'PIN Admin', 'administrator'),
            '5678': ('dev', 'PIN Developer', 'administrator'),
            '9999': ('demo', 'PIN Demo', 'viewer')
        }
        if access_pin in pins:
            user_id, name, role = pins[access_pin]
            create_demo_session(user_id, name, role)
            print(f"DEBUG: PIN login successful for {name} Ã¢â€ â€™ REDIRECTING to /legacy/report")
            return '/legacy/report'
        else:
            return '/login?error=invalid_pin'
    
    elif button_id == 'manual-login-btn':
        if manual_email and '@' in manual_email:
            role = 'administrator' if 'swaccha' in manual_email.lower() else 'viewer'
            create_demo_session('manual_user', f'User ({manual_email})', role)
            print(f"DEBUG: Email login successful for {manual_email} Ã¢â€ â€™ REDIRECTING to /legacy/report")
            handle_login_with_refresh
        else:
            return '/login?error=invalid_email'
    
    raise PreventUpdate

app.clientside_callback(
    """
    function(n_clicks) {
        // Disable button for 2 seconds after click to prevent rapid clicking
        if (n_clicks > 0) {
            const btn = document.getElementById('username-password-login-btn');
            if (btn) {
                btn.disabled = true;
                btn.style.opacity = '0.6';
                setTimeout(() => {
                    btn.disabled = false;
                    btn.style.opacity = '1';
                }, 2000);
            }
        }
        return window.dash_clientside.no_update;
    }
    """,
    Output('username-input', 'style'),  # Dummy output
    Input('username-password-login-btn', 'n_clicks'),
    prevent_initial_call=True
)


def validate_user_credentials(username, password):
    """
    Validate username/password credentials
    
    Args:
        username (str): Username
        password (str): Password
        
    Returns:
        bool: True if valid credentials
    """
    # Default credentials for demo
    valid_credentials = {
        'admin': 'password',
        'administrator': 'admin123',
        'demo': 'demo123',
        'user': 'user123'
    }
    
    return username in valid_credentials and valid_credentials[username] == password

def get_user_role_by_username(username):
    """
    Get user role based on username
    
    Args:
        username (str): Username
        
    Returns:
        str: User role
    """
    admin_users = ['admin', 'administrator', 'swaccha']
    
    if username in admin_users:
        return 'administrator'
    else:
        return 'viewer'
    

error_messages = {
    'oauth_not_available': 'Google OAuth not configured. Use demo login.',
    'oauth_failed': 'OAuth setup failed. Use demo login.',
    'unauthorized': 'You are not authorized. Contact administrator.',
    'invalid_pin': 'Invalid PIN. Try: 1234, 5678, or 9999',
    'missing_credentials': 'Please enter both username and password.',    # Ã¢Å“â€¦ ADD
    'invalid_credentials': 'Invalid username or password. Try: admin/password'  # Ã¢Å“â€¦ ADD
}

# 6. Admin dashboard actions - NO LOGOUT (handled by JavaScript)
@callback(
    Output('url', 'pathname', allow_duplicate=True),
    [Input('quick-reports-btn', 'n_clicks'),
     Input('quick-settings-btn', 'n_clicks')],
    [State('current-page', 'data'),
     State('user-authenticated', 'data')],
    prevent_initial_call=True
)
def handle_admin_actions(reports_clicks, settings_clicks, current_page, is_authenticated):
    """Handle admin dashboard actions - logout handled by JavaScript"""
    if not ctx.triggered:
        raise PreventUpdate
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if ctx.triggered[0]['value'] in [None, 0]:
        raise PreventUpdate
    
    print(f"DEBUG: Admin action triggered - {button_id}")
    
    if button_id == 'quick-reports-btn' and is_authenticated:
        return '/reports'
    elif button_id == 'quick-settings-btn' and is_authenticated:
        return '/settings'
    
    raise PreventUpdate

# 7. Placeholder navigation
@callback(
    Output('url', 'pathname', allow_duplicate=True),
    [Input('back-to-dashboard-btn', 'n_clicks')],
    [State('current-page', 'data'),
     State('user-authenticated', 'data')],
    prevent_initial_call=True
)
def handle_placeholder_nav(back_clicks, current_page, is_authenticated):
    """Handle placeholder page navigation"""
    if (not is_authenticated or 
        current_page not in ['analytics_page', 'reports_page'] or 
        not ctx.triggered):
        raise PreventUpdate
    
    if ctx.triggered[0]['value'] in [None, 0]:
        raise PreventUpdate
    
    return '/dashboard'

# 8. Unauthorized access callbacks

# Countdown display callback
@callback(
    Output('countdown-display', 'children'),
    [Input('unauthorized-countdown-timer', 'n_intervals')],
    [State('current-page', 'data')],
    prevent_initial_call=True
)
def update_countdown_display(n_intervals, current_page):
    """Update countdown display"""
    if current_page != 'unauthorized_access':
        raise PreventUpdate
    
    remaining_seconds = 5 - n_intervals
    if remaining_seconds <= 0:
        return "0"
    return str(remaining_seconds)

def kadapa_rayachoti_layout():
    """Enhanced dashboard for Kadapa Rayachoti with interactive elements"""
    return html.Div([
        # Header Section with Gradient
        html.Div([
            html.Div([
                html.H1("Tharuni Associates", className="header-title"),
                html.H2("Kadapa - Rayachoti", className="header-subtitle"),
                html.P("Remediation Progress Dashboard", className="header-description")
            ], className="header-content")
        ], className="header-section"),
        
        # Cards Grid with Interactive Cards
        html.Div([
            # Card 1 - Machine Capacity
            html.Div([
                html.Div("Ã¢Å¡â„¢Ã¯Â¸Â", className="card-icon"),
                html.Div("Machine Capacity", className="card-title"),
                html.Div("1,200 MT/day", className="card-value"),
                html.Div("Daily processing capability", className="card-description")
            ], className="metric-card", id="card-machine", n_clicks=0),
            
            # Card 2 - Given Quantity
            html.Div([
                html.Div("Ã°Å¸â€œÂ¦", className="card-icon"),
                html.Div("Given Quantity", className="card-title"),
                html.Div("94,604 MT", className="card-value"),
                html.Div("Total material to process", className="card-description")
            ], className="metric-card", id="card-given", n_clicks=0),
            
            # Card 3 - Cumulative
            html.Div([
                html.Div("Ã°Å¸â€œÅ ", className="card-icon"),
                html.Div("Cumulative", className="card-title"),
                html.Div("31,344 MT", className="card-value"),
                html.Div("Processed to date", className="card-description")
            ], className="metric-card", id="card-cumulative", n_clicks=0),
            
            # Card 4 - Remaining
            html.Div([
                html.Div("Ã¢ÂÂ³", className="card-icon"),
                html.Div("Remaining", className="card-title"),
                html.Div("63,260 MT", className="card-value"),
                html.Div("Material left to process", className="card-description")
            ], className="metric-card", id="card-remaining", n_clicks=0),
            
            # Card 5 - Yesterday's Processing
            html.Div([
                html.Div("Ã°Å¸â€œâ€¦", className="card-icon"),
                html.Div("Processed Yesterday", className="card-title"),
                html.Div("1,564 MT", className="card-value"),
                html.Div("Previous day's progress", className="card-description")
            ], className="metric-card", id="card-yesterday", n_clicks=0)
        ], className="cards-grid")
    ], className="dashboard-container")

# Enhanced CSS with colorful header text
ENHANCED_DASHBOARD_CSS = """
/* Base Styles */
.dashboard-container {
    font-family: 'Segoe UI', Roboto, -apple-system, sans-serif;
    max-width: 100%;
    padding: 0;
    margin: 0;
    color: #333;
    line-height: 1.6;
    background: #f8fafc;
    min-height: 100vh;
}

/* Header Section with Gradient */
.header-section {
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
    padding: 2rem 1rem;
    text-align: center;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}

.header-content {
    max-width: 800px;
    margin: 0 auto;
}

.header-title {
    margin: 0;
    font-size: 2rem;
    font-weight: 700;
    letter-spacing: 0.5px;
    text-shadow: 0 2px 4px rgba(0,0,0,0.2);
    /* Gradient text effect */
    background: linear-gradient(45deg, #ffd700, #ff6b6b, #4ecdc4, #45b7d1, #96ceb4, #ffeaa7);
    background-size: 300% 300%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: gradientShift 4s ease-in-out infinite;
}

.header-subtitle {
    margin: 0.5rem 0 0;
    font-size: 1.4rem;
    font-weight: 500;
    text-shadow: 0 1px 2px rgba(0,0,0,0.1);
    /* Orange to pink gradient */
    background: linear-gradient(45deg, #ff9a56, #ff6b6b, #ffa8a8);
    background-size: 200% 200%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: gradientShift 3s ease-in-out infinite reverse;
}

.header-description {
    margin: 0.5rem auto 0;
    font-size: 0.95rem;
    max-width: 600px;
    /* Cyan to green gradient */
    background: linear-gradient(45deg, #4ecdc4, #44bd9e, #96ceb4);
    background-size: 200% 200%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: gradientShift 2.5s ease-in-out infinite;
}

/* Gradient animation keyframes */
@keyframes gradientShift {
    0%, 100% {
        background-position: 0% 50%;
    }
    50% {
        background-position: 100% 50%;
    }
}

/* Cards Grid */
.cards-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 1.5rem;
    padding: 1.5rem;
    max-width: 1200px;
    margin: 0 auto;
}

.metric-card {
    background: white;
    border-radius: 12px;
    padding: 1.8rem 1.5rem;
    box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    text-align: center;
    transition: all 0.3s ease;
    cursor: pointer;
    border: 2px solid transparent;
    position: relative;
    overflow: hidden;
}

.metric-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 15px rgba(0,0,0,0.1);
    border-color: #4f46e5;
}

.metric-card:active {
    transform: translateY(-2px);
}

.metric-card::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, #4f46e5, #7c3aed);
}

.card-icon {
    font-size: 2rem;
    margin-bottom: 1rem;
    transition: transform 0.3s ease;
}

.metric-card:hover .card-icon {
    transform: scale(1.1);
}

.card-title {
    font-size: 1.1rem;
    font-weight: 600;
    color: #4b5563;
    margin-bottom: 0.5rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.card-value {
    font-size: 2rem;
    font-weight: 700;
    color: #1f2937;
    margin: 0.5rem 0;
    transition: color 0.3s ease;
}

.metric-card:hover .card-value {
    color: #4f46e5;
}

.card-description {
    font-size: 0.9rem;
    color: #6b7280;
    margin-top: 0.5rem;
    opacity: 0.9;
}

/* Color Variations for Cards */
.metric-card:nth-child(1)::after { background: linear-gradient(90deg, #3b82f6, #60a5fa); }
.metric-card:nth-child(2)::after { background: linear-gradient(90deg, #10b981, #34d399); }
.metric-card:nth-child(3)::after { background: linear-gradient(90deg, #f59e0b, #fbbf24); }
.metric-card:nth-child(4)::after { background: linear-gradient(90deg, #ef4444, #f87171); }
.metric-card:nth-child(5)::after { background: linear-gradient(90deg, #8b5cf6, #a78bfa); }

.metric-card:nth-child(1):hover { border-color: #3b82f6; }
.metric-card:nth-child(2):hover { border-color: #10b981; }
.metric-card:nth-child(3):hover { border-color: #f59e0b; }
.metric-card:nth-child(4):hover { border-color: #ef4444; }
.metric-card:nth-child(5):hover { border-color: #8b5cf6; }

.metric-card:nth-child(1):hover .card-value { color: #3b82f6; }
.metric-card:nth-child(2):hover .card-value { color: #10b981; }
.metric-card:nth-child(3):hover .card-value { color: #f59e0b; }
.metric-card:nth-child(4):hover .card-value { color: #ef4444; }
.metric-card:nth-child(5):hover .card-value { color: #8b5cf6; }

/* Click Animation */
.metric-card.clicked {
    animation: cardClick 0.4s ease;
}

@keyframes cardClick {
    0% { transform: scale(0.98); }
    50% { transform: scale(1.02); }
    100% { transform: scale(1); }
}

/* Responsive Design */
@media (max-width: 768px) {
    .cards-grid {
        grid-template-columns: 1fr;
        gap: 1.2rem;
        padding: 1.2rem;
    }
    
    .header-title {
        font-size: 1.6rem;
    }
    
    .header-subtitle {
        font-size: 1.2rem;
    }
    
    .metric-card {
        padding: 1.5rem 1.2rem;
    }
    
    .card-value {
        font-size: 1.8rem;
    }
}

@media (max-width: 480px) {
    .header-section {
        padding: 1.5rem 1rem;
    }
    
    .header-title {
        font-size: 1.4rem;
    }
    
    .header-subtitle {
        font-size: 1.1rem;
    }
    
    .metric-card {
        padding: 1.3rem 1rem;
    }
    
    .card-icon {
        font-size: 1.8rem;
    }
    
    .card-title {
        font-size: 1rem;
    }
    
    .card-value {
        font-size: 1.6rem;
    }
}

/* Fallback for browsers that don't support background-clip: text */
@supports not (-webkit-background-clip: text) {
    .header-title {
        color: #ffd700;
    }
    
    .header-subtitle {
        color: #ff6b6b;
    }
    
    .header-description {
        color: #4ecdc4;
    }
}
"""

# JavaScript for click functionality (would be added to your Dash app)
CLICK_JS = """
// This would be part of your Dash callback
document.addEventListener('DOMContentLoaded', function() {
    const cards = document.querySelectorAll('.metric-card');
    
    cards.forEach(card => {
        card.addEventListener('click', function() {
            // Remove clicked class from all cards
            cards.forEach(c => c.classList.remove('clicked'));
            
            // Add to clicked card
            this.classList.add('clicked');
            
            // You could add additional logic here to handle the click
            console.log('Card clicked:', this.id);
        });
    });
});
"""
# Alternative method if not using Dash Pages:
# Add this to your existing callback structure

# @callback(
#     Output('page-content', 'children'),
#     Input('url', 'pathname')
# )
# def display_page(pathname):
#     if pathname == '/Kadapa/Rayachoti':
#         return layout()
#     else:
#         return your_existing_layout()

# CSS styles to add to your app
app_styles = """
table th {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: white !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    font-size: 0.7rem !important;
    letter-spacing: 0.5px !important;
    white-space: nowrap !important;
}

table tr:nth-child(even) {
    background: #f8f9fa !important;
}

table tr:hover {
    background: #e3f2fd !important;
}

@media (max-width: 480px) {
    table th, table td {
        padding: 8px 6px !important;
        font-size: 0.8rem !important;
    }
}
"""

# Add the CSS to your app (in your main.py where you initialize the Dash app)
# app.index_string = app.index_string.replace('</head>', f'<style>{app_styles}</style></head>')

# Auto-redirect callback
@callback(
    Output('url', 'pathname', allow_duplicate=True),
    [Input('unauthorized-redirect-timer', 'n_intervals')],
    [State('current-page', 'data')],
    prevent_initial_call=True
)
def auto_redirect_to_public(n_intervals, current_page):
    """Auto-redirect to public dashboard after 5 seconds"""
    if current_page != 'unauthorized_access' or n_intervals == 0:
        raise PreventUpdate
    
    print("DEBUG: Auto-redirecting to public dashboard after 5 seconds")
    return '/'

# Manual redirect callbacks
@callback(
    Output('url', 'pathname', allow_duplicate=True),
    [Input('manual-redirect-btn', 'n_clicks'),
     Input('login-redirect-btn', 'n_clicks')],
    [State('current-page', 'data')],
    prevent_initial_call=True
)
def handle_manual_redirect(manual_clicks, login_clicks, current_page):
    """Handle manual redirect buttons"""
    if current_page != 'unauthorized_access' or not ctx.triggered:
        raise PreventUpdate
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if ctx.triggered[0]['value'] in [None, 0]:
        raise PreventUpdate
    
    if button_id == 'manual-redirect-btn':
        print("DEBUG: Manual redirect to public dashboard")
        return '/'
    elif button_id == 'login-redirect-btn':
        print("DEBUG: Manual redirect to login page")
        return '/login'
    
    raise PreventUpdate


def create_demo_session(user_id, name, role):
    """Create demo session (stable)"""
    session_data = {
        'session_id': f'stable_session_{user_id}',
        'user_id': user_id,
        'email': f'{user_id}@swacchaandhra.local',
        'name': name,
        'picture': '/assets/img/default-avatar.png',
        'role': role,
        'auth_method': 'demo'
    }
    flask.session['swaccha_session_id'] = session_data['session_id']
    flask.session['user_data'] = session_data
    print(f"DEBUG: Demo session created for {name}")

# Configure upload settings and register dashboard routes

# Ã¢Å“â€¦ FIXED: Register routes WITH custom dashboard routes (no conflicts)
register_custom_dashboard_routes(server)  # Custom routes for dashboard functionality

# Ã¢Å“â€¦ KEEP: Register dashboard Flask routes (moved from main to admin_dashboard)
# This handles the /dashboard route without conflicts
# upload_dir = Path('/tmp/uploads')
# upload_dir.mkdir(exist_ok=True)
# user_upload_dir = upload_dir / 'dash_uploads'
# user_upload_dir.mkdir(exist_ok=True)

if __name__ == '__main__':
    try:
        print("Ã°Å¸Å¡â‚¬ Starting Enhanced Flask Application...")
        
        # Setup legacy report (ADD THIS LINE)
        setup_legacy_report(server)
        setup_site_dashboard(server)
        # Register existing callbacks
        logger.info("Ã¢Å“â€¦ Unified callbacks registered successfully")
        logger.info("Ã¢Å“â€¦ Simple Legacy report integrated")
        
        print("Ã°Å¸Å’Â Application URLs:")
        print("   - Main App: http://localhost:8050")
        print("   - Login: http://localhost:8050/login")
        print("   - Legacy Report: http://localhost:8050/legacy-report Ã¢â€ â€™ /legacy/report")
        print("   - Direct Access: http://localhost:8050/legacy/report")
        
        # Start the main Flask/Dash app
        app.run(debug=True, host='0.0.0.0', port=8050)
        
    except Exception as e:
        logger.error(f" Failed to start enhanced app: {e}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        # Clean up
        try:
            stop_file_monitoring()
        except:
            pass