# pdf_generators/legacy_project_summary.py - UPDATED WITH CLEAN DESIGN
"""
Legacy Project Status PDF Generator - EXACT WORKING PATTERN
Updated with clean and minimal design
"""

import io
import requests
from datetime import datetime
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from flask import Blueprint, make_response, jsonify
import traceback

# Create blueprint for Legacy PDF routes
legacy_pdf_bp = Blueprint('legacy_pdf_generator', __name__)

# API URL - same as your working realtime version
API_BASE_URL = "https://weighbridge-site-api-new-287877277037.asia-southeast1.run.app"

def fetch_legacy_project_data():
    """Fetch legacy project data from API - same pattern as working version"""
    try:
        print(f"Fetching legacy project data from: {API_BASE_URL}/project_summary")
        response = requests.get(f"{API_BASE_URL}/project_summary", timeout=20)
        if response.status_code == 200:
            data = response.json()
            print(f"Successfully fetched legacy data for {data.get('project_statistics', {}).get('total_sites', 0)} sites")
            return data
        else:
            print(f"API returned status {response.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching legacy project data: {e}")
        return None

def format_number(num):
    """Format numbers for display"""
    if num >= 1000000:
        return f"{num/1000000:.2f}M"
    elif num >= 1000:
        return f"{num/1000:.1f}K"
    else:
        return f"{num:,.0f}"

