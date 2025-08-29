# simple_legacy_report.py
"""
Enhanced Legacy Report with Weighbridge Data Integration
"""

from flask import Blueprint, render_template, session, redirect, request, jsonify, send_file
import pandas as pd
from datetime import datetime
import json
import io
import os
import glob
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

# Create Blueprint
legacy_bp = Blueprint('legacy_report', __name__, url_prefix='/legacy')

def load_data():
    """Load weighbridge CSV data"""
    try:
        # Look for the most recent weighbridge CSV file
        csv_files = glob.glob('weighbridge_records_*.csv')
        
        if csv_files:
            # Sort by modification time to get the most recent
            latest_csv = max(csv_files, key=os.path.getmtime)
            print(f"Loading weighbridge data from: {latest_csv}")
            df = pd.read_csv(latest_csv)
        else:
            # Try different possible locations and names
            possible_files = [
                'weighbridge_records_last_2_dates_20250829_012603.csv',
                'data/weighbridge_records_*.csv',
                'weighbridge_data.csv',
                'data/weighbridge_data.csv'
            ]
            
            df = None
            for pattern in possible_files:
                if '*' in pattern:
                    files = glob.glob(pattern)
                    if files:
                        df = pd.read_csv(files[0])
                        print(f"Loading weighbridge data from: {files[0]}")
                        break
                else:
                    if os.path.exists(pattern):
                        df = pd.read_csv(pattern)
                        print(f"Loading weighbridge data from: {pattern}")
                        break
            
            if df is None:
                print("No weighbridge CSV files found - using sample data")
                return create_sample_weighbridge_data()
        
        # Convert date columns to datetime
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
        
        # Convert timestamp columns
        timestamp_columns = ['first_timestamp', 'second_timestamp', 'cloud_upload_timestamp', '_processed_timestamp']
        for col in timestamp_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Convert numeric columns
        numeric_columns = ['first_weight', 'second_weight', 'net_weight', 'net_weight_calculated']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        print(f"Loaded {len(df)} weighbridge records")
        return df
        
    except Exception as e:
        print(f"Error loading weighbridge data: {e}")
        return create_sample_weighbridge_data()

def create_sample_weighbridge_data():
    """Create sample weighbridge data if file not found"""
    import numpy as np
    
    # Create sample data matching your CSV structure
    n_records = 50
    
    data = {
        'date': pd.date_range('2025-08-27', periods=n_records, freq='H'),
        'time': ['12:00:00'] * n_records,
        'site_name': np.random.choice(['Bheemavaram', 'Eluru', 'Hindupur', 'Kurnool'], n_records),
        'cluster': np.random.choice(['Bheemavaram', 'Eluru', 'Hindupur', 'Kurnool'], n_records),
        'agency_name': np.random.choice(['Tharuni Associates', 'Saurashtra Enviro Projects'], n_records),
        'material': np.random.choice(['Legacy/MSW', 'Recyclables', 'Organic Waste'], n_records),
        'ticket_no': [f'T{3000+i}' for i in range(n_records)],
        'vehicle_no': np.random.choice(['AP37BG6795', 'AP27TU6165', 'AP21CV1234'], n_records),
        'transfer_party_name': ['On-site'] * n_records,
        'first_weight': np.random.randint(5000, 8000, n_records),
        'second_weight': np.random.randint(2000, 4000, n_records),
        'net_weight': np.random.randint(2000, 5000, n_records),
        'record_status': ['complete'] * n_records,
        'site_incharge': np.random.choice(['Manikanta', 'Rajesh', 'Suresh'], n_records),
        'user_name': ['admin'] * n_records,
        '_folder_source': np.random.choice(['Tharuni_Associates/Bheemavaram', 'Tharuni_Associates/Eluru'], n_records)
    }
    
    return pd.DataFrame(data)

