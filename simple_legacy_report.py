# simple_legacy_report.py
"""
Enhanced Legacy Report with Column Management and PDF Export
"""

from flask import Blueprint, render_template, session, redirect, request, jsonify, send_file
import pandas as pd
from datetime import datetime
import json
import io
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

# Create Blueprint
legacy_bp = Blueprint('legacy_report', __name__, url_prefix='/legacy')

def load_data():
    """Load CSV data with your headers"""
    try:
        df = pd.read_csv('data/waste_data.csv')  # Update path as needed
        
        # Ensure date columns are datetime
        date_columns = ['start_date', 'planned_end_date', 'expected_end_date']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
            
        return df
    except FileNotFoundError:
        return create_sample_data()

def create_sample_data():
    """Create sample data matching your CSV structure"""
    import numpy as np
    
    agencies = ['Agency A', 'Agency B', 'Agency C']
    contractors = ['Contractor 1', 'Contractor 2', 'Contractor 3']
    clusters = ['Cluster North', 'Cluster South', 'Cluster East', 'Cluster West']
    sites = ['Site 1', 'Site 2', 'Site 3', 'Site 4', 'Site 5']
    machines = ['Machine A', 'Machine B', 'Machine C']
    
    n_records = 100
    
    data = {
        'Agency': np.random.choice(agencies, n_records),
        'Sub/contractor': np.random.choice(contractors, n_records),
        'Cluster': np.random.choice(clusters, n_records),
        'Site': np.random.choice(sites, n_records),
        'Machine': np.random.choice(machines, n_records),
        'Daily_Capacity': np.random.randint(10, 100, n_records),
        'start_date': pd.date_range('2024-01-01', periods=n_records, freq='D'),
        'planned_end_date': pd.date_range('2024-06-01', periods=n_records, freq='D'),
        'expected_end_date': pd.date_range('2024-07-01', periods=n_records, freq='D'),
        'days_to_sept30': np.random.randint(30, 150, n_records),
        'Quantity to be remediated in MT': np.random.randint(50, 500, n_records),
        'Cumulative Quantity remediated till date in MT': np.random.randint(20, 300, n_records),
        'Active_site': np.random.choice(['Yes', 'No'], n_records),
        'net_to_be_remediated_mt': np.random.randint(10, 200, n_records),
        'days_required': np.random.randint(5, 60, n_records),
        'Quantity remediated today': np.random.randint(0, 50, n_records)
    }
    
    return pd.DataFrame(data)

def get_column_metadata(df):
    """Get metadata about columns for the UI"""
    columns = []
    for col in df.columns:
        col_info = {
            'name': col,
            'display_name': col.replace('_', ' ').title(),
            'type': str(df[col].dtype),
            'sample_value': str(df[col].iloc[0]) if not df.empty else '',
            'visible': True  # Default to visible
        }
        columns.append(col_info)
    return columns

@legacy_bp.route('/report')
def legacy_report():
    """Main legacy report page with column management"""
    if not session.get('swaccha_session_id'):
        return redirect('/login')
    
    user_data = session.get('user_data', {})
    user_name = user_data.get('name', 'User')
    
    print(f"🎉 Hello from Legacy Report! User: {user_name}")
    
    # Load data
    df = load_data()
    
    # Get filter options
    agencies = sorted(df['Agency'].unique()) if 'Agency' in df.columns else []
    clusters = sorted(df['Cluster'].unique()) if 'Cluster' in df.columns else []
    sites = sorted(df['Site'].unique()) if 'Site' in df.columns else []
    
    # Get column metadata
    column_metadata = get_column_metadata(df)
    
    # Apply filters from request
    filtered_df = apply_filters(df, request.args)
    
    # Get column preferences from session
    column_prefs = session.get('column_preferences', {})
    visible_columns = column_prefs.get('visible_columns', list(df.columns))
    column_order = column_prefs.get('column_order', list(df.columns))
    
    # Reorder and filter columns
    ordered_columns = [col for col in column_order if col in visible_columns and col in filtered_df.columns]
    display_df = filtered_df[ordered_columns] if ordered_columns else filtered_df
    
    # Calculate dynamic cards
    cards_data = calculate_cards(filtered_df)
    
    # Convert to records for template
    records = display_df.to_dict('records')
    
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
    """Export filtered data as PDF"""
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
        display_df = filtered_df[ordered_columns] if ordered_columns else filtered_df
        
        # Create PDF
        pdf_buffer = create_pdf_report(display_df, request.args)
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'legacy_report_{timestamp}.pdf'
        
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        print(f"PDF export error: {e}")
        return jsonify({'error': str(e)}), 500

