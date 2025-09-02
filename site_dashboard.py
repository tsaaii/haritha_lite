# site_dashboard.py - Flask Blueprint for Site Dashboards
"""
Site Dashboard Flask Blueprint
Fetches real data from weighbridge API and displays site-specific dashboards
Enhanced with pagination support and day-specific totals
"""

from flask import Blueprint, render_template, request, session, redirect, jsonify, url_for
from datetime import datetime, timedelta
import requests
from collections import defaultdict
import logging

# Create blueprint for site dashboard routes
site_dashboard_bp = Blueprint('site_dashboard', __name__, url_prefix='/site')

def get_sites_from_api():
    """Get sites from API with fallback"""
    try:
        response = requests.get("https://weighbridge-api-287877277037.asia-southeast1.run.app/sites", timeout=10)
        if response.status_code == 200:
            data = response.json()
            return sorted(data.get("sites", []))
    except Exception as e:
        logging.error(f"Error fetching sites: {e}")
    return ["Adoni", "Bheemavaram", "Nandyal", "Yemmiganur"]

def get_site_info_from_api(site_name):
    """
    Get site-specific information from the site info API
    
    Args:
        site_name (str): Name of the site
        
    Returns:
        dict: Site information data
    """
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
    """
    Get ALL records for a specific site from the weighbridge API with pagination support
    
    Args:
        site_name (str): Name of the site
        target_date (str): Specific date to filter records (YYYY-MM-DD format). If None, gets recent records.
        
    Returns:
        tuple: (all_records_list, todays_records_list)
    """
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

def get_site_records(site_name, days_back=7):
    """
    Backward compatibility function - gets recent records
    """
    all_records, todays_records = get_all_site_records(site_name)
    
    # Filter for recent records (last N days)
    cutoff_date = datetime.now() - timedelta(days=days_back)
    cutoff_str = cutoff_date.strftime('%Y-%m-%d')
    
    recent_records = [r for r in all_records if r.get('date', '') >= cutoff_str]
    return recent_records