def create_legacy_fallback_pdf():
    """Create a simple fallback PDF when main generation fails - same pattern as working version"""
    print("Creating legacy fallback PDF...")
    
    try:
        buffer = io.BytesIO()
        # Updated with standard margins
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=landscape(A4),
            rightMargin=40,
            leftMargin=40,
            topMargin=60,
            bottomMargin=40
        )
        styles = getSampleStyleSheet()
        
        # Clean title style
        title_style = ParagraphStyle(
            'CleanTitle',
            parent=styles['Heading1'],
            fontSize=28,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#2D3748'),
            fontName='Helvetica-Bold'
        )
        
        content = [
            Paragraph("Legacy Project Status Report", title_style),
            Spacer(1, 20),
            Paragraph("Report Generation Notice", styles['Heading2']),
            Spacer(1, 10),
            Paragraph("This is a fallback report generated when the main API data could not be retrieved.", styles['Normal']),
            Spacer(1, 10),
            Paragraph("System Information:", styles['Heading3']),
            Paragraph(f"• Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']),
            Paragraph(f"• API Endpoint: {API_BASE_URL}/project_summary", styles['Normal']),
            Paragraph("• Status: Unable to fetch live data", styles['Normal']),
            Spacer(1, 20),
            Paragraph("Next Steps:", styles['Heading3']),
            Paragraph("1. Check API connectivity", styles['Normal']),
            Paragraph("2. Verify network connection", styles['Normal']),
            Paragraph("3. Try refreshing the report in a few minutes", styles['Normal']),
        ]
        
        doc.build(content)
        pdf_data = buffer.getvalue()
        buffer.close()
        
        print(f"Fallback PDF created: {len(pdf_data):,} bytes")
        return pdf_data
        
    except Exception as e:
        print(f"Even fallback PDF failed: {e}")
        return None

def create_legacy_project_pdf():
    """Create the Legacy Project Status PDF report - EXACT WORKING PATTERN"""
    print("Starting Legacy Project PDF creation...")
    
    try:
        buffer = io.BytesIO()
        
        # Create document with landscape orientation - UPDATED WITH STANDARD MARGINS
        doc = SimpleDocTemplate(
            buffer,
            pagesize=landscape(A4),
            rightMargin=40,
            leftMargin=40,
            topMargin=60,
            bottomMargin=40
        )
        
        # Fetch data - same pattern as working version
        project_data = fetch_legacy_project_data()
        
        if not project_data:
            print("No project data available, creating fallback PDF")
            return create_legacy_fallback_pdf()
        
        # Custom styles - UPDATED WITH CLEAN COLORS
        styles = getSampleStyleSheet()
        
        # Enhanced title style with clean colors - CENTERED
        title_style = ParagraphStyle(
            'EnhancedTitle',
            parent=styles['Heading1'],
            fontSize=28,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#2D3748'),  # Clean dark gray
            fontName='Helvetica-Bold'
        )
        
        # Subtitle style - CENTERED
        subtitle_style = ParagraphStyle(
            'SubTitle',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=25,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#4A5568'),  # Medium gray
            fontName='Helvetica'
        )
        
        # Section header style - CENTERED
        section_style = ParagraphStyle(
            'SectionHeader',
            parent=styles['Heading2'],
            fontSize=18,
            spaceAfter=15,
            spaceBefore=20,
            alignment=TA_CENTER,  # CENTERED HEADINGS
            textColor=colors.HexColor('#3182CE'),  # Professional blue
            fontName='Helvetica-Bold'
        )
        
        content = []
        
        # Header with title - SAME PATTERN AS WORKING VERSION BUT CENTERED
        content.append(Paragraph("LEGACY PROJECT STATUS REPORT", title_style))
        content.append(Paragraph("Swachh Andhra Pradesh Initiative", subtitle_style))
        content.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %H:%M')}", styles['Normal']))
        content.append(Spacer(1, 30))
        
        # Extract key statistics - EXACT SAME PATTERN
        stats = project_data.get('project_statistics', {})
        
        # Project Status Banner - UPDATED WITH CLEAN COLORS AND STANDARD COLUMN WIDTHS
        completion_pct = stats.get('overall_completion_percentage', 0)
        days_remaining = project_data.get('days_remaining', 0)
        
        # STANDARD COLUMN WIDTHS - Equal distribution
        col_widths = [3.4*inch, 3.4*inch, 3.4*inch]
        
        status_data = [
            ['PROJECT STATUS', 'COMPLETION', 'TIME REMAINING'],
            [
                f"{stats.get('total_sites', 0)} Total Sites",
                f"{completion_pct:.1f}% Completed",
                f"{days_remaining} Days to Target"
            ]
        ]
        
        status_table = Table(status_data, colWidths=col_widths)
        status_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2D3748')),  # Clean dark header
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#F7FAFC')),  # Light gray background
            ('TEXTCOLOR', (0, 1), (-1, 1), colors.HexColor('#1A202C')),  # Dark text
            ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 2, colors.HexColor('#2D3748')),
            ('TOPPADDING', (0, 0), (-1, -1), 15),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
        ]))
        
        content.append(status_table)
        content.append(Spacer(1, 25))
        
        # Key Metrics Dashboard - UPDATED WITH CLEAN COLORS
        content.append(Paragraph("PROJECT STATISTICS OVERVIEW", section_style))
        
        metrics_data = [
            ['METRIC', 'VALUE', 'STATUS'],
            ['Total Sites', f"{stats.get('total_sites', 0):,}", 'Monitored'],
            ['Active Sites', f"{stats.get('active_sites', 0):,}", 'Running'],
            ['Valid Sites', f"{stats.get('valid_sites', 0):,}", 'Approved'],
            ['Total Remediated', f"{stats.get('total_quantity_remediated', 0):,.0f} MT", 'Processed'],
            ['Today\'s Progress', f"{stats.get('total_remediated_today', 0):,.0f} MT", 'Daily Output'],
            ['Daily Capacity', f"{stats.get('total_daily_capacity', 0):,.0f} MT", 'Maximum Capacity'],
        ]
        
        metrics_table = Table(metrics_data, colWidths=col_widths)
        metrics_table.setStyle(TableStyle([
            # Header styling - UPDATED WITH CLEAN COLORS
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3182CE')),  # Professional blue
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            
            # Data rows styling - UPDATED WITH CLEAN COLORS
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#1A202C')),
            
            # Alternating row colors - CLEAN BACKGROUNDS
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#F7FAFC'), colors.white]),
            
            # Grid and padding - CLEAN BORDERS
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#4A5568')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        content.append(metrics_table)
        content.append(Spacer(1, 25))
        
        # Agency Performance Breakdown - UPDATED WITH CLEAN COLORS AND PROPER WIDTHS
        content.append(Paragraph("AGENCY CLUSTER SUMMARY", section_style))
        
        agency_summary = project_data.get('agency_cluster_summary', [])
        
        if agency_summary:
            # Create agency table - UPDATED WITH PROPER COLUMN WIDTHS
            agency_data = [['AGENCY', 'CLUSTER', 'SITES', 'TOTAL (MT)', 'REMEDIATED (MT)', 'COMPLETION %']]
            
            for item in agency_summary:
                agency_data.append([
                    item.get('agency', 'Unknown'),
                    item.get('cluster', 'N/A'),
                    f"{item.get('site_count', 0)}",
                    f"{item.get('total_quantity_mt', 0):,.0f}",
                    f"{item.get('remediated_quantity_mt', 0):,.0f}",
                    f"{item.get('completion_percentage', 0):.1f}%"
                ])
            
            # PROPER COLUMN ALIGNMENT - Total width: 10.2 inches
            agency_col_widths = [2*inch, 2*inch, 1.3*inch, 1.3*inch, 1.3*inch, 1.3*inch]
            
            agency_table = Table(agency_data, colWidths=agency_col_widths)
            agency_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#38A169')),  # Clean success green
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('ALIGN', (0, 1), (1, -1), 'LEFT'),
                ('ALIGN', (2, 1), (-1, -1), 'CENTER'),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#1A202C')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F7FAFC')]),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#4A5568')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            
            content.append(agency_table)
        else:
            content.append(Paragraph("No agency data available", styles['Normal']))
        
        content.append(Spacer(1, 25))
        
        # Site Details Section - UPDATED WITH CLEAN COLORS
        content.append(Paragraph("SITE DETAILS SUMMARY", section_style))
        
        site_data = project_data.get('site_details', [])
        
        if site_data:
            site_count = len(site_data)
            active_count = len([s for s in site_data if s.get('active_site') == 'Yes'])
            completed_count = len([s for s in site_data if s.get('completion_percentage', 0) >= 100])
            
            site_summary_data = [
                ['METRIC', 'VALUE'],
                ['Total Sites', f"{site_count:,}"],
                ['Active Sites', f"{active_count:,}"],
                ['Completed Sites', f"{completed_count:,}"],
                ['Completion Rate', f"{(completed_count/site_count)*100:.1f}%"]
            ]
            
            site_summary_table = Table(site_summary_data, colWidths=[3*inch, 2*inch])
            site_summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2D3748')),  # Clean dark header
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('ALIGN', (0, 1), (0, -1), 'LEFT'),
                ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#1A202C')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F7FAFC')]),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#4A5568')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            
            content.append(site_summary_table)
        else:
            content.append(Paragraph("No site details available", styles['Normal']))
        
        content.append(Spacer(1, 25))
        
        # Key Insights - UPDATED WITH CLEAN COLORS
        content.append(Paragraph("KEY INSIGHTS & ALERTS", section_style))
        
        insights = project_data.get('key_insights', {})
        
        insights_list = [
            f"Status: {insights.get('project_status', 'Status data not available')}",
            f"Progress: {insights.get('daily_progress', 'Progress data not available')}",
            f"Critical: {insights.get('critical_sites', 'Critical sites data not available')}",
            f"Material: {insights.get('material_handling', 'Material handling data not available')}"
        ]
        
        for insight in insights_list:
            content.append(Paragraph(f"• {insight}", styles['Normal']))
            content.append(Spacer(1, 8))
        
        content.append(Spacer(1, 20))
        
        # Footer - UPDATED WITH STANDARD COLUMN WIDTHS
        footer_data = [
            ['Real-time Data', f'Target: {project_data.get("target_date", "N/A")}', f'Report: {project_data.get("report_date", "N/A")}'],
            ['API Status: Connected', f'Sites: {len(project_data.get("site_details", []))}', 'Source: Live Monitoring']
        ]
        
        footer_table = Table(footer_data, colWidths=col_widths)
        footer_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#4A5568')),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
        ]))
        
        content.append(footer_table)
        
        # Build the PDF - SAME PATTERN AS WORKING VERSION
        print("Building PDF document...")
        doc.build(content)
        
        pdf_data = buffer.getvalue()
        buffer.close()
        
        print(f"PDF created successfully: {len(pdf_data):,} bytes")
        return pdf_data
        
    except Exception as e:
        print(f"Error in create_legacy_project_pdf: {e}")
        print(traceback.format_exc())
        return create_legacy_fallback_pdf()

