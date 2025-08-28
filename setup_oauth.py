# setup_oauth.py - Run this to set up OAuth quickly
"""
OAuth Setup Script for Swaccha Andhra Dashboard
Automatically installs dependencies and checks configuration
"""

import os
import sys
import subprocess
import json

def install_dependencies():
    """Install required OAuth dependencies"""
    print("📦 Installing OAuth dependencies...")
    
    dependencies = [
        'google-auth>=2.22.0',
        'google-auth-oauthlib>=1.0.0', 
        'google-auth-httplib2>=0.1.0',
        'google-api-python-client>=2.95.0',
        'requests>=2.31.0'
    ]
    
    for dep in dependencies:
        try:
            print(f"   Installing {dep}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', dep])
            print(f"   ✅ {dep} installed")
        except subprocess.CalledProcessError:
            print(f"   ❌ Failed to install {dep}")
            return False
    
    print("✅ All dependencies installed successfully!")
    return True

def check_client_secrets():
    """Check client_secrets.json configuration"""
    print("\n🔍 Checking client_secrets.json...")
    
    if not os.path.exists('client_secrets.json'):
        print("❌ client_secrets.json not found")
        print("\n📝 To create client_secrets.json:")
        print("1. Go to https://console.developers.google.com/")
        print("2. Create a project (or select existing)")
        print("3. Enable Google+ API or People API")
        print("4. Create OAuth 2.0 credentials")
        print("5. Add redirect URI: https://applied-pursuit-332603.el.r.appspot.com/oauth/callback")
        print("6. Download the JSON file")
        print("7. Rename it to 'client_secrets.json'")
        print("8. Place it in your project root directory")
        
        # Create template
        template = {
            "web": {
                "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",
                "project_id": "your-project-id",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://www.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_secret": "YOUR_CLIENT_SECRET",
                "redirect_uris": [
                    "https://applied-pursuit-332603.el.r.appspot.com/oauth/callback",
                    "http://127.0.0.1:8050/oauth/callback"
                ]
            }
        }
        
        with open('client_secrets.json.template', 'w') as f:
            json.dump(template, f, indent=2)
        
        print("\n✅ Created client_secrets.json.template")
        print("   Edit this file with your Google credentials and rename to client_secrets.json")
        return False
    
    try:
        with open('client_secrets.json', 'r') as f:
            config = json.load(f)
        
        # Check format
        if 'web' in config:
            oauth_config = config['web']
        elif 'installed' in config:
            oauth_config = config['installed']
        else:
            print("❌ Invalid client_secrets.json format")
            return False
        
        # Check required fields
        required_fields = ['client_id', 'client_secret']
        missing_fields = [field for field in required_fields if not oauth_config.get(field)]
        
        if missing_fields:
            print(f"❌ Missing required fields: {missing_fields}")
            return False
        
        # Check redirect URI
        redirect_uris = oauth_config.get('redirect_uris', [])
        required_uri = 'https://applied-pursuit-332603.el.r.appspot.com/oauth/callback'
        
        if required_uri not in redirect_uris:
            print(f"⚠️  Redirect URI missing: {required_uri}")
            print("   Add this to your Google Cloud Console OAuth configuration")
        
        print("✅ client_secrets.json looks good!")
        print(f"   Client ID: {oauth_config['client_id'][:20]}...")
        return True
        
    except json.JSONDecodeError:
        print("❌ Invalid JSON in client_secrets.json")
        return False
    except Exception as e:
        print(f"❌ Error reading client_secrets.json: {e}")
        return False

def check_auth_config():
    """Check auth configuration"""
    print("\n👥 Checking user authorization...")
    
    try:
        from config.auth import ALLOWED_USERS
        
        total_users = sum(len(users) for users in ALLOWED_USERS.values())
        print(f"✅ Auth configuration loaded - {total_users} authorized users")
        
        print("   Administrators:")
        for email in ALLOWED_USERS.get('administrators', []):
            print(f"     - {email}")
        
        print("   Super Admins:")
        for email in ALLOWED_USERS.get('super_admins', []):
            print(f"     - {email}")
        
        return True
        
    except ImportError:
        print("❌ Could not import auth configuration")
        return False

def test_oauth_system():
    """Test the OAuth system"""
    print("\n🧪 Testing OAuth system...")
    
    try:
        from utils.simple_oauth import get_oauth_manager
        
        oauth_manager = get_oauth_manager()
        debug_info = oauth_manager.get_debug_info()
        
        print(f"   OAuth configured: {'✅' if debug_info.get('oauth_configured') else '❌'}")
        print(f"   client_secrets.json: {'✅' if debug_info.get('client_secrets_exists') else '❌'}")
        print(f"   Active sessions: {debug_info.get('active_sessions', 0)}")
        
        # Test dependencies
        print("   Dependencies:")
        for dep, status in debug_info.get('dependencies', {}).items():
            print(f"     - {dep}: {status}")
        
        return debug_info.get('oauth_configured', False)
        
    except ImportError as e:
        print(f"❌ Could not import OAuth manager: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Swaccha Andhra OAuth Setup")
    print("=" * 50)
    
    # Step 1: Install dependencies
    if not install_dependencies():
        print("\n❌ Setup failed at dependency installation")
        return
    
    # Step 2: Check client secrets
    secrets_ok = check_client_secrets()
    
    # Step 3: Check auth config
    auth_ok = check_auth_config()
    
    # Step 4: Test system
    oauth_ok = test_oauth_system()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 SETUP SUMMARY")
    print("=" * 50)
    
    print(f"Dependencies: {'✅ Installed' if True else '❌ Failed'}")
    print(f"client_secrets.json: {'✅ Configured' if secrets_ok else '❌ Missing/Invalid'}")
    print(f"Auth config: {'✅ Loaded' if auth_ok else '❌ Error'}")
    print(f"OAuth system: {'✅ Ready' if oauth_ok else '⚠️ Demo Mode'}")
    
    if oauth_ok:
        print("\n🎉 OAUTH FULLY CONFIGURED!")
        print("✅ Your app is ready for real Google OAuth")
    else:
        print("\n📱 DEMO MODE ACTIVE")
        print("✅ Your app will work with demo authentication")
        print("📝 Complete the client_secrets.json setup for real OAuth")
    
    print("\n🚀 NEXT STEPS:")
    print("1. Run your app: python main.py")
    print("2. Visit: https://applied-pursuit-332603.el.r.appspot.com/debug/oauth")
    print("3. Test the OAuth flow")
    
    if not secrets_ok:
        print("4. Set up real Google OAuth (optional):")
        print("   - Follow instructions at /debug/oauth")
        print("   - Edit client_secrets.json.template")
        print("   - Rename to client_secrets.json")

if __name__ == "__main__":
    main()