def process_site_data(site_name, target_date=None):
    """
    Process weighbridge records to calculate site statistics
    Now focuses on day-specific totals with historical data for context
    Also fetches site-specific information from the site info API
    
    Args:
        site_name (str): Name of the site
        target_date (str): Target date for calculations (defaults to today)
        
    Returns:
        dict: Processed site data with statistics
    """
    if target_date is None:
        target_date = datetime.now().strftime('%Y-%m-%d')
    
    # Get site-specific information from the new API
    site_info = get_site_info_from_api(site_name)
    
    # Get all records and today's records from weighbridge API
    all_records, todays_records = get_all_site_records(site_name, target_date)
    
    print(f"DEBUG: Processing {len(all_records)} total records, {len(todays_records)} for {target_date}")
    
    # DEBUGGING: Let's see what dates we have in all records
    if all_records:
        date_counts = defaultdict(int)
        for record in all_records:
            date = record.get('date', 'NO_DATE')
            date_counts[date] += 1
        
        print(f"DEBUG: Date distribution in all records:")
        for date, count in sorted(date_counts.items()):
            print(f"  {date}: {count} records")
        print(f"DEBUG: Target date '{target_date}' has {date_counts.get(target_date, 0)} records")
    
    # Default response structure with correct field names
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
        'historical_summary': {
            'total_historical_records': 0,
            'date_range': 'No data'
        },
        # Site info defaults - using correct field names from API
        'agency': 'Not available',
        'contractor': 'Not available',  # This maps to sub_contractor from API
        'cluster': 'Not available',     # This maps to cluster_name from API
        'cluster_name': 'Not available',
        'sub_contractor': 'Not available',
        'total_quantity_given': 0,      # This maps to quantity_to_be_remediated
        'quantity_to_be_remediated': 0,
        'total_remediated': 0,          # This maps to cumulative_quantity_remediated
        'cumulative_quantity_remediated': 0,
        'net_to_be_remediated': 0,
        'quantity_remediated_today': 0,
        'completion_percentage': 0,
        'target_quantity_per_day': 0,
        'target_percentage_per_day': 0, # Calculated from target_quantity_per_day
        'days_remaining': 0,
        'progress_offset': 283
    }
    
    # Merge site info data into response with correct field mappings
    if site_info:
        # Direct mappings from site API
        base_response.update({
            'agency': site_info.get('agency', 'Not available'),
            'cluster_name': site_info.get('cluster_name', 'Not available'),
            'sub_contractor': site_info.get('sub_contractor', 'Not available'),
            'quantity_to_be_remediated': site_info.get('quantity_to_be_remediated', 0),
            'cumulative_quantity_remediated': site_info.get('cumulative_quantity_remediated', 0),
            'net_to_be_remediated': site_info.get('net_to_be_remediated', 0),
            'quantity_remediated_today': site_info.get('quantity_remediated_today', 0),
            'completion_percentage': site_info.get('completion_percentage', 0),
            'target_quantity_per_day': site_info.get('target_quantity_per_day', 0),
            'days_remaining': site_info.get('days_remaining', 0)
        })
        
        # Template-friendly mappings (what the HTML template expects)
        base_response.update({
            'contractor': site_info.get('sub_contractor', 'Not available'),  # Template expects 'contractor'
            'cluster': site_info.get('cluster_name', 'Not available'),       # Template expects 'cluster'  
            'total_quantity_given': site_info.get('quantity_to_be_remediated', 0),  # Template expects this
            'total_remediated': site_info.get('cumulative_quantity_remediated', 0)  # Template expects this
        })
        
        # Calculate target percentage per day if we have the data
        total_quantity = site_info.get('quantity_to_be_remediated', 0)
        target_per_day = site_info.get('target_quantity_per_day', 0)
        if total_quantity > 0 and target_per_day > 0:
            target_percentage_per_day = (target_per_day / total_quantity) * 100
            base_response['target_percentage_per_day'] = round(target_percentage_per_day, 2)
        
        # Calculate progress offset for circular progress bar (283 is full circle circumference)
        completion_percentage = site_info.get('completion_percentage', 0)
        progress_offset = 283 - (283 * (completion_percentage / 100))
        base_response['progress_offset'] = round(progress_offset, 2)
    
    if not all_records:
        return base_response
    
    # ========================================
    # TODAY'S/TARGET DATE CALCULATIONS (TOTALS)
    # ========================================
    
    # Initialize TODAY'S counters (these are the main "totals")
    total_trips = len(todays_records)  # TODAY'S trips
    total_inward = 0.0   # TODAY'S inward weight
    total_outward = 0.0  # TODAY'S outward weight  
    total_net_weight = 0.0  # TODAY'S total weight
    
    # TODAY'S recent vehicles and hourly activity
    recent_vehicles = []
    hourly_activity = defaultdict(int)
    todays_material_breakdown = defaultdict(lambda: {'count': 0, 'weight': 0.0})
    
    # Process TODAY'S records for main statistics
    for record in todays_records:
        try:
            net_weight = float(record.get('net_weight', 0))
            material = record.get('material', '').strip()
            time = record.get('time', '')
            vehicle_no = record.get('vehicle_no', '')
            ticket_no = record.get('ticket_no', '')
            date = record.get('date', '')
            
            # Add to today's totals
            total_net_weight += net_weight
            
            # Classify as inward or outward based on material
            if material == "Legacy/MSW":
                total_inward += net_weight
            else:
                total_outward += net_weight
            
            # Today's material breakdown
            todays_material_breakdown[material]['count'] += 1
            todays_material_breakdown[material]['weight'] += net_weight
            
            # Hourly activity for today
            if time:
                try:
                    hour = int(time.split(':')[0])
                    hourly_activity[hour] += 1
                except:
                    pass
            
            # Recent vehicles (from today) - collect all data for sorting later
            recent_vehicles.append({
                'vehicle_no': vehicle_no,
                'ticket_no': ticket_no,
                'time': time,
                'weight': net_weight,
                'material': material,
                'date': date,
                'datetime_str': f"{date} {time}" if date and time else f"{date} 00:00:00"
            })
        
        except Exception as e:
            print(f"ERROR: Failed to process today's record: {e}")
            continue
    
    # Sort recent vehicles by time (most recent first) and take only the latest 10
    try:
        # Sort by datetime string in descending order (most recent first)
        recent_vehicles.sort(key=lambda x: x.get('datetime_str', ''), reverse=True)
        recent_vehicles = recent_vehicles[:10]  # Take top 10 most recent
        
        print(f"DEBUG: Recent vehicles after sorting:")
        for i, vehicle in enumerate(recent_vehicles[:3]):  # Show first 3
            print(f"  {i+1}. {vehicle['vehicle_no']} at {vehicle['datetime_str']}")
            
    except Exception as e:
        print(f"ERROR: Failed to sort recent vehicles: {e}")
        recent_vehicles = recent_vehicles[:10]  # Fallback to first 10
    
    # FALLBACK: If no vehicles from today, get recent vehicles from ALL records
    if not recent_vehicles and all_records:
        print(f"DEBUG: No vehicles found for {target_date}, getting recent vehicles from all records")
        fallback_vehicles = []
        
        for record in all_records:
            try:
                fallback_vehicles.append({
                    'vehicle_no': record.get('vehicle_no', ''),
                    'ticket_no': record.get('ticket_no', ''),
                    'time': record.get('time', ''),
                    'weight': float(record.get('net_weight', 0)),
                    'material': record.get('material', '').strip(),
                    'date': record.get('date', ''),
                    'datetime_str': f"{record.get('date', '')} {record.get('time', '')}" if record.get('date') and record.get('time') else f"{record.get('date', '')} 00:00:00"
                })
            except:
                continue
        
        try:
            # Sort all vehicles by datetime (most recent first) and take top 10
            fallback_vehicles.sort(key=lambda x: x.get('datetime_str', ''), reverse=True)
            recent_vehicles = fallback_vehicles[:10]
            
            print(f"DEBUG: Using {len(recent_vehicles)} fallback vehicles from all historical records")
            
        except Exception as e:
            print(f"ERROR: Failed to sort fallback vehicles: {e}")
            recent_vehicles = fallback_vehicles[:10]
    
    # ========================================
    # HISTORICAL DATA FOR CONTEXT
    # ========================================
    
    historical_material_breakdown = defaultdict(lambda: {'count': 0, 'weight': 0.0})
    daily_activity = defaultdict(int)
    
    # Process ALL records for historical context
    for record in all_records:
        try:
            material = record.get('material', '').strip()
            date = record.get('date', '')
            net_weight = float(record.get('net_weight', 0))
            
            # Historical material breakdown
            historical_material_breakdown[material]['count'] += 1
            historical_material_breakdown[material]['weight'] += net_weight
            
            # Daily activity over time
            daily_activity[date] += 1
            
        except Exception as e:
            print(f"ERROR: Failed to process historical record: {e}")
            continue
    
    # ========================================
    # CALCULATIONS AND STATUS
    # ========================================
    
    # Calculate averages and percentages (based on TODAY'S data)
    avg_weight_per_trip = total_net_weight / total_trips if total_trips > 0 else 0
    inward_percentage = (total_inward / total_net_weight * 100) if total_net_weight > 0 else 0
    outward_percentage = (total_outward / total_net_weight * 100) if total_net_weight > 0 else 0
    
    # Determine site status (based on TODAY'S activity)
    if total_trips > 0:
        status = 'Active'
        status_emoji = '🟢'
    elif len(all_records) > 0:
        status = 'No activity today'
        status_emoji = '🟡'
    else:
        status = 'Offline'
        status_emoji = '🔴'
    
    # Generate enhanced alerts based on both weighbridge and site info data
    alerts = []
    if total_trips == 0:
        alerts.append(f"No weighbridge transactions recorded on {target_date}")
    elif total_trips < 10:
        alerts.append(f"Low weighbridge activity: Only {total_trips} trips on {target_date}")
    else:
        alerts.append(f"Active weighbridge: {total_trips} trips completed on {target_date}")
    
    # Add site progress alerts
    if site_info:
        completion_pct = site_info.get('completion_percentage', 0)
        days_remaining = site_info.get('days_remaining', 0)
        quantity_today = site_info.get('quantity_remediated_today', 0)
        target_per_day = site_info.get('target_quantity_per_day', 0)
        
        if completion_pct >= 75:
            alerts.append(f"Project nearly complete: {completion_pct:.1f}% finished")
        elif completion_pct >= 50:
            alerts.append(f"Project halfway done: {completion_pct:.1f}% completed")
        elif completion_pct < 25:
            alerts.append(f"Early stage: {completion_pct:.1f}% completed")
        
        if days_remaining <= 7:
            alerts.append(f"Urgent: Only {days_remaining} days remaining")
        elif days_remaining <= 14:
            alerts.append(f"Approaching deadline: {days_remaining} days left")
        
        if quantity_today > target_per_day:
            alerts.append(f"Exceeded daily target: {quantity_today:.0f} MT vs {target_per_day:.0f} MT target")
        elif quantity_today < target_per_day * 0.5:
            alerts.append(f"Behind daily target: {quantity_today:.0f} MT vs {target_per_day:.0f} MT target")
    
    # Material flow analysis
    if total_inward > total_outward:
        alerts.append(f"More inward material today: {inward_percentage:.1f}% vs {outward_percentage:.1f}%")
    elif total_outward > total_inward:
        alerts.append(f"More outward material today: {outward_percentage:.1f}% vs {inward_percentage:.1f}%")
    else:
        alerts.append("Balanced inward/outward material today")
    
    # Historical data range
    if all_records:
        dates = [r.get('date') for r in all_records if r.get('date')]
        if dates:
            min_date = min(dates)
            max_date = max(dates)
            data_range = f"{min_date} to {max_date}"
        else:
            data_range = "Date information unavailable"
    else:
        data_range = "No data"
    
    # Final comprehensive return with all data
    return {
        'site_name': site_name,
        'target_date': target_date,
        'status': status,
        'status_emoji': status_emoji,
        
        # Site Information (using both original API keys and template-friendly names)
        'agency': base_response['agency'],
        'contractor': base_response['contractor'],  # Template expects this
        'cluster': base_response['cluster'],        # Template expects this
        'cluster_name': base_response['cluster_name'], 
        'sub_contractor': base_response['sub_contractor'],
        'total_quantity_given': base_response['total_quantity_given'],  # Template expects this
        'quantity_to_be_remediated': base_response['quantity_to_be_remediated'],
        'total_remediated': base_response['total_remediated'],          # Template expects this
        'cumulative_quantity_remediated': base_response['cumulative_quantity_remediated'],
        'net_to_be_remediated': base_response['net_to_be_remediated'],
        'quantity_remediated_today': base_response['quantity_remediated_today'],
        'completion_percentage': base_response['completion_percentage'],
        'target_quantity_per_day': base_response['target_quantity_per_day'],
        'target_percentage_per_day': base_response['target_percentage_per_day'], # Template expects this
        'days_remaining': base_response['days_remaining'],
        'progress_offset': base_response['progress_offset'],
        
        # TODAY'S TRIP COUNTS AND WEIGHTS (MAIN TOTALS from weighbridge)
        'total_trips': total_trips,  # TODAY'S trips
        'total_inward': round(total_inward / 1000, 2),  # TODAY'S inward (MT)
        'total_outward': round(total_outward / 1000, 2), # TODAY'S outward (MT)
        'total_net_weight': round(total_net_weight / 1000, 2), # TODAY'S total (MT)
        
        # TODAY'S averages and percentages
        'avg_weight_per_trip': round(avg_weight_per_trip / 1000, 2), # TODAY'S average (MT)
        'inward_percentage': round(inward_percentage, 1),
        'outward_percentage': round(outward_percentage, 1),
        
        # TODAY'S detailed data
        'recent_vehicles': recent_vehicles,  # Already limited to 10 most recent after sorting
        'material_breakdown': dict(todays_material_breakdown),  # TODAY'S materials
        'hourly_activity': dict(hourly_activity),  # TODAY'S hourly pattern
        
        # HISTORICAL CONTEXT
        'historical_material_breakdown': dict(historical_material_breakdown),
        'daily_activity': dict(daily_activity),  # Activity over time
        
        # Meta information
        'last_updated': datetime.now().strftime('%H:%M:%S'),
        'data_range': data_range,
        'alerts': alerts,
        'todays_record_count': len(todays_records),
        'total_historical_records': len(all_records),
        'recent_vehicles_source': 'today' if any(v.get('date') == target_date for v in recent_vehicles) else 'historical',
        'recent_vehicles_count': len(recent_vehicles),
        
        # Summary for historical context
        'historical_summary': {
            'total_historical_records': len(all_records),
            'date_range': data_range,
            'unique_dates': len(set(r.get('date', '') for r in all_records if r.get('date')))
        }
    }

