# utils/page_builder.py
"""
Page Builder Utility
Creates themed pages with consistent layout and navigation
Used by all endpoint modules for consistent page generation
"""

from flask import session
from config.themes import get_theme

def get_user_info():
    """Get current user information from session"""
    user_info = session.get('user_data', {})
    return {
        'name': user_info.get('name', 'Administrator'),
        'role': user_info.get('role', 'administrator').replace('_', ' ').title(),
        'email': user_info.get('email', 'admin@swacchaandhra.gov.in'),
        'picture': user_info.get('picture', '/assets/img/default-avatar.png')
    }

def create_navigation_html(current_page, theme):
    """Create navigation HTML with proper active states"""
    nav_items = [
        {"id": "dashboard", "icon": "📊", "label": "Dashboard", "url": "/dashboard"},
        {"id": "analytics", "icon": "📈", "label": "Data Analytics", "url": "/data-analytics"},
        {"id": "charts", "icon": "📉", "label": "Charts", "url": "/charts"},
        {"id": "reports", "icon": "📋", "label": "Reports", "url": "/reports"},
        {"id": "reviews", "icon": "⭐", "label": "Reviews", "url": "/reviews"},
        {"id": "forecasting", "icon": "🔮", "label": "Forecasting", "url": "/forecasting"},
        {"id": "upload", "icon": "📤", "label": "Upload", "url": "/upload"}
    ]
    
    nav_html = ""
    for item in nav_items:
        active_class = "active" if current_page.lower() in item["id"] else ""
        nav_html += f'''
            <a href="{item["url"]}" class="nav-tab {active_class}">
                {item["icon"]} {item["label"]}
            </a>
        '''
    
    return nav_html

def create_features_html(features, theme):
    """Create features grid HTML"""
    features_html = ""
    for feature in features:
        features_html += f'''
            <div class="preview-item">
                <div class="preview-item-icon">{feature["icon"]}</div>
                <h4>{feature["title"]}</h4>
                <p>{feature["description"]}</p>
            </div>
        '''
    return features_html

def create_capabilities_html(capabilities, theme):
    """Create capabilities list HTML"""
    capabilities_html = ""
    for capability in capabilities:
        capabilities_html += f'<li>{capability}</li>'
    return f'<ul class="capabilities-list">{capabilities_html}</ul>'

