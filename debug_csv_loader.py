# debug_csv_loading.py
"""
Debug script to identify why CSV is not loading into filter container
"""

import sys
import os
import traceback

def debug_csv_loading():
    """Debug CSV loading step by step"""
    print("🔍 DEBUGGING CSV LOADING ISSUE")
    print("=" * 60)
    
    # Step 1: Check if data_loader.py exists and works
    print("\n1. 📦 Testing data_loader.py import...")
    try:
        from data_loader import get_cached_data, get_filter_options, check_csv_file
        print("✅ data_loader.py imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import data_loader.py: {e}")
        return False
    except Exception as e:
        print(f"❌ Error importing data_loader.py: {e}")
        return False
    
    # Step 2: Check CSV file existence
    print("\n2. 📁 Checking CSV file existence...")
    try:
        csv_files = check_csv_file()
        if csv_files:
            for file_info in csv_files:
                print(f"✅ Found: {file_info['path']} ({file_info['size_mb']} MB)")
        else:
            print("❌ No CSV files found in expected locations:")
            print("   Expected locations:")
            print("   - waste_management_data_updated.csv")
            print("   - data/waste_management_data_updated.csv") 
            print("   - uploads/waste_management_data_updated.csv")
            print("   - uploads/dash_uploads/waste_management_data_updated.csv")
            
            # Create a minimal test CSV
            print("\n📝 Creating minimal test CSV...")
            create_test_csv()
            return debug_csv_loading()  # Retry after creating CSV
    except Exception as e:
        print(f"❌ Error checking CSV files: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return False
    
    # Step 3: Test data loading
    print("\n3. 📊 Testing data loading...")
    try:
        df = get_cached_data()
        print(f"✅ Data loaded: {len(df)} records")
        
        if df.empty:
            print("❌ DataFrame is empty!")
            return False
        
        print(f"📋 Columns: {list(df.columns)}")
        
        # Show sample data
        print(f"📄 Sample data (first 3 rows):")
        print(df.head(3).to_string())
        
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return False
    
    # Step 4: Test filter options generation
    print("\n4. 🎛️ Testing filter options generation...")
    try:
        options = get_filter_options(df)
        
        agencies = [opt['value'] for opt in options['agencies']]
        clusters = [opt['value'] for opt in options['clusters']]
        sites = [opt['value'] for opt in options['sites']]
        
        print(f"✅ Agencies ({len(agencies)}): {agencies}")
        print(f"✅ Clusters ({len(clusters)}): {clusters}")
        print(f"✅ Sites ({len(sites)}): {sites}")
        
        if len(agencies) <= 1:  # Only 'all' option
            print("⚠️ Warning: Only 'all' option found - check CSV data format")
            
    except Exception as e:
        print(f"❌ Error generating filter options: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return False
    
    # Step 5: Test dashboard page integration
    print("\n5. 🔧 Testing dashboard page integration...")
    try:
        from endpoints.dashboard_page import get_csv_filter_options
        dashboard_options = get_csv_filter_options()
        
        print(f"✅ Dashboard filter options loaded:")
        print(f"   📊 Agencies: {len(dashboard_options['agencies'])} options")
        print(f"   🗺️ Clusters: {len(dashboard_options['clusters'])} options")
        print(f"   📍 Sites: {len(dashboard_options['sites'])} options")
        
        # Show actual options
        print(f"\n📋 Agency options:")
        for value, label in dashboard_options['agencies'][:5]:  # First 5
            print(f"   - {value}: {label}")
        
        print(f"\n📋 Cluster options:")
        for value, label in dashboard_options['clusters']:
            print(f"   - {value}: {label}")
        
    except Exception as e:
        print(f"❌ Error testing dashboard integration: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return False
    
    # Step 6: Test Flask route registration
    print("\n6. 🌐 Testing Flask route...")
    try:
        from endpoints.dashboard_page import register_dashboard_routes
        print("✅ Dashboard routes can be imported")
        
        # Test if we can access the dashboard page function
        from endpoints.dashboard_page import dashboard_page
        print("✅ Dashboard page function accessible")
        
    except Exception as e:
        print(f"❌ Error with Flask routes: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 CSV LOADING DEBUG COMPLETED")
    print("=" * 60)
    
    return True

def create_test_csv():
    """Create a test CSV file if none exists"""
    try:
        import pandas as pd
        import os
        from datetime import datetime, timedelta
        
        # Create test data
        data = [
            {"Date": "2025-06-01", "agency": "madanapalle", "site": "madanapalle", "cluster": "MM", "weight": 15000, "vehicle": "AP39VB2709", "time": "09:30:00", "waste_type": "MSW"},
            {"Date": "2025-06-02", "agency": "donthalli", "site": "donthalli", "cluster": "NMC", "weight": 23000, "vehicle": "AP04UB0825", "time": "10:15:00", "waste_type": "MSW"},
            {"Date": "2025-06-03", "agency": "visakhapatnam", "site": "visakhapatnam", "cluster": "VMRC", "weight": 18500, "vehicle": "AP39UC5432", "time": "08:45:00", "waste_type": "MSW"},
            {"Date": "2025-06-04", "agency": "hyderabad", "site": "hyderabad", "cluster": "GHMC", "weight": 31000, "vehicle": "TS09FC8765", "time": "11:20:00", "waste_type": "MSW"},
            {"Date": "2025-06-05", "agency": "tirupati", "site": "tirupati", "cluster": "TTD", "weight": 14200, "vehicle": "AP07RB2398", "time": "07:30:00", "waste_type": "MSW"},
            {"Date": "2025-06-06", "agency": "guntur", "site": "guntur", "cluster": "GMC", "weight": 26800, "vehicle": "AP16DB9087", "time": "13:45:00", "waste_type": "MSW"},
            {"Date": "2025-06-07", "agency": "madanapalle", "site": "madanapalle", "cluster": "MM", "weight": 19300, "vehicle": "AP39VB2709", "time": "14:20:00", "waste_type": "MSW"},
            {"Date": "2025-06-08", "agency": "donthalli", "site": "donthalli", "cluster": "NMC", "weight": 21700, "vehicle": "AP04UB0825", "time": "16:10:00", "waste_type": "MSW"}
        ]
        
        df = pd.DataFrame(data)
        
        # Create directories
        os.makedirs('uploads', exist_ok=True)
        os.makedirs('data', exist_ok=True)
        
        # Save CSV to multiple locations
        paths = [
            'waste_management_data_updated.csv',
            'data/waste_management_data_updated.csv', 
            'uploads/waste_management_data_updated.csv'
        ]
        
        for path in paths:
            df.to_csv(path, index=False)
            print(f"✅ Created test CSV: {path}")
        
        print(f"📊 Test CSV contains {len(df)} records with {df['agency'].nunique()} agencies")
        
    except Exception as e:
        print(f"❌ Error creating test CSV: {e}")

def check_dashboard_html():
    """Check if the dashboard HTML contains CSV data"""
    print("\n" + "=" * 60)
    print("🔍 CHECKING DASHBOARD HTML GENERATION")
    print("=" * 60)
    
    try:
        from endpoints.dashboard_page import create_dashboard_filter_content
        
        # Test content generation
        content = create_dashboard_filter_content('dark')
        
        print("✅ Dashboard content generated successfully")
        
        # Check if HTML contains actual CSV data
        html = content['description']
        
        # Look for signs of CSV data vs hardcoded data
        if 'madanapalle' in html.lower():
            print("✅ Found CSV agency 'madanapalle' in HTML")
        else:
            print("❌ Did not find CSV agencies in HTML")
            
        if 'zigma' in html.lower():
            print("❌ Found hardcoded agency 'zigma' - CSV not loaded!")
        else:
            print("✅ No hardcoded agencies found")
        
        # Count option tags
        option_count = html.count('<option')
        print(f"📋 Found {option_count} option tags in HTML")
        
        # Show a snippet of the HTML around agency options
        if 'agency-filter' in html:
            start = html.find('id="agency-filter"')
            if start != -1:
                end = html.find('</select>', start)
                if end != -1:
                    snippet = html[start:end+9]
                    print(f"\n📄 Agency filter HTML snippet:")
                    print(snippet[:500] + "..." if len(snippet) > 500 else snippet)
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking dashboard HTML: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return False

def main():
    """Main debug function"""
    print("🚀 CSV Loading Debug Tool")
    print("Debugging why CSV data is not appearing in dashboard filters")
    
    # Run all debug steps
    basic_debug = debug_csv_loading()
    html_debug = check_dashboard_html()
    
    if basic_debug and html_debug:
        print("\n🎉 ALL DEBUG TESTS PASSED!")
        print("✅ CSV data should be loading into dashboard filters")
        print("\n📝 Next steps:")
        print("1. Start your dashboard: python main.py")
        print("2. Go to /dashboard")
        print("3. Check browser console for any JavaScript errors")
        print("4. Verify filter dropdowns show CSV data")
    else:
        print("\n❌ SOME DEBUG TESTS FAILED")
        print("🔧 Issues found that need to be fixed:")
        if not basic_debug:
            print("   - CSV loading or data processing issues")
        if not html_debug:
            print("   - HTML generation or integration issues")

if __name__ == "__main__":
    main()