@site_dashboard_bp.route('/')
def site_list():
    """Show list of available sites"""
    sites = get_sites_from_api()
    return render_template('site_list.html', sites=sites)

@site_dashboard_bp.route('/<site_name>')
def site_dashboard(site_name):
    """Main site dashboard route"""
    
    # Validate site name
    available_sites = get_sites_from_api()
    if site_name not in available_sites:
        return render_template('site_not_found.html', 
                             site_name=site_name, 
                             available_sites=available_sites), 404
    
    # Get target date from query params (defaults to today)
    target_date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    
    print(f"DEBUG: Loading dashboard for site: {site_name}, date: {target_date}")
    
    # Get processed site data for the target date
    site_data = process_site_data(site_name, target_date)
    
    return render_template('site_dashboard.html', **site_data)

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
    
    available_sites = get_sites_from_api()
    if site_name not in available_sites:
        return render_template('site_not_found.html', 
                             site_name=site_name, 
                             available_sites=available_sites), 404
    
    target_date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    site_data = process_site_data(site_name, target_date)
    return render_template('site_analytics.html', **site_data)

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
        'historical_records_sample': all_records[-50:] if len(all_records) > 50 else all_records  # Last 50 for sample
    }
    
    return jsonify(response)

@site_dashboard_bp.route('/<site_name>/debug/api')
def debug_api_response(site_name):
    """Debug endpoint to check raw API response format"""
    
    try:
        base_url = "https://weighbridge-api-287877277037.asia-southeast1.run.app/records"
        params = {
            'site_name': site_name,
            'page': 1,
            'per_page': 10  # Small sample for debugging
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

@site_dashboard_bp.route('/<site_name>/debug/records')
def debug_records_processing(site_name):
    """Debug endpoint to see how records are being processed"""
    
    target_date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    
    try:
        # Get all records and today's records
        all_records, todays_records = get_all_site_records(site_name, target_date)
        
        # Analyze date distribution
        date_counts = defaultdict(int)
        date_samples = defaultdict(list)
        
        for i, record in enumerate(all_records):
            date = record.get('date', 'NO_DATE')
            date_counts[date] += 1
            
            # Keep first 3 records as samples for each date
            if len(date_samples[date]) < 3:
                date_samples[date].append({
                    'index': i,
                    'date': date,
                    'time': record.get('time', ''),
                    'vehicle_no': record.get('vehicle_no', ''),
                    'ticket_no': record.get('ticket_no', ''),
                    'net_weight': record.get('net_weight', ''),
                    'material': record.get('material', ''),
                })
        
        debug_data = {
            'site_name': site_name,
            'target_date': target_date,
            'today_date': datetime.now().strftime('%Y-%m-%d'),
            'summary': {
                'total_records_from_api': len(all_records),
                'todays_records_filtered': len(todays_records),
                'difference': len(all_records) - len(todays_records),
                'unique_dates_in_data': len(date_counts)
            },
            'date_distribution': dict(date_counts),
            'date_samples': {date: samples for date, samples in date_samples.items()},
            'first_10_records': all_records[:10] if all_records else [],
            'target_date_records_sample': todays_records[:5] if todays_records else []
        }
        
        return jsonify(debug_data)
        
    except Exception as e:
        import traceback
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc(),
            'site_name': site_name,
            'target_date': target_date
        })

