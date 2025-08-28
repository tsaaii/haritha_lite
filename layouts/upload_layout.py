"""
Upload Page Layout - Dedicated layout for uploads
"""

from flask import session
from utils.theme_utils import get_theme_styles

def create_upload_layout(theme_name="dark"):
    """Create dedicated upload page layout"""
    theme_styles = get_theme_styles(theme_name)
    theme = theme_styles["theme"]
    
    user_info = session.get('user_data', {})
    user_name = user_info.get('name', 'Administrator')
    user_role_display = user_info.get('role', 'administrator').replace('_', ' ').title()
    
    return f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Upload - Swaccha Andhra Dashboard</title>
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
            
            /* Custom Upload Page Styles */
            .upload-container {{
                min-height: 100vh;
                display: flex;
                flex-direction: column;
            }}
            
            .upload-header {{
                background: linear-gradient(135deg, {theme["secondary_bg"]} 0%, {theme["accent_bg"]} 100%);
                padding: 1rem 2rem;
                box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            
            .upload-logo {{
                font-size: 1.5rem;
                font-weight: 800;
                color: {theme["text_primary"]};
            }}
            
            .upload-nav {{
                display: flex;
                gap: 1rem;
            }}
            
            .nav-link {{
                padding: 0.5rem 1rem;
                background: rgba(255, 255, 255, 0.1);
                color: {theme["text_primary"]};
                text-decoration: none;
                border-radius: 6px;
                transition: all 0.3s ease;
            }}
            
            .nav-link:hover {{
                background: {theme["brand_primary"]};
                color: white;
            }}
            
            .upload-main {{
                flex: 1;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                padding: 2rem;
                background: linear-gradient(
                    45deg, 
                    {theme["primary_bg"]} 0%, 
                    {theme["secondary_bg"]} 100%
                );
            }}
            
            .greeting-section {{
                text-align: center;
                max-width: 600px;
                padding: 3rem;
                background: {theme["card_bg"]};
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                border: 2px solid {theme["brand_primary"]};
                position: relative;
                overflow: hidden;
            }}
            
            .greeting-section::before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: radial-gradient(
                    circle at 30% 70%, 
                    {theme["brand_primary"]}15 0%, 
                    transparent 50%
                );
                pointer-events: none;
            }}
            
            .greeting-content {{
                position: relative;
                z-index: 2;
            }}
            
            .greeting-icon {{
                font-size: 5rem;
                margin-bottom: 1rem;
                animation: bounce 2s ease-in-out infinite;
                filter: drop-shadow(2px 2px 8px rgba(0, 0, 0, 0.3));
            }}
            
            .greeting-title {{
                font-size: 3.5rem;
                font-weight: 900;
                color: {theme["text_primary"]};
                margin-bottom: 1rem;
                text-shadow: 2px 2px 8px rgba(0, 0, 0, 0.3);
                background: linear-gradient(45deg, {theme["brand_primary"]}, {theme["brand_secondary"]});
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }}
            
            .greeting-subtitle {{
                font-size: 1.3rem;
                color: {theme["text_secondary"]};
                margin-bottom: 2rem;
                line-height: 1.5;
            }}
            
            .upload-actions {{
                display: flex;
                gap: 1rem;
                justify-content: center;
                flex-wrap: wrap;
            }}
            
            .action-btn {{
                padding: 1rem 2rem;
                border: none;
                border-radius: 12px;
                font-weight: 600;
                font-size: 1rem;
                cursor: pointer;
                transition: all 0.3s ease;
                text-decoration: none;
                display: inline-block;
                min-width: 150px;
            }}
            
            .btn-primary {{
                background: {theme["brand_primary"]};
                color: white;
                box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
            }}
            
            .btn-secondary {{
                background: {theme["accent_bg"]};
                color: {theme["text_primary"]};
                border: 2px solid {theme["brand_primary"]};
            }}
            
            .action-btn:hover {{
                transform: translateY(-3px);
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
            }}
            
            @keyframes bounce {{
                0%, 20%, 50%, 80%, 100% {{
                    transform: translateY(0);
                }}
                40% {{
                    transform: translateY(-20px);
                }}
                60% {{
                    transform: translateY(-10px);
                }}
            }}
            
            /* Responsive design */
            @media (max-width: 768px) {{
                .greeting-section {{
                    margin: 1rem;
                    padding: 2rem;
                }}
                
                .greeting-title {{
                    font-size: 2.5rem;
                }}
                
                .upload-actions {{
                    flex-direction: column;
                    align-items: center;
                }}
                
                .action-btn {{
                    width: 100%;
                    max-width: 250px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="upload-container">
            <header class="upload-header">
                <div class="upload-logo">📤 Upload Center</div>
                <nav class="upload-nav">
                    <a href="/dashboard" class="nav-link">📊 Dashboard</a>
                    <a href="/data-analytics" class="nav-link">📈 Analytics</a>
                    <a href="/reports" class="nav-link">📋 Reports</a>
                    <a href="/?logout=true" class="nav-link">🚪 Logout</a>
                </nav>
            </header>
            
            <main class="upload-main">
                <div class="greeting-section">
                    <div class="greeting-content">
                        <div class="greeting-icon">👋</div>
                        <h1 class="greeting-title">Hi Sai!</h1>
                        <p class="greeting-subtitle">
                            Welcome to your personalized upload center. 
                            Ready to manage your files and data?
                        </p>
                        <div class="upload-actions">
                            <a href="#" class="action-btn btn-primary">📁 Browse Files</a>
                            <a href="/dashboard" class="action-btn btn-secondary">← Back to Dashboard</a>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    </body>
    </html>
    '''