def create_pdf_report(df, filters):
    """Create PDF report from dataframe"""
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
    title = Paragraph("🎉 Legacy Report - स्वच्छ आंध्र प्रदेश", title_style)
    content.append(title)
    
    # Filters summary
    filter_text = create_filter_summary(filters)
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
        # Limit columns for PDF (max 8 columns to fit page)
        max_cols = 8
        if len(df.columns) > max_cols:
            df_pdf = df.iloc[:, :max_cols]
            content.append(Paragraph(f"<i>Note: Showing first {max_cols} columns due to page width constraints</i>", styles['Italic']))
            content.append(Spacer(1, 12))
        else:
            df_pdf = df
        
        # Create table data
        table_data = []
        
        # Headers
        headers = [col.replace('_', ' ').title()[:15] for col in df_pdf.columns]  # Truncate long headers
        table_data.append(headers)
        
        # Data rows (limit to 50 rows for PDF)
        max_rows = 50
        for _, row in df_pdf.head(max_rows).iterrows():
            row_data = []
            for val in row:
                if pd.isna(val):
                    row_data.append('')
                elif isinstance(val, (int, float)):
                    row_data.append(str(val))
                else:
                    # Truncate long text
                    row_data.append(str(val)[:20])
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

def create_filter_summary(filters):
    """Create a summary of applied filters"""
    filter_parts = []
    
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
    """Apply filters to dataframe"""
    filtered_df = df.copy()
    
    if filters.get('agency') and 'Agency' in df.columns:
        filtered_df = filtered_df[filtered_df['Agency'] == filters.get('agency')]
    
    if filters.get('cluster') and 'Cluster' in df.columns:
        filtered_df = filtered_df[filtered_df['Cluster'] == filters.get('cluster')]
    
    if filters.get('site') and 'Site' in df.columns:
        filtered_df = filtered_df[filtered_df['Site'] == filters.get('site')]
    
    if filters.get('start_date') and 'start_date' in df.columns:
        start_date = pd.to_datetime(filters.get('start_date'))
        filtered_df = filtered_df[filtered_df['start_date'] >= start_date]
    
    if filters.get('end_date') and 'start_date' in df.columns:
        end_date = pd.to_datetime(filters.get('end_date'))
        filtered_df = filtered_df[filtered_df['start_date'] <= end_date]
    
    return filtered_df

def calculate_cards(df):
    """Calculate dynamic card values"""
    if len(df) == 0:
        return {
            'total_records': 0,
            'total_msw_received': 0,
            'total_output': 0,
            'total_trips': 0
        }
    
    total_records = len(df)
    
    # Use your actual column names
    total_msw_received = df['Quantity to be remediated in MT'].sum() if 'Quantity to be remediated in MT' in df.columns else 0
    total_output = df['Cumulative Quantity remediated till date in MT'].sum() if 'Cumulative Quantity remediated till date in MT' in df.columns else 0
    total_trips = len(df)  # Count of records as requested
    
    return {
        'total_records': total_records,
        'total_msw_received': round(total_msw_received, 2),
        'total_output': round(total_output, 2),
        'total_trips': total_trips
    }

if __name__ == "__main__":
    print("🎉 Hello from Legacy Report!")
    print("✅ Enhanced with column management and PDF export")
    
    # Test data loading
    df = load_data()
    print(f"📊 Loaded {len(df)} records")
    print(f"📋 Columns: {list(df.columns)}")