@legacy_pdf_bp.route('/api/legacy-project/download')
def download_legacy_project_pdf():
    """Generate and download Legacy Project Status PDF - EXACT SAME PATTERN AS WORKING VERSION"""
    try:
        print("Starting Legacy Project PDF generation process...")
        start_time = datetime.now()
        
        # Generate PDF - same pattern as working version
        pdf_data = create_legacy_project_pdf()
        
        # Check if PDF generation succeeded - EXACT SAME PATTERN AS WORKING VERSION
        if pdf_data is None:
            print("PDF generation returned None")
            return jsonify({
                'error': 'PDF generation failed',
                'message': 'Could not create PDF document'
            }), 500
        
        if len(pdf_data) == 0:
            print("PDF generation returned empty data")
            return jsonify({
                'error': 'PDF generation failed', 
                'message': 'PDF document is empty'
            }), 500
        
        end_time = datetime.now()
        generation_time = (end_time - start_time).total_seconds()
        
        # Create filename with current date in DD-MM-YYYY format
        current_date = datetime.now().strftime('%d-%m-%Y')
        filename = f"Legacy_project_status_{current_date}.pdf"
        
        print(f"PDF generated successfully: {filename} ({len(pdf_data):,} bytes in {generation_time:.2f}s)")
        
        # Create response with proper headers - EXACT SAME PATTERN AS WORKING VERSION
        response = make_response(pdf_data)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
        response.headers['Content-Length'] = str(len(pdf_data))  # Convert to string to avoid issues
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        
        return response
        
    except Exception as e:
        print(f"Error in download_legacy_project_pdf: {e}")
        print(traceback.format_exc())
        return jsonify({
            'error': 'PDF generation failed',
            'details': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@legacy_pdf_bp.route('/api/legacy-project/preview')
def preview_legacy_data():
    """Preview the legacy project data structure"""
    try:
        project_data = fetch_legacy_project_data()
        
        if not project_data:
            return jsonify({
                'error': 'Could not fetch project data',
                'api_url': f"{API_BASE_URL}/project_summary",
                'timestamp': datetime.now().isoformat()
            }), 500
        
        return jsonify({
            'timestamp': datetime.now().isoformat(),
            'api_status': 'Connected',
            'api_url': f"{API_BASE_URL}/project_summary",
            'report_date': project_data.get('report_date'),
            'target_date': project_data.get('target_date'),
            'days_remaining': project_data.get('days_remaining'),
            'project_statistics': project_data.get('project_statistics'),
            'agency_count': len(project_data.get('agency_cluster_summary', [])),
            'site_count': len(project_data.get('site_details', [])),
            'key_insights': project_data.get('key_insights'),
            'filename_format': f"Legacy_project_status_{datetime.now().strftime('%d-%m-%Y')}.pdf"
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'api_url': f"{API_BASE_URL}/project_summary",
            'timestamp': datetime.now().isoformat()
        }), 500

def register_pdf_routes(app):
    """Register Legacy Project PDF routes - same pattern as working version"""
    app.register_blueprint(legacy_pdf_bp)
    print("Legacy Project PDF routes registered:")
    print("   - PDF Download: /api/legacy-project/download") 
    print("   - Data Preview: /api/legacy-project/preview")
    print("   - Using exact working pattern from realtime_summary.py")