def get_column_metadata(df):
    """Get metadata about columns for the UI"""
    columns = []
    
    # Define user-friendly names for weighbridge columns
    column_display_names = {
        'date': 'Date',
        'time': 'Time',
        'site_name': 'Site Name',
        'cluster': 'Cluster',
        'agency_name': 'Agency Name',
        'material': 'Material',
        'ticket_no': 'Ticket Number',
        'vehicle_no': 'Vehicle Number',
        'transfer_party_name': 'Transfer Party',
        'first_weight': 'First Weight (kg)',
        'first_timestamp': 'First Weighing Time',
        'second_weight': 'Second Weight (kg)',
        'second_timestamp': 'Second Weighing Time',
        'net_weight': 'Net Weight (kg)',
        'material_type': 'Material Type',
        'site_incharge': 'Site Incharge',
        'user_name': 'User Name',
        'cloud_upload_timestamp': 'Upload Time',
        'record_status': 'Status',
        'net_weight_calculated': 'Calculated Net Weight (kg)',
        '_source_file': 'Source File',
        '_processed_timestamp': 'Processed Time',
        '_folder_source': 'Folder Source'
    }
    
    for col in df.columns:
        col_info = {
            'name': col,
            'display_name': column_display_names.get(col, col.replace('_', ' ').title()),
            'type': str(df[col].dtype),
            'sample_value': str(df[col].iloc[0]) if not df.empty else '',
            'visible': col not in ['_source_file', '_processed_timestamp']  # Hide internal columns by default
        }
        columns.append(col_info)
    return columns