@site_dashboard_bp.route('/<site_name>/debug/vehicles')
def debug_recent_vehicles(site_name):
    """Debug endpoint specifically for recent vehicles data"""
    
    target_date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    
    try:
        # Get all records and today's records
        all_records, todays_records = get_all_site_records(site_name, target_date)
        
        # Process vehicles from today's records (similar to main function)
        vehicles_data = []
        
        for i, record in enumerate(todays_records):
            try:
                vehicle_info = {
                    'index': i,
                    'vehicle_no': record.get('vehicle_no', ''),
                    'ticket_no': record.get('ticket_no', ''),
                    'time': record.get('time', ''),
                    'date': record.get('date', ''),
                    'weight': record.get('net_weight', 0),
                    'material': record.get('material', ''),
                    'datetime_str': f"{record.get('date', '')} {record.get('time', '')}" if record.get('date') and record.get('time') else f"{record.get('date', '')} 00:00:00",
                    'raw_record': record  # Include full record for debugging
                }
                vehicles_data.append(vehicle_info)
                
            except Exception as e:
                vehicles_data.append({
                    'index': i,
                    'error': str(e),
                    'raw_record': record
                })
        
        # Sort by datetime (most recent first)
        try:
            vehicles_data.sort(key=lambda x: x.get('datetime_str', ''), reverse=True)
        except Exception as e:
            print(f"Sort error: {e}")
        
        debug_info = {
            'site_name': site_name,
            'target_date': target_date,
            'summary': {
                'total_records_for_date': len(todays_records),
                'vehicles_processed': len(vehicles_data),
                'has_vehicles': len(vehicles_data) > 0
            },
            'all_vehicles_today': vehicles_data,
            'top_10_recent': vehicles_data[:10],
            'time_analysis': {
                'earliest_time': min([v.get('datetime_str', '') for v in vehicles_data]) if vehicles_data else 'No data',
                'latest_time': max([v.get('datetime_str', '') for v in vehicles_data]) if vehicles_data else 'No data',
                'unique_times': len(set(v.get('datetime_str', '') for v in vehicles_data))
            },
            'potential_issues': []
        }
        
        # Identify potential issues
        if len(todays_records) == 0:
            debug_info['potential_issues'].append(f"No records found for {target_date}")
        elif len(vehicles_data) == 0:
            debug_info['potential_issues'].append("Records exist but no vehicle data could be processed")
        elif all(not v.get('time') for v in vehicles_data):
            debug_info['potential_issues'].append("All records missing time information")
        elif all(not v.get('vehicle_no') for v in vehicles_data):
            debug_info['potential_issues'].append("All records missing vehicle number information")
        
        return jsonify(debug_info)
        
    except Exception as e:
        import traceback
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc(),
            'site_name': site_name,
            'target_date': target_date
        })

