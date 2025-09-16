# site_dashboard.py - Flask Blueprint for Site Dashboards
"""
Site Dashboard Flask Blueprint
Fetches real data from weighbridge API and displays site-specific dashboards
FIXED: Returns complete HTML to prevent Dash interference
"""

from flask import Blueprint, request, session, redirect, jsonify, make_response
from datetime import datetime, timedelta
import requests
from collections import defaultdict
import logging
from jinja2 import Template

# CREATE BLUEPRINT FIRST
site_dashboard_bp = Blueprint('site_dashboard', __name__, url_prefix='/site')

def create_standalone_html_response(title, content):
    """Create a complete HTML response that doesn't load Dash"""
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{{ title }}</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body { 
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                margin: 0;
                padding: 20px;
            }
            .container {
                background: white;
                border-radius: 12px;
                padding: 2rem;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                margin-top: 2rem;
                max-width: 1200px;
            }
            .header {
                background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
                color: white;
                padding: 2rem;
                border-radius: 12px 12px 0 0;
                margin: -2rem -2rem 2rem -2rem;
            }
            .btn-back {
                background: #3b82f6;
                color: white;
                padding: 10px 20px;
                text-decoration: none;
                border-radius: 8px;
                display: inline-block;
                margin-bottom: 1rem;
            }
            .btn-back:hover {
                background: #2563eb;
                color: white;
                text-decoration: none;
            }
            .card {
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                margin-bottom: 1rem;
            }
            .metric-card {
                text-align: center;
                padding: 1.5rem;
                background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            }
            .metric-value {
                font-size: 2rem;
                font-weight: bold;
                color: #495057;
            }
            .alert-success {
                background: #d4edda;
                border: 1px solid #c3e6cb;
                color: #155724;
                padding: 1rem;
                border-radius: 8px;
                margin: 1rem 0;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>{{ title }}</h1>
                <p class="mb-0">Site-specific dashboard</p>
            </div>
            
            <a href="/" class="btn-back">← Back to Main Dashboard</a>
            
            {{ content | safe }}
        </div>
        
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
        <!-- NO DASH JAVASCRIPT - This prevents Dash from loading -->
    </body>
    </html>
    """
    
    template = Template(html_template)
    html = template.render(title=title, content=content)
    
    # Create response with headers that prevent caching
    response = make_response(html)
    response.headers['Content-Type'] = 'text/html; charset=utf-8'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    
    return response

def get_sites_from_api():
    """Get sites from API with fallback"""
    try:
        response = requests.get("https://weighbridge-api-287877277037.asia-southeast1.run.app/sites", timeout=10)
        if response.status_code == 200:
            data = response.json()
            return sorted(data.get("sites", []))
    except Exception as e:
        logging.error(f"Error fetching sites: {e}")
    return ["Adoni", "Bheemavaram", "Nandyal", "Yemmiganur", "Palacole", "Anantapur", "Visag", "Kadapa"]

def get_site_info_from_api(site_name):
    """Get site-specific information from the site info API"""
    try:
        url = f"https://weighbridge-site-api-287877277037.asia-southeast1.run.app/site/{site_name}"
        
        print(f"DEBUG: Fetching site info for {site_name} from {url}")
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"DEBUG: Got site info data: {data}")
            
            # Calculate progress offset for circular progress bar (283 is full circle circumference)
            completion_percentage = data.get('completion_percentage', 0)
            progress_offset = 283 - (283 * (completion_percentage / 100))
            
            # Add calculated fields
            data['progress_offset'] = round(progress_offset, 2)
            
            return data
        else:
            print(f"ERROR: Site info API returned status {response.status_code} for {site_name}")
            return {}
            
    except Exception as e:
        print(f"ERROR: Failed to fetch site info for {site_name}: {e}")
        return {}

def get_all_site_records(site_name, target_date=None):
    """Get ALL records for a specific site from the weighbridge API with pagination support"""
    all_records = []
    todays_records = []
    page = 1
    
    # Use today's date if no target date specified
    if target_date is None:
        target_date = datetime.now().strftime('%Y-%m-%d')
    
    try:
        url = f"https://weighbridge-api-287877277037.asia-southeast1.run.app/records"
        
        while True:
            params = {
                'site_name': site_name,
                'page': page,
                'per_page': 100  # Maximum records per page
            }
            
            print(f"DEBUG: Fetching page {page} for {site_name} from {url}")
            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code != 200:
                print(f"ERROR: API returned status {response.status_code} for {site_name} page {page}")
                break
                
            data = response.json()
            records = data.get('records', [])
            pagination = data.get('pagination', {})
            
            if not records:
                print(f"DEBUG: No more records found at page {page}")
                break
            
            print(f"DEBUG: Got {len(records)} records from page {page}")
            
            # Add to all records
            all_records.extend(records)
            
            # Filter today's records
            page_todays_records = [r for r in records if r.get('date') == target_date]
            todays_records.extend(page_todays_records)
            
            # Check if we have more pages
            has_next_page = pagination.get('has_next_page', False)
            current_page = pagination.get('current_page', page)
            total_pages = pagination.get('total_pages', 1)
            
            print(f"DEBUG: Page {current_page}/{total_pages}, has_next: {has_next_page}")
            
            if not has_next_page or page >= total_pages:
                break
                
            page += 1
            
        print(f"DEBUG: Total records fetched: {len(all_records)}")
        print(f"DEBUG: Today's records ({target_date}): {len(todays_records)}")
        
        return all_records, todays_records
            
    except Exception as e:
        print(f"ERROR: Failed to fetch site records for {site_name}: {e}")
        return [], []

def process_site_data(site_name, target_date=None):
    """Process weighbridge records to calculate site statistics"""
    if target_date is None:
        target_date = datetime.now().strftime('%Y-%m-%d')
    
    # Get site-specific information from the new API
    site_info = get_site_info_from_api(site_name)
    
    # Get all records and today's records from weighbridge API
    all_records, todays_records = get_all_site_records(site_name, target_date)
    
    print(f"DEBUG: Processing {len(all_records)} total records, {len(todays_records)} for {target_date}")
    
    # Default response structure
    base_response = {
        'site_name': site_name,
        'target_date': target_date,
        'status': 'No Data',
        'status_emoji': '⚠️',
        'total_trips': 0,
        'total_inward': 0.0,
        'total_outward': 0.0,
        'total_net_weight': 0.0,
        'recent_vehicles': [],
        'material_breakdown': {},
        'hourly_activity': {},
        'last_updated': datetime.now().strftime('%H:%M:%S'),
        'data_range': 'No data available',
        'alerts': ['No recent data available'],
        'agency': 'Not available',
        'contractor': 'Not available',
        'cluster': 'Not available',
        'total_quantity_given': 0,
        'total_remediated': 0,
        'completion_percentage': 0,
        'days_remaining': 0,
        'progress_offset': 283
    }
    
    # Merge site info data into response
    if site_info:
        base_response.update({
            'agency': site_info.get('agency', 'Not available'),
            'contractor': site_info.get('sub_contractor', 'Not available'),
            'cluster': site_info.get('cluster_name', 'Not available'),
            'total_quantity_given': round(site_info.get('quantity_to_be_remediated', 0), 2),
            'total_remediated': round(site_info.get('cumulative_quantity_remediated', 0), 2),
            'completion_percentage': round(site_info.get('completion_percentage', 0), 2),
            'days_remaining': site_info.get('days_remaining', 0),
            'progress_offset': round(site_info.get('progress_offset', 283), 2)
        })
    
    if not all_records:
        return base_response
    
    # Process today's records for main statistics
    total_trips = len(todays_records)
    total_inward = 0.0
    total_outward = 0.0
    total_net_weight = 0.0
    recent_vehicles = []
    
    for record in todays_records:
        try:
            net_weight = float(record.get('net_weight', 0))
            material = record.get('material', '').strip()
            
            total_net_weight += net_weight
            
            if material == "Legacy/MSW":
                total_inward += net_weight
            else:
                total_outward += net_weight
            
            recent_vehicles.append({
                'vehicle_no': record.get('vehicle_no', ''),
                'ticket_no': record.get('ticket_no', ''),
                'time': record.get('time', ''),
                'weight': net_weight,
                'material': material,
                'date': record.get('date', '')
            })
        
        except Exception as e:
            print(f"ERROR: Failed to process record: {e}")
            continue
    
    # Sort recent vehicles by time and take top 10
    recent_vehicles.sort(key=lambda x: x.get('time', ''), reverse=True)
    recent_vehicles = recent_vehicles[:10]
    
    # Determine status
    if total_trips > 0:
        status = 'Active'
        status_emoji = '🟢'
    elif len(all_records) > 0:
        status = 'No activity today'
        status_emoji = '🟡'
    else:
        status = 'Offline'
        status_emoji = '🔴'
    
    # Generate alerts
    alerts = []
    if total_trips == 0:
        alerts.append(f"No weighbridge transactions recorded on {target_date}")
    else:
        alerts.append(f"Active weighbridge: {total_trips} trips completed on {target_date}")
    
    return {
        **base_response,
        'status': status,
        'status_emoji': status_emoji,
        'total_trips': total_trips,
        'total_inward': round(total_inward / 1000, 2),
        'total_outward': round(total_outward / 1000, 2),
        'total_net_weight': round(total_net_weight / 1000, 2),
        'recent_vehicles': recent_vehicles,
        'alerts': alerts,
        'todays_record_count': len(todays_records),
        'total_historical_records': len(all_records)
    }

# ROUTES - Now using the blueprint that was created above

@site_dashboard_bp.route('/')
def site_list():
    """List all available sites - FIXED to return complete HTML"""
    
    if not session.get('swaccha_session_id'):
        return redirect('/login')
    
    sites = get_sites_from_api()
    
    sites_html = ""
    for site in sites:
        sites_html += f"""
        <div class="col-md-4 mb-3">
            <div class="card">
                <div class="card-body">
                    <h5 class="card-title">{site.title()}</h5>
                    <p class="card-text">
                        Click to view detailed dashboard
                    </p>
                    <a href="/site/{site}" class="btn btn-primary">View Dashboard</a>
                </div>
            </div>
        </div>
        """
    
    content = f"""
    <div class="alert-success">
        <strong>✅ Site List Working!</strong> 
        This page is served by Flask, not Dash.
    </div>
    
    <h2>Available Sites</h2>
    <div class="row">
        {sites_html}
    </div>
    """
    
    return create_standalone_html_response("Site List", content)

@site_dashboard_bp.route('/<site_name>')
def site_dashboard(site_name):
    """Site-specific dashboard - FIXED to return complete HTML"""
    
    # Check authentication
    if not session.get('swaccha_session_id'):
        return redirect('/login')
    
    # Validate site name
    available_sites = get_sites_from_api()
    if site_name not in available_sites:
        content = f"""
        <div class="alert alert-warning">
            <h4>Site Not Found</h4>
            <p>The site <strong>{site_name}</strong> was not found in our database.</p>
            <p>Available sites: {', '.join(available_sites)}</p>
        </div>
        """
        return create_standalone_html_response(f"Site Not Found: {site_name}", content)
    
    # Get target date from query params (defaults to today)
    target_date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    
    print(f"DEBUG: Loading dashboard for site: {site_name}, date: {target_date}")
    
    # Get processed site data for the target date
    site_data = process_site_data(site_name, target_date)
    
    # Create site dashboard content
    content = f"""
    <div class="alert-success">
        <strong>✅ Flask Route Working!</strong> 
        This is <strong>{site_name.title()}</strong> served by Flask, not Dash.
    </div>
    
    <div class="row">
        <div class="col-md-6">
            <div class="card">
                <div class="card-header">
                    <h5>Site Information</h5>
                </div>
                <div class="card-body">
                    <p><strong>Site:</strong> {site_name.title()}</p>
                    <p><strong>Agency:</strong> {site_data.get('agency', 'Unknown')}</p>
                    <p><strong>Cluster:</strong> {site_data.get('cluster', 'Unknown')}</p>
                    <p><strong>Status:</strong> {site_data.get('status_emoji', '')} {site_data.get('status', 'Active')}</p>
                    <p><strong>Last Updated:</strong> {site_data.get('last_updated', 'Unknown')}</p>
                </div>
            </div>
        </div>
        
        <div class="col-md-6">
            <div class="card">
                <div class="card-header">
                    <h5>Progress Metrics</h5>
                </div>
                <div class="card-body">
                    <p><strong>Total Quantity:</strong> {site_data.get('total_quantity_given', 0):,.2f} MT</p>
                    <p><strong>Completed:</strong> {site_data.get('total_remediated', 0):,.2f} MT</p>
                    <p><strong>Completion:</strong> {site_data.get('completion_percentage', 0):.2f}%</p>
                    <p><strong>Days Remaining:</strong> {site_data.get('days_remaining', 0)}</p>
                </div>
            </div>
        </div>
    </div>
    
    <div class="row mt-4">
        <div class="col-md-4">
            <div class="card metric-card">
                <div class="metric-value">{site_data.get('total_trips', 0)}</div>
                <div>Total Trips Today</div>
            </div>
        </div>
        <div class="col-md-4">
            <div class="card metric-card">
                <div class="metric-value">{site_data.get('total_net_weight', 0)} MT</div>
                <div>Net Weight Today</div>
            </div>
        </div>
        <div class="col-md-4">
            <div class="card metric-card">
                <div class="metric-value">{site_data.get('total_historical_records', 0)}</div>
                <div>Total Historical Records</div>
            </div>
        </div>
    </div>
    
    <div class="mt-4">
        <div class="card">
            <div class="card-header">
                <h5>Actions</h5>
            </div>
            <div class="card-body">
                <a href="/site/{site_name}/analytics" class="btn btn-primary me-2">View Analytics</a>
                <a href="/site/{site_name}/api/data" class="btn btn-secondary me-2">API Data</a>
                <a href="/legacy/report" class="btn btn-success">Legacy Report</a>
                <a href="/site/" class="btn btn-outline-secondary">All Sites</a>
            </div>
        </div>
    </div>
    
    <div class="mt-4">
        <div class="card">
            <div class="card-header">
                <h5>Recent Activity</h5>
            </div>
            <div class="card-body">
                <p><strong>Target Date:</strong> {target_date}</p>
                <p><strong>Records for Today:</strong> {site_data.get('todays_record_count', 0)}</p>
                
                <h6>Recent Vehicles:</h6>
                <div class="table-responsive">
                    <table class="table table-sm">
                        <thead>
                            <tr>
                                <th>Vehicle</th>
                                <th>Time</th>
                                <th>Weight (kg)</th>
                                <th>Material</th>
                            </tr>
                        </thead>
                        <tbody>
                            {"".join([f"<tr><td>{v.get('vehicle_no', 'N/A')}</td><td>{v.get('time', 'N/A')}</td><td>{v.get('weight', 0):,.0f}</td><td>{v.get('material', 'N/A')}</td></tr>" for v in site_data.get('recent_vehicles', [])[:5]])}
                        </tbody>
                    </table>
                </div>
                
                <h6>Alerts:</h6>
                <ul>
                    {"".join([f"<li>{alert}</li>" for alert in site_data.get('alerts', [])])}
                </ul>
            </div>
        </div>
    </div>
    """
    
    return create_standalone_html_response(f"Site Dashboard: {site_name.title()}", content)

@site_dashboard_bp.route('/<site_name>/api/data')
def site_api_data(site_name):
    """API endpoint for real-time site data (AJAX updates)"""
    
    available_sites = get_sites_from_api()
    if site_name not in available_sites:
        return jsonify({'error': 'Site not found'}), 404
    
    # Get target date from query params
    target_date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    
    site_data = process_site_data(site_name, target_date)
    return jsonify(site_data)

@site_dashboard_bp.route('/<site_name>/analytics')
def site_analytics(site_name):
    """Detailed analytics page for a site"""
    
    if not session.get('swaccha_session_id'):
        return redirect('/login')
    
    available_sites = get_sites_from_api()
    if site_name not in available_sites:
        content = f"""
        <div class="alert alert-warning">
            <h4>Site Not Found</h4>
            <p>The site <strong>{site_name}</strong> was not found.</p>
        </div>
        """
        return create_standalone_html_response(f"Analytics - Site Not Found", content)
    
    target_date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    site_data = process_site_data(site_name, target_date)
    
    content = f"""
    <div class="alert-success">
        <strong>📊 Analytics Dashboard for {site_name.title()}</strong>
    </div>
    
    <div class="card">
        <div class="card-header">
            <h5>Site Analytics - {target_date}</h5>
        </div>
        <div class="card-body">
            <h6>Data Summary:</h6>
            <ul>
                <li>Today's Trips: {site_data.get('total_trips', 0)}</li>
                <li>Total Weight: {site_data.get('total_net_weight', 0)} MT</li>
                <li>Historical Records: {site_data.get('total_historical_records', 0)}</li>
                <li>Completion: {site_data.get('completion_percentage', 0):.1f}%</li>
            </ul>
            
            <h6>Status:</h6>
            <p>{site_data.get('status_emoji', '')} {site_data.get('status', 'Unknown')}</p>
            
            <a href="/site/{site_name}" class="btn btn-primary">Back to Dashboard</a>
        </div>
    </div>
    """
    
    return create_standalone_html_response(f"Analytics: {site_name.title()}", content)

# Keep your existing debug and export routes - they return JSON so they're fine
@site_dashboard_bp.route('/<site_name>/export')
def export_site_data(site_name):
    """Export site data as JSON"""
    
    available_sites = get_sites_from_api()
    if site_name not in available_sites:
        return jsonify({'error': 'Site not found'}), 404
    
    target_date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    
    # Get raw records for the target date
    all_records, todays_records = get_all_site_records(site_name, target_date)
    
    response = {
        'site_name': site_name,
        'target_date': target_date,
        'export_timestamp': datetime.now().isoformat(),
        'todays_record_count': len(todays_records),
        'total_historical_records': len(all_records),
        'todays_records': todays_records,
        'historical_records_sample': all_records[-50:] if len(all_records) > 50 else all_records
    }
    
    return jsonify(response)

# Your debug routes can stay as they are since they return JSON
@site_dashboard_bp.route('/<site_name>/debug/api')
def debug_api_response(site_name):
    """Debug endpoint to check raw API response format"""
    
    try:
        base_url = "https://weighbridge-api-287877277037.asia-southeast1.run.app/records"
        params = {
            'site_name': site_name,
            'page': 1,
            'per_page': 10
        }
        
        response = requests.get(base_url, params=params, timeout=15)
        
        debug_info = {
            'url': base_url,
            'params': params,
            'status_code': response.status_code,
            'headers': dict(response.headers),
            'raw_response_preview': response.text[:1000] if response.text else 'No response text'
        }
        
        if response.status_code == 200:
            try:
                data = response.json()
                debug_info.update({
                    'json_keys': list(data.keys()),
                    'records_count': len(data.get('records', [])),
                    'pagination_info': data.get('pagination', {}),
                    'sample_record': data.get('records', [{}])[0] if data.get('records') else {},
                    'full_response': data
                })
            except Exception as json_error:
                debug_info['json_error'] = str(json_error)
        
        return jsonify(debug_info)
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'site_name': site_name,
            'debug_endpoint': True
        })