@legacy_bp.route('/report')
def legacy_report():
    """Main weighbridge report page"""
    if not session.get('swaccha_session_id'):
        return redirect('/login')
    
    user_data = session.get('user_data', {})
    user_name = user_data.get('name', 'User')
    
    print(f"Loading Weighbridge Report for user: {user_name}")
    
    # Load weighbridge data
    df = load_data()
    
    # Get filter options from actual data
    agencies = sorted(df['agency_name'].dropna().unique()) if 'agency_name' in df.columns else []
    clusters = sorted(df['cluster'].dropna().unique()) if 'cluster' in df.columns else []
    sites = sorted(df['site_name'].dropna().unique()) if 'site_name' in df.columns else []
    
    # Get column metadata
    column_metadata = get_column_metadata(df)
    
    # Apply filters from request
    filtered_df = apply_filters(df, request.args)
    
    # Get column preferences from session
    column_prefs = session.get('column_preferences', {})
    visible_columns = column_prefs.get('visible_columns', [col['name'] for col in column_metadata if col['visible']])
    column_order = column_prefs.get('column_order', list(df.columns))
    
    # Reorder and filter columns
    ordered_columns = [col for col in column_order if col in visible_columns and col in filtered_df.columns]
    if not ordered_columns:  # Fallback to main columns if none selected
        ordered_columns = ['date', 'time', 'site_name', 'agency_name', 'ticket_no', 'vehicle_no', 
                          'first_weight', 'second_weight', 'net_weight', 'record_status']
        ordered_columns = [col for col in ordered_columns if col in filtered_df.columns]
    
    display_df = filtered_df[ordered_columns] if ordered_columns else filtered_df
    
    # Calculate dynamic cards for weighbridge data
    cards_data = calculate_weighbridge_cards(filtered_df)
    
    # Format data for display
    records = []
    for _, row in display_df.iterrows():
        record = {}
        for col in ordered_columns:
            value = row[col]
            
            # Format different data types
            if pd.isna(value):
                record[col] = ''
            elif col in ['first_weight', 'second_weight', 'net_weight', 'net_weight_calculated']:
                record[col] = f"{value:,.1f}" if isinstance(value, (int, float)) else str(value)
            elif col == 'date':
                record[col] = value.strftime('%Y-%m-%d') if hasattr(value, 'strftime') else str(value)
            elif col in ['first_timestamp', 'second_timestamp', 'cloud_upload_timestamp']:
                record[col] = value.strftime('%Y-%m-%d %H:%M:%S') if hasattr(value, 'strftime') else str(value)
            else:
                record[col] = str(value)
        records.append(record)
    
    return render_template('legacy_report/simple_dashboard.html',
                         user_name=user_name,
                         records=records,
                         cards_data=cards_data,
                         agencies=agencies,
                         clusters=clusters,
                         sites=sites,
                         current_filters=request.args,
                         total_records=len(filtered_df),
                         column_metadata=column_metadata,
                         visible_columns=visible_columns,
                         column_order=column_order,
                         display_columns=ordered_columns,
                         current_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

@legacy_bp.route('/api/update-columns', methods=['POST'])
def update_column_preferences():
    """Update user's column preferences"""
    if not session.get('swaccha_session_id'):
        return jsonify({'error': 'Authentication required'}), 401
    
    data = request.get_json()
    visible_columns = data.get('visible_columns', [])
    column_order = data.get('column_order', [])
    
    # Store in session
    session['column_preferences'] = {
        'visible_columns': visible_columns,
        'column_order': column_order
    }
    
    return jsonify({'status': 'success'})

@legacy_bp.route('/api/export-pdf')
def export_pdf():
    """Export filtered weighbridge data as PDF"""
    if not session.get('swaccha_session_id'):
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        # Load and filter data
        df = load_data()
        filtered_df = apply_filters(df, request.args)
        
        # Get column preferences
        column_prefs = session.get('column_preferences', {})
        visible_columns = column_prefs.get('visible_columns', list(df.columns))
        column_order = column_prefs.get('column_order', list(df.columns))
        
        # Reorder and filter columns
        ordered_columns = [col for col in column_order if col in visible_columns and col in filtered_df.columns]
        if not ordered_columns:
            ordered_columns = ['date', 'site_name', 'ticket_no', 'vehicle_no', 'net_weight']
            ordered_columns = [col for col in ordered_columns if col in filtered_df.columns]
        
        display_df = filtered_df[ordered_columns] if ordered_columns else filtered_df
        
        # Create PDF
        pdf_buffer = create_pdf_report(display_df, request.args, is_weighbridge=True)
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'weighbridge_report_{timestamp}.pdf'
        
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        print(f"PDF export error: {e}")
        return jsonify({'error': str(e)}), 500

def create_pdf_report(df, filters, is_weighbridge=False):
    """Create PDF report from weighbridge dataframe"""
    buffer = io.BytesIO()
    
    # Create document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=1*inch,
        bottomMargin=0.5*inch
    )
    
    # Get styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        alignment=1,  # Center alignment
    )
    
    # Build content
    content = []
    
    # Title
    title_text = "Weighbridge Data Report" if is_weighbridge else "Legacy Report"
    title = Paragraph(f"{title_text} - Swachh Andhra Pradesh", title_style)
    content.append(title)
    
    # Filters summary
    filter_text = create_filter_summary(filters, is_weighbridge)
    if filter_text:
        filter_para = Paragraph(f"<b>Applied Filters:</b> {filter_text}", styles['Normal'])
        content.append(filter_para)
        content.append(Spacer(1, 12))
    
    # Summary stats
    stats_text = f"<b>Total Records:</b> {len(df)} | <b>Export Date:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    stats_para = Paragraph(stats_text, styles['Normal'])
    content.append(stats_para)
    content.append(Spacer(1, 20))
    
    # Prepare table data
    if not df.empty:
        # Select key columns for PDF
        pdf_columns = ['date', 'site_name', 'ticket_no', 'vehicle_no', 'net_weight', 'record_status']
        available_columns = [col for col in pdf_columns if col in df.columns]
        
        if len(available_columns) == 0:
            available_columns = list(df.columns)[:6]  # Take first 6 columns as fallback
        
        df_pdf = df[available_columns]
        
        # Create table data
        table_data = []
        
        # Headers
        headers = []
        for col in df_pdf.columns:
            if col == 'net_weight':
                headers.append('Net Weight (kg)')
            elif col == 'ticket_no':
                headers.append('Ticket No')
            elif col == 'vehicle_no':
                headers.append('Vehicle No')
            elif col == 'site_name':
                headers.append('Site')
            else:
                headers.append(col.replace('_', ' ').title())
        table_data.append(headers)
        
        # Data rows (limit to 50 rows for PDF)
        max_rows = 50
        for _, row in df_pdf.head(max_rows).iterrows():
            row_data = []
            for col, val in zip(df_pdf.columns, row):
                if pd.isna(val):
                    row_data.append('')
                elif col in ['net_weight', 'first_weight', 'second_weight']:
                    row_data.append(f"{val:,.1f}" if isinstance(val, (int, float)) else str(val))
                elif col == 'date':
                    row_data.append(val.strftime('%Y-%m-%d') if hasattr(val, 'strftime') else str(val))
                else:
                    row_data.append(str(val)[:20])  # Truncate long text
            table_data.append(row_data)
        
        if len(df) > max_rows:
            content.append(Paragraph(f"<i>Note: Showing first {max_rows} rows of {len(df)} total records</i>", styles['Italic']))
            content.append(Spacer(1, 12))
        
        # Create table
        table = Table(table_data, repeatRows=1)
        
        # Table style
        table.setStyle(TableStyle([
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Data styling
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            
            # Alternating row colors
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        
        content.append(table)
    else:
        content.append(Paragraph("No data available with current filters.", styles['Normal']))
    
    # Build PDF
    doc.build(content)
    buffer.seek(0)
    
    return buffer

def create_filter_summary(filters, is_weighbridge=False):
    """Create a summary of applied filters"""
    filter_parts = []
    
    if is_weighbridge:
        if filters.get('agency'):
            filter_parts.append(f"Agency: {filters['agency']}")
        if filters.get('cluster'):
            filter_parts.append(f"Cluster: {filters['cluster']}")
        if filters.get('site'):
            filter_parts.append(f"Site: {filters['site']}")
        if filters.get('start_date'):
            filter_parts.append(f"Start Date: {filters['start_date']}")
        if filters.get('end_date'):
            filter_parts.append(f"End Date: {filters['end_date']}")
        if filters.get('vehicle'):
            filter_parts.append(f"Vehicle: {filters['vehicle']}")
        if filters.get('status'):
            filter_parts.append(f"Status: {filters['status']}")
    else:
        # Original filters for legacy data
        if filters.get('agency'):
            filter_parts.append(f"Agency: {filters['agency']}")
        if filters.get('cluster'):
            filter_parts.append(f"Cluster: {filters['cluster']}")
        if filters.get('site'):
            filter_parts.append(f"Site: {filters['site']}")
        if filters.get('start_date'):
            filter_parts.append(f"Start Date: {filters['start_date']}")
        if filters.get('end_date'):
            filter_parts.append(f"End Date: {filters['end_date']}")
    
    return " | ".join(filter_parts) if filter_parts else "None"

def apply_filters(df, filters):
    """Apply filters to weighbridge dataframe"""
    filtered_df = df.copy()
    
    # Agency filter
    if filters.get('agency') and 'agency_name' in df.columns:
        filtered_df = filtered_df[filtered_df['agency_name'] == filters.get('agency')]
    
    # Cluster filter
    if filters.get('cluster') and 'cluster' in df.columns:
        filtered_df = filtered_df[filtered_df['cluster'] == filters.get('cluster')]
    
    # Site filter
    if filters.get('site') and 'site_name' in df.columns:
        filtered_df = filtered_df[filtered_df['site_name'] == filters.get('site')]
    
    # Date filters
    if filters.get('start_date') and 'date' in df.columns:
        start_date = pd.to_datetime(filters.get('start_date'))
        filtered_df = filtered_df[filtered_df['date'] >= start_date]
    
    if filters.get('end_date') and 'date' in df.columns:
        end_date = pd.to_datetime(filters.get('end_date'))
        filtered_df = filtered_df[filtered_df['date'] <= end_date]
    
    # Vehicle filter
    if filters.get('vehicle') and 'vehicle_no' in df.columns:
        filtered_df = filtered_df[filtered_df['vehicle_no'].str.contains(filters.get('vehicle'), case=False, na=False)]
    
    # Status filter
    if filters.get('status') and 'record_status' in df.columns:
        filtered_df = filtered_df[filtered_df['record_status'] == filters.get('status')]
    
    return filtered_df

def calculate_weighbridge_cards(df):
    """Calculate card values for weighbridge data with material type logic"""
    if len(df) == 0:
        return {
            'total_records': 0,
            'total_msw_received': 0,
            'total_output': 0,
            'unique_vehicles': 0
        }
    
    total_records = len(df)
    
    # Calculate Legacy/MSW total (sum of net_weight where material = 'Legacy/MSW')
    if 'material' in df.columns and 'net_weight' in df.columns:
        legacy_msw_mask = df['material'].str.contains('Legacy/MSW', case=False, na=False)
        total_msw_kg = df.loc[legacy_msw_mask, 'net_weight'].sum()
        
        # Calculate Other Materials total (sum of net_weight where material != 'Legacy/MSW')
        other_materials_mask = ~legacy_msw_mask & df['net_weight'].notna()
        total_output_kg = df.loc[other_materials_mask, 'net_weight'].sum()
        
        # Convert from kg to metric tonnes (divide by 1000)
        total_msw = total_msw_kg / 1000
        total_output = total_output_kg / 1000
    else:
        # Fallback if columns don't exist
        total_weight_kg = df['net_weight'].sum() if 'net_weight' in df.columns else 0
        total_msw = total_weight_kg / 1000
        total_output = 0
    
    # Count unique vehicles (changed from total trips to unique vehicles)
    unique_vehicles = df['vehicle_no'].nunique() if 'vehicle_no' in df.columns else 0
    
    return {
        'total_records': total_records,
        'total_msw_received': round(total_msw, 2),  # Round to 2 decimal places for tonnes
        'total_output': round(total_output, 2),     # Round to 2 decimal places for tonnes
        'unique_vehicles': unique_vehicles
    }

@legacy_bp.route('/logout')
def logout():
    """Logout route - clears session and redirects to main page"""
    try:
        # Get user info before clearing session
        user_data = session.get('user_data', {})
        user_name = user_data.get('name', 'User')
        
        print(f"DEBUG: Logout initiated for user: {user_name}")
        
        # Clear all session data
        session.clear()
        
        print("DEBUG: Session cleared - redirecting to main page")
        
        # Redirect to main page with logout success message
        return redirect('/?logout=success')
        
    except Exception as e:
        print(f"ERROR: Logout failed: {e}")
        # Force redirect even if there's an error
        session.clear()
        return redirect('/')

# API endpoint for logout
@legacy_bp.route('/api/logout', methods=['POST'])
def api_logout():
    """API endpoint for logout"""
    try:
        user_data = session.get('user_data', {})
        user_name = user_data.get('name', 'User')
        
        print(f"DEBUG: API logout for user: {user_name}")
        
        # Clear session
        session.clear()
        
        return jsonify({
            'success': True,
            'message': 'Logged out successfully',
            'redirect_url': '/'
        })
        
    except Exception as e:
        print(f"ERROR: API logout failed: {e}")
        session.clear()  # Clear session anyway
        return jsonify({
            'success': True,  # Still return success to ensure redirect
            'message': 'Logged out',
            'redirect_url': '/'
        })

if __name__ == "__main__":
    print("Loading Weighbridge Report System")
    print("Updated for real weighbridge data integration")
    
    # Test data loading
    df = load_data()
    print(f"Loaded {len(df)} weighbridge records")
    print(f"Columns: {list(df.columns)}")
    
    if not df.empty:
        print(f"Date range: {df['date'].min()} to {df['date'].max()}")
        if 'site_name' in df.columns:
            print(f"Sites: {list(df['site_name'].unique())}")
        if 'agency_name' in df.columns:
            print(f"Agencies: {list(df['agency_name'].unique())}")