@site_dashboard_bp.route('/<site_name>/debug/comparison')
def debug_comparison(site_name):
    """Compare API raw data vs dashboard processed data"""
    
    target_date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    
    try:
        # 1. Get raw API response (first page)
        base_url = "https://weighbridge-api-287877277037.asia-southeast1.run.app/records"
        params = {'site_name': site_name, 'page': 1, 'per_page': 100}
        raw_response = requests.get(base_url, params=params, timeout=15)
        raw_data = raw_response.json() if raw_response.status_code == 200 else {}
        
        # 2. Get processed dashboard data
        dashboard_data = process_site_data(site_name, target_date)
        
        # 3. Compare
        comparison = {
            'raw_api_data': {
                'status_code': raw_response.status_code,
                'total_records_in_response': len(raw_data.get('records', [])),
                'pagination': raw_data.get('pagination', {}),
                'sample_records': raw_data.get('records', [])[:5]
            },
            'dashboard_processed_data': {
                'total_trips_shown': dashboard_data.get('total_trips', 0),
                'target_date': dashboard_data.get('target_date'),
                'total_historical_records': dashboard_data.get('total_historical_records', 0),
                'todays_record_count': dashboard_data.get('todays_record_count', 0)
            },
            'analysis': {
                'issue_identified': len(raw_data.get('records', [])) != dashboard_data.get('total_trips', 0),
                'likely_cause': 'Dashboard shows only target date records, API shows all records',
                'explanation': f"API returned {len(raw_data.get('records', []))} records from all dates, but dashboard filtered to {dashboard_data.get('total_trips', 0)} records for {target_date}"
            }
        }
        
        return jsonify(comparison)
        
    except Exception as e:
        import traceback
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        })

def refresh_api_data():
    """Trigger data refresh on the weighbridge API"""
    try:
        refresh_url = "https://weighbridge-api-287877277037.asia-southeast1.run.app/refresh"
        response = requests.post(refresh_url, timeout=30)
        
        if response.status_code == 200:
            print("Data refresh triggered successfully")
            return True, response.json() if response.text else {'status': 'success'}
        else:
            print(f"Refresh failed with status: {response.status_code}")
            return False, response.text
    except Exception as e:
        print(f"Error triggering refresh: {e}")
        return False, str(e)

@site_dashboard_bp.route('/admin/refresh', methods=['POST'])
def admin_refresh():
    """Admin endpoint to refresh data"""
    success, result = refresh_api_data()
    
    if success:
        return jsonify({
            'status': 'success',
            'message': 'Data refresh triggered successfully',
            'result': result
        })
    else:
        return jsonify({
            'status': 'error', 
            'message': 'Failed to trigger data refresh',
            'error': result
        }), 500