def create_themed_page(title, icon, theme_name, content, page_type="default"):
    """
    Create a themed page with consistent layout
    
    Args:
        title (str): Page title
        icon (str): Page icon emoji
        theme_name (str): Theme name
        content (dict): Page-specific content
        page_type (str): Type of page for specific styling
    
    Returns:
        str: Complete HTML page
    """
    theme = get_theme(theme_name)
    user_info = get_user_info()
    
    # Create navigation with current page highlighted
    navigation_html = create_navigation_html(title.lower(), theme)
    
    # Create features grid if available
    features_html = ""
    if "features" in content:
        features_html = create_features_html(content["features"], theme)
    
    # Create capabilities list if available
    capabilities_html = ""
    if "capabilities" in content:
        capabilities_html = create_capabilities_html(content["capabilities"], theme)
    
    # Page-specific content sections
    specific_content = ""
    if page_type == "dashboard" and "metrics" in content:
        metrics = content["metrics"]
        specific_content = f'''
            <div class="metrics-grid">
                <div class="metric-card">
                    <h3>Total Collections</h3>
                    <p class="metric-value">{metrics["total_collections"]}</p>
                </div>
                <div class="metric-card">
                    <h3>Active Vehicles</h3>
                    <p class="metric-value">{metrics["active_vehicles"]}</p>
                </div>
                <div class="metric-card">
                    <h3>Efficiency Score</h3>
                    <p class="metric-value">{metrics["efficiency_score"]}</p>
                </div>
                <div class="metric-card">
                    <h3>Waste Processed</h3>
                    <p class="metric-value">{metrics["waste_processed"]}</p>
                </div>
            </div>
        '''
    elif page_type == "analytics" and "analytics_data" in content:
        analytics = content["analytics_data"]
        specific_content = f'''
            <div class="analytics-summary">
                <div class="analytics-card">
                    <h3>Efficiency Trends</h3>
                    <p>Current: {analytics["efficiency_trends"]["current_month"]}</p>
                    <p>Previous: {analytics["efficiency_trends"]["previous_month"]}</p>
                    <p class="improvement">Improvement: {analytics["efficiency_trends"]["improvement"]}</p>
                </div>
                <div class="analytics-card">
                    <h3>Collection Patterns</h3>
                    <p>Peak Hours: {analytics["collection_patterns"]["peak_hours"]}</p>
                    <p>Active Routes: {analytics["collection_patterns"]["optimal_routes"]}</p>
                </div>
            </div>
        '''
    elif page_type == "reports" and "recent_reports" in content:
        reports = content["recent_reports"]
        reports_html = ""
        for report in reports:
            reports_html += f'''
                <div class="report-item">
                    <h4>{report["title"]}</h4>
                    <p>Type: {report["type"]} | Generated: {report["generated"]}</p>
                    <p>Status: {report["status"]} | Size: {report["size"]}</p>
                </div>
            '''
        specific_content = f'<div class="reports-list">{reports_html}</div>'
    
    return f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title} - Swaccha Andhra Dashboard</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Inter', sans-serif;
                background-color: {theme["primary_bg"]};
                color: {theme["text_primary"]};
                line-height: 1.6;
                min-height: 100vh;
            }}
            
            .page-container {{
                min-height: 100vh;
                display: flex;
                flex-direction: column;
            }}
            
            /* Navigation Header */
            .navigation-header {{
                background: linear-gradient(135deg, {theme["secondary_bg"]} 0%, {theme["accent_bg"]} 100%);
                border-bottom: 3px solid {theme["brand_primary"]};
                padding: 1rem 2rem;
                box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
                position: sticky;
                top: 0;
                z-index: 1000;
            }}
            
            .nav-content {{
                max-width: 1600px;
                margin: 0 auto;
                display: flex;
                justify-content: space-between;
                align-items: center;
                flex-wrap: wrap;
                gap: 1rem;
            }}
            
            /* Nav-tabs contains both navigation and user info */
            .nav-tabs {{
                display: flex;
                align-items: center;
                gap: 1rem;
                flex-wrap: wrap;
                flex: 1;
                justify-content: space-between;
            }}
            
            /* Navigation buttons container */
            .nav-buttons {{
                display: flex;
                gap: 0.5rem;
                flex-wrap: wrap;
                align-items: center;
            }}
            
            .nav-tab {{
                background: {theme["accent_bg"]};
                color: {theme["text_primary"]};
                border: 2px solid {theme["card_bg"]};
                padding: 0.75rem 1.25rem;
                border-radius: 8px;
                text-decoration: none;
                font-weight: 600;
                font-size: 0.9rem;
                transition: all 0.2s ease;
                display: flex;
                align-items: center;
                gap: 0.5rem;
                white-space: nowrap;
                min-height: 44px;
            }}
            
            .nav-tab:hover {{
                background: {theme["brand_primary"]};
                color: white;
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            }}
            
            .nav-tab.active {{
                background: {theme["brand_primary"]};
                color: white;
                border-color: {theme["brand_primary"]};
                box-shadow: 0 4px 12px rgba(49, 130, 206, 0.4);
            }}
            
            /* User info inside nav-tabs */
            .user-info {{
                display: flex;
                align-items: center;
                gap: 1rem;
                background: {theme["card_bg"]};
                padding: 0.5rem 1rem;
                border-radius: 8px;
                border: 2px solid {theme["accent_bg"]};
                min-height: 44px;
                flex-shrink: 0;
            }}
            
            .user-avatar {{
                width: 32px;
                height: 32px;
                border-radius: 50%;
                border: 2px solid {theme["brand_primary"]};
                object-fit: cover;
            }}
            
            .user-details {{
                display: flex;
                flex-direction: column;
            }}
            
            .user-name {{
                font-weight: 600;
                font-size: 0.9rem;
                color: {theme["text_primary"]};
                line-height: 1.2;
            }}
            
            .user-role {{
                font-size: 0.75rem;
                color: {theme["text_secondary"]};
                line-height: 1.2;
            }}
            
            .logout-btn {{
                background: {theme["error"]};
                color: white;
                border: none;
                padding: 0.5rem 1rem;
                border-radius: 6px;
                cursor: pointer;
                font-weight: 600;
                font-size: 0.85rem;
                transition: all 0.2s ease;
                text-decoration: none;
                display: flex;
                align-items: center;
                gap: 0.25rem;
                min-height: 36px;
            }}
            
            .logout-btn:hover {{
                background: #C53030;
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(197, 48, 48, 0.4);
            }}
            
            /* Theme Switcher */
            .theme-switcher {{
                display: flex;
                align-items: center;
                gap: 0.25rem;
                background: {theme["card_bg"]};
                border: 2px solid {theme["accent_bg"]};
                border-radius: 8px;
                padding: 0.25rem;
                box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
                min-height: 44px;
            }}
            
            .theme-btn {{
                background: transparent;
                border: 1px solid {theme.get("border_light", theme["accent_bg"])};
                color: {theme["text_primary"]};
                padding: 0.25rem;
                border-radius: 4px;
                cursor: pointer;
                font-size: 1rem;
                width: 32px;
                height: 32px;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: all 0.2s ease;
            }}
            
            .theme-btn:hover {{
                background: {theme["brand_primary"]};
                color: white;
                transform: scale(1.1);
            }}
            
            .theme-btn.active {{
                background: {theme["brand_primary"]};
                color: white;
            }}
            
            /* Main Content */
            .main-content {{
                flex: 1;
                padding: 2rem;
                max-width: 1600px;
                margin: 0 auto;
                width: 100%;
            }}
            
            .page-hero {{
                background: linear-gradient(135deg, {theme["secondary_bg"]} 0%, {theme["accent_bg"]} 100%);
                border-radius: 12px;
                padding: 3rem 2rem;
                margin-bottom: 2rem;
                text-align: center;
                border: 2px solid {theme["card_bg"]};
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                position: relative;
                overflow: hidden;
            }}
            
            .page-hero::before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: radial-gradient(circle at 30% 70%, {theme["brand_primary"]}22 0%, transparent 50%);
                pointer-events: none;
            }}
            
            .page-hero-content {{
                position: relative;
                z-index: 2;
            }}
            
            .page-icon {{
                font-size: 4rem;
                margin-bottom: 1rem;
                filter: drop-shadow(2px 2px 8px rgba(0, 0, 0, 0.3));
                animation: float 3s ease-in-out infinite;
            }}
            
            @keyframes float {{
                0%, 100% {{ transform: translateY(0px); }}
                50% {{ transform: translateY(-10px); }}
            }}
            
            .page-title {{
                font-size: 3rem;
                font-weight: 900;
                color: {theme["text_primary"]};
                margin-bottom: 0.5rem;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
                line-height: 1.1;
            }}
            
            .page-subtitle {{
                font-size: 1.2rem;
                color: {theme["text_secondary"]};
                line-height: 1.5;
                max-width: 600px;
                margin: 0 auto;
            }}
            
            /* Content Sections */
            .content-section {{
                background: {theme["card_bg"]};
                border-radius: 12px;
                border: 2px solid {theme["accent_bg"]};
                padding: 2rem;
                margin: 2rem 0;
                box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
            }}
            
            .content-section h2 {{
                color: {theme["text_primary"]};
                font-size: 1.8rem;
                font-weight: 700;
                margin-bottom: 1rem;
            }}
            
            .content-section p {{
                color: {theme["text_secondary"]};
                font-size: 1.1rem;
                line-height: 1.6;
                margin-bottom: 2rem;
            }}
            
            /* Feature Grid */
            .feature-preview {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 1rem;
                margin-top: 2rem;
            }}
            
            .preview-item {{
                background: {theme["accent_bg"]};
                border: 1px solid {theme["card_bg"]};
                border-radius: 8px;
                padding: 1rem;
                text-align: center;
                transition: all 0.2s ease;
            }}
            
            .preview-item:hover {{
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
                border-color: {theme["brand_primary"]};
            }}
            
            .preview-item-icon {{
                font-size: 1.5rem;
                margin-bottom: 0.5rem;
            }}
            
            .preview-item h4 {{
                color: {theme["text_primary"]};
                font-size: 0.9rem;
                font-weight: 600;
                margin-bottom: 0.25rem;
            }}
            
            .preview-item p {{
                color: {theme["text_secondary"]};
                font-size: 0.8rem;
                line-height: 1.3;
                margin-bottom: 0;
            }}
            
            /* Metrics Grid */
            .metrics-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 1rem;
                margin: 2rem 0;
            }}
            
            .metric-card {{
                background: {theme["accent_bg"]};
                border: 2px solid {theme["card_bg"]};
                border-radius: 8px;
                padding: 1.5rem;
                text-align: center;
            }}
            
            .metric-card h3 {{
                color: {theme["text_secondary"]};
                font-size: 0.9rem;
                margin-bottom: 0.5rem;
            }}
            
            .metric-value {{
                color: {theme["brand_primary"]};
                font-size: 2rem;
                font-weight: 900;
                margin: 0;
            }}
            
            /* Analytics Cards */
            .analytics-summary {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 1rem;
                margin: 2rem 0;
            }}
            
            .analytics-card {{
                background: {theme["accent_bg"]};
                border: 2px solid {theme["card_bg"]};
                border-radius: 8px;
                padding: 1.5rem;
            }}
            
            .analytics-card h3 {{
                color: {theme["text_primary"]};
                margin-bottom: 1rem;
            }}
            
            .analytics-card p {{
                color: {theme["text_secondary"]};
                margin-bottom: 0.5rem;
            }}
            
            .improvement {{
                color: {theme["success"]};
                font-weight: 600;
            }}
            
            /* Reports List */
            .reports-list {{
                margin: 2rem 0;
            }}
            
            .report-item {{
                background: {theme["accent_bg"]};
                border: 1px solid {theme["card_bg"]};
                border-radius: 8px;
                padding: 1rem;
                margin-bottom: 1rem;
            }}
            
            .report-item h4 {{
                color: {theme["text_primary"]};
                margin-bottom: 0.5rem;
            }}
            
            .report-item p {{
                color: {theme["text_secondary"]};
                font-size: 0.9rem;
                margin-bottom: 0.25rem;
            }}
            
            /* Capabilities List */
            .capabilities-list {{
                list-style: none;
                padding-left: 0;
            }}
            
            .capabilities-list li {{
                color: {theme["text_secondary"]};
                margin-bottom: 0.5rem;
                padding-left: 1.5rem;
                position: relative;
            }}
            
            .capabilities-list li::before {{
                content: '✓';
                color: {theme["success"]};
                font-weight: bold;
                position: absolute;
                left: 0;
            }}
            
            /* Footer */
            .footer {{
                background: {theme["secondary_bg"]};
                border-top: 2px solid {theme["card_bg"]};
                padding: 1rem 2rem;
                text-align: center;
                color: {theme["text_secondary"]};
                font-size: 0.9rem;
            }}
            
            /* Responsive Design */
            @media (max-width: 1200px) {{
                .nav-tabs {{
                    flex-direction: column;
                    gap: 1rem;
                    align-items: stretch;
                }}
                
                .nav-buttons {{
                    justify-content: center;
                    width: 100%;
                }}
                
                .user-info {{
                    justify-content: center;
                    width: 100%;
                }}
            }}
            
            @media (max-width: 768px) {{
                .nav-content {{
                    flex-direction: column;
                    gap: 1rem;
                }}
                
                .nav-tabs {{
                    width: 100%;
                }}
                
                .nav-buttons {{
                    width: 100%;
                    justify-content: center;
                    flex-wrap: wrap;
                }}
                
                .nav-tab {{
                    flex: 1;
                    justify-content: center;
                    min-width: auto;
                    padding: 0.5rem 0.75rem;
                    font-size: 0.8rem;
                }}
                
                .main-content {{
                    padding: 1rem;
                }}
                
                .page-title {{
                    font-size: 2rem;
                }}
                
                .page-hero {{
                    padding: 2rem 1rem;
                }}
                
                .theme-switcher {{
                    align-self: center;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="page-container">
            <!-- Navigation Header -->
            <nav class="navigation-header">
                <div class="nav-content">
                    <!-- Nav-tabs contains both navigation buttons and user info -->
                    <div class="nav-tabs">
                        <!-- Left: Navigation Buttons -->
                        <div class="nav-buttons">
                            {navigation_html}
                        </div>
                        
                        <!-- Center/Right: User Info -->
                        <div class="user-info">
                            <img src="{user_info['picture']}" alt="User Avatar" class="user-avatar">
                            <div class="user-details">
                                <div class="user-name">{user_info['name']}</div>
                                <div class="user-role">{user_info['role']}</div>
                            </div>
                            <a href="/?logout=true" class="logout-btn">
                                🚪 Logout
                            </a>
                        </div>
                    </div>
                    
                    <!-- Right: Theme Switcher -->
                    <div class="theme-switcher">
                        <button class="theme-btn {'active' if theme_name == 'dark' else ''}" onclick="changeTheme('dark')" title="Dark Mode">🌙</button>
                        <button class="theme-btn {'active' if theme_name == 'light' else ''}" onclick="changeTheme('light')" title="Light Mode">☀️</button>
                        <button class="theme-btn {'active' if theme_name == 'high_contrast' else ''}" onclick="changeTheme('high_contrast')" title="High Contrast">🔳</button>
                        <button class="theme-btn {'active' if theme_name == 'swaccha_green' else ''}" onclick="changeTheme('swaccha_green')" title="Swaccha Green">🌿</button>
                    </div>
                </div>
            </nav>
            
            <!-- Main Content -->
            <main class="main-content">
                <div class="page-hero">
                    <div class="page-hero-content">
                        <div class="page-icon">{icon}</div>
                        <h1 class="page-title">{title}</h1>
                        <p class="page-subtitle">{content.get('description', 'Advanced functionality coming soon.')}</p>
                    </div>
                </div>
                
                {specific_content}
                
                <div class="content-section">
                    <h2>🚀 Key Features</h2>
                    <p>Explore the powerful capabilities available in this section:</p>
                    
                    <div class="feature-preview">
                        {features_html}
                    </div>
                </div>
                
                <div class="content-section">
                    <h2>📋 Capabilities</h2>
                    <p>This section provides comprehensive functionality including:</p>
                    
                    {capabilities_html}
                </div>
            </main>
            
            <!-- Footer -->
            <footer class="footer">
                <p>© 2025 Swaccha Andhra Corporation • {title} Section • <span id="current-time"></span></p>
            </footer>
        </div>
        
        <script>
            // Update current time
            function updateTime() {{
                const now = new Date();
                document.getElementById('current-time').textContent = now.toLocaleString();
            }}
            updateTime();
            setInterval(updateTime, 1000);
            
            // Theme switching
            function changeTheme(themeName) {{
                fetch('/api/set-theme', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ theme: themeName }})
                }}).then(() => {{
                    window.location.reload();
                }});
            }}
            
            // Add smooth scroll behavior
            document.documentElement.style.scrollBehavior = 'smooth';
        </script>
    </body>
    </html>
    '''