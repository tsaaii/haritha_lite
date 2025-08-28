import os
import pandas as pd
import datetime
from pathlib import Path
import glob

# Try matplotlib for PDF generation (most compatible)
try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    from matplotlib.backends.backend_pdf import PdfPages
    PDF_LIB = 'matplotlib'
except ImportError:
    PDF_LIB = None

print(f"PDF Library available: {PDF_LIB}")


class LegacyWasteReportGenerator:
    """Legacy Waste Remediation Report Generator with professional styling"""
    
    def __init__(self, csv_folder_path, output_folder=None):
        """Initialize the report generator
        
        Args:
            csv_folder_path: Path to folder containing CSV files
            output_folder: Path to save reports (default: reports subfolder)
        """
        self.csv_folder_path = Path(csv_folder_path)
        self.output_folder = Path(output_folder or self.csv_folder_path / "reports")
        self.output_folder.mkdir(exist_ok=True)
        
        # Data storage
        self.all_data = pd.DataFrame()
        self.valid_records = pd.DataFrame()
        self.rejected_records = pd.DataFrame()
        self.report_date = None
    
    def find_and_validate_csvs(self):
        """Find all CSV files and validate they have same headers"""
        csv_files = list(self.csv_folder_path.glob("*.csv"))
        
        if not csv_files:
            raise ValueError(f"No CSV files found in {self.csv_folder_path}")
        
        print(f"Found {len(csv_files)} CSV files")
        
        # Check headers consistency
        headers = None
        valid_files = []
        
        for csv_file in csv_files:
            try:
                df = pd.read_csv(csv_file, nrows=0)  # Read only headers
                if headers is None:
                    headers = list(df.columns)
                    valid_files.append(csv_file)
                elif list(df.columns) == headers:
                    valid_files.append(csv_file)
                else:
                    print(f"Warning: {csv_file.name} has different headers, skipping")
            except Exception as e:
                print(f"Error reading {csv_file.name}: {e}")
        
        if not valid_files:
            raise ValueError("No valid CSV files with consistent headers found")
        
        # Check required columns
        required_columns = ['first_weight', 'second_weight', 'net_weight', 'site_name', 'material_type']
        missing_columns = [col for col in required_columns if col not in headers]
        
        if missing_columns:
            print(f"Warning: Missing required columns: {missing_columns}")
            print(f"Available columns: {headers}")
        
        return valid_files
    
    def load_and_combine_data(self):
        """Load and combine all CSV files, then save the combined dataset"""
        csv_files = self.find_and_validate_csvs()
        
        dfs = []
        for csv_file in csv_files:
            try:
                df = pd.read_csv(csv_file)
                df['source_file'] = csv_file.name
                dfs.append(df)
                print(f"Loaded {len(df)} records from {csv_file.name}")
            except Exception as e:
                print(f"Error loading {csv_file.name}: {e}")
        
        if not dfs:
            raise ValueError("No data could be loaded from CSV files")
        
        self.all_data = pd.concat(dfs, ignore_index=True)
        print(f"Total records loaded: {len(self.all_data)}")
        
        # Extract report date from filenames or use current date
        self.extract_report_date(csv_files)
        
        # Save combined dataset as CSV
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        combined_filename = f"Combined_Legacy_Waste_Data_{self.report_date.replace('-', '')}_{timestamp}.csv"
        combined_path = self.output_folder / combined_filename
        
        try:
            self.all_data.to_csv(combined_path, index=False)
            print(f"✅ Combined dataset saved to: {combined_path}")
            print(f"📊 Combined dataset contains {len(self.all_data)} total records from {len(csv_files)} files")
            
            # Store the path for reference in final report summary
            self.combined_data_path = combined_path
            
        except Exception as e:
            print(f"⚠️  Warning: Could not save combined dataset: {e}")
            self.combined_data_path = None
        
        return self.all_data
    
    def extract_report_date(self, csv_files):
        """Extract date from CSV filenames or use current date"""
        # Try to extract date from first filename
        try:
            filename = csv_files[0].stem
            # Look for date patterns in filename
            import re
            date_patterns = [
                r'(\d{4}-\d{2}-\d{2})',  # YYYY-MM-DD
                r'(\d{2}-\d{2}-\d{4})',  # DD-MM-YYYY
                r'(\d{8})',              # YYYYMMDD
            ]
            
            for pattern in date_patterns:
                match = re.search(pattern, filename)
                if match:
                    date_str = match.group(1)
                    try:
                        if len(date_str) == 8:  # YYYYMMDD
                            self.report_date = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
                        elif '-' in date_str:
                            if date_str.split('-')[0].isdigit() and len(date_str.split('-')[0]) == 4:
                                self.report_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").strftime("%d-%m-%Y")
                            else:
                                self.report_date = datetime.datetime.strptime(date_str, "%d-%m-%Y").strftime("%d-%m-%Y")
                        return
                    except:
                        continue
        except:
            pass
        
        # Use current date if no date found in filename
        self.report_date = datetime.datetime.now().strftime("%d-%m-%Y")
    
    def clean_and_filter_data(self):
        """Clean and filter data according to business rules"""
        df = self.all_data.copy()
        
        # Convert weight columns to numeric, handling any non-numeric values
        weight_columns = ['first_weight', 'second_weight', 'net_weight']
        for col in weight_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Initialize rejected records list
        rejected_records = []
        
        # Rule 1: Reject records where first_weight and second_weight are same
        mask1 = (df['first_weight'] == df['second_weight']) & df['first_weight'].notna()
        rejected_records.append(df[mask1].copy().assign(rejection_reason='First and Second weight are same'))
        
        # Rule 2: Reject records where first_weight or second_weight is 0
        mask2 = ((df['first_weight'] == 0) | (df['second_weight'] == 0)) & ~mask1
        rejected_records.append(df[mask2].copy().assign(rejection_reason='Weight is zero'))
        
        # Rule 3: Reject records where net_weight is less than 1000 kg
        mask3 = (df['net_weight'] < 1000) & ~mask1 & ~mask2
        rejected_records.append(df[mask3].copy().assign(rejection_reason='Net weight less than 1000 kg'))
        
        # Combine all rejection masks
        rejected_mask = mask1 | mask2 | mask3
        
        # Store rejected records
        if any(len(r) > 0 for r in rejected_records):
            self.rejected_records = pd.concat([r for r in rejected_records if len(r) > 0], ignore_index=True)
        else:
            self.rejected_records = pd.DataFrame()
        
        # Store valid records
        self.valid_records = df[~rejected_mask].copy()
        
        print(f"Valid records: {len(self.valid_records)}")
        print(f"Rejected records: {len(self.rejected_records)}")
        
        return self.valid_records, self.rejected_records
    
    def calculate_summaries(self):
        """Calculate all required summaries"""
        if self.valid_records.empty:
            return {}
        
        # Convert kg to MT (1 metric tonne = 1000 kg)
        df = self.valid_records.copy()
        df['net_weight_mt'] = df['net_weight'] / 1000.0
        
        summaries = {}
        
        # 1. Total waste by site
        summaries['by_site'] = df.groupby('site_name')['net_weight_mt'].sum().sort_values(ascending=False)
        
        # 2. Total waste by cluster (if cluster_name column exists)
        if 'cluster_name' in df.columns:
            summaries['by_cluster'] = df.groupby('cluster_name')['net_weight_mt'].sum().sort_values(ascending=False)
        elif 'cluster' in df.columns:
            summaries['by_cluster'] = df.groupby('cluster')['net_weight_mt'].sum().sort_values(ascending=False)
        else:
            summaries['by_cluster'] = pd.Series(dtype=float)
        
        # 3. Site and material type combinations
        summaries['by_site_material'] = df.groupby(['site_name', 'material_type'])['net_weight_mt'].sum().sort_values(ascending=False)
        
        # 4. Get unique materials for separate tables
        summaries['materials'] = df['material_type'].unique() if 'material_type' in df.columns else []
        
        return summaries
    
    def create_pdf_with_matplotlib(self, summaries, output_path):
        """Create PDF using matplotlib - most compatible option"""
        try:
            # Calculate summary statistics
            total_waste = summaries['by_site'].sum() if not summaries['by_site'].empty else 0
            total_trips = len(self.valid_records) if not self.valid_records.empty else 0
            total_sites = len(summaries['by_site']) if not summaries['by_site'].empty else 0
            total_clusters = len(summaries['by_cluster']) if not summaries['by_cluster'].empty else 0
            
            with PdfPages(str(output_path)) as pdf:
                # Page 1: Header and Executive Summary
                fig, ax = plt.subplots(figsize=(8.27, 11.69))  # A4 size
                ax.axis('off')
                
                # Header section
                header_rect = patches.Rectangle((0.05, 0.85), 0.9, 0.12, linewidth=2, 
                                              edgecolor='black', facecolor='lightgray', alpha=0.3)
                ax.add_patch(header_rect)
                
                ax.text(0.5, 0.94, 'Swachha Andhra Corporation', 
                       ha='center', va='center', fontsize=16, fontweight='bold')
                ax.text(0.5, 0.90, f'Daily Summary Report for Legacy Waste Remediation on {datetime.date.today()} by Advitia Labs', 
                       ha='center', va='center', fontsize=12, fontweight='bold', color='darkblue')
                ax.text(0.5, 0.87, f'Generated on: {datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")}', 
                       ha='center', va='center', fontsize=10)
                
                # Executive Summary
                summary_rect = patches.Rectangle((0.1, 0.65), 0.8, 0.15, linewidth=1, 
                                               edgecolor='darkblue', facecolor='lightblue', alpha=0.3)
                ax.add_patch(summary_rect)
                
                ax.text(0.5, 0.77, 'EXECUTIVE SUMMARY', ha='center', va='center', 
                       fontsize=14, fontweight='bold', color='darkblue')
                
                summary_text = f"""Total Waste Remediated: {total_waste:.3f} MT
Total Successful Trips: {total_trips:,}
Number of Active Sites: {total_sites}
Number of Clusters: {total_clusters}
Rejected Records: {len(self.rejected_records)}"""
                
                ax.text(0.5, 0.70, summary_text, ha='center', va='center', fontsize=11)
                
                # Site Summary Table
                y_pos = 0.55
                ax.text(0.5, y_pos, 'TOTAL WASTE REMEDIATED BY SITE', ha='center', 
                       fontsize=12, fontweight='bold', color='darkblue')
                
                if not summaries['by_site'].empty:
                    y_pos -= 0.05
                    # Table headers
                    ax.text(0.25, y_pos, 'Site Name', ha='center', fontweight='bold', 
                           bbox=dict(boxstyle="round,pad=0.3", facecolor='lightblue'))
                    ax.text(0.75, y_pos, 'Weight (MT)', ha='center', fontweight='bold',
                           bbox=dict(boxstyle="round,pad=0.3", facecolor='lightblue'))
                    
                    # Table data
                    for i, (site, weight) in enumerate(summaries['by_site'].head(10).items()):
                        y_pos -= 0.03
                        bg_color = 'lightgray' if i % 2 == 0 else 'white'
                        ax.text(0.25, y_pos, str(site)[:30], ha='center', fontsize=9,
                               bbox=dict(boxstyle="round,pad=0.2", facecolor=bg_color))
                        ax.text(0.75, y_pos, f'{weight:.3f}', ha='center', fontsize=9,
                               bbox=dict(boxstyle="round,pad=0.2", facecolor=bg_color))
                
                ax.set_xlim(0, 1)
                ax.set_ylim(0, 1)
                pdf.savefig(fig, bbox_inches='tight')
                plt.close()
                
                # Page 2: Cluster Summary and Material Breakdown
                if not summaries['by_cluster'].empty or summaries['materials']:
                    fig, ax = plt.subplots(figsize=(8.27, 11.69))
                    ax.axis('off')
                    
                    y_pos = 0.95
                    
                    # Cluster Summary
                    if not summaries['by_cluster'].empty:
                        ax.text(0.5, y_pos, 'TOTAL WASTE REMEDIATED BY CLUSTER', ha='center', 
                               fontsize=12, fontweight='bold', color='darkblue')
                        y_pos -= 0.05
                        
                        # Table headers
                        ax.text(0.25, y_pos, 'Cluster Name', ha='center', fontweight='bold',
                               bbox=dict(boxstyle="round,pad=0.3", facecolor='lightblue'))
                        ax.text(0.75, y_pos, 'Weight (MT)', ha='center', fontweight='bold',
                               bbox=dict(boxstyle="round,pad=0.3", facecolor='lightblue'))
                        
                        # Table data
                        for i, (cluster, weight) in enumerate(summaries['by_cluster'].head(10).items()):
                            y_pos -= 0.03
                            bg_color = 'lightgray' if i % 2 == 0 else 'white'
                            ax.text(0.25, y_pos, str(cluster)[:30], ha='center', fontsize=9,
                                   bbox=dict(boxstyle="round,pad=0.2", facecolor=bg_color))
                            ax.text(0.75, y_pos, f'{weight:.3f}', ha='center', fontsize=9,
                                   bbox=dict(boxstyle="round,pad=0.2", facecolor=bg_color))
                        
                        y_pos -= 0.08
                    
                    # Material Type Breakdown
                    if summaries['materials']:
                        ax.text(0.5, y_pos, 'WASTE REMEDIATION BY MATERIAL TYPE', ha='center', 
                               fontsize=12, fontweight='bold', color='darkblue')
                        y_pos -= 0.05
                        
                        for material in summaries['materials'][:3]:  # Show first 3 materials
                            material_data = summaries['by_site_material'][summaries['by_site_material'].index.get_level_values(1) == material]
                            site_data = material_data.groupby(level=0).sum()
                            
                            if not site_data.empty:
                                ax.text(0.5, y_pos, f'Material: {str(material)[:40]}', ha='center', 
                                       fontsize=10, fontweight='bold', color='darkgreen')
                                y_pos -= 0.03
                                
                                for i, (site, weight) in enumerate(site_data.head(5).items()):
                                    y_pos -= 0.025
                                    ax.text(0.25, y_pos, str(site)[:25], ha='center', fontsize=8)
                                    ax.text(0.75, y_pos, f'{weight:.3f}', ha='center', fontsize=8)
                                
                                y_pos -= 0.03
                    
                    ax.set_xlim(0, 1)
                    ax.set_ylim(0, 1)
                    pdf.savefig(fig, bbox_inches='tight')
                    plt.close()
                
                # Page 3: Rejected Records
                if not self.rejected_records.empty:
                    fig, ax = plt.subplots(figsize=(8.27, 11.69))
                    ax.axis('off')
                    
                    y_pos = 0.95
                    ax.text(0.5, y_pos, 'REJECTED RECORDS DETAILS', ha='center', 
                           fontsize=12, fontweight='bold', color='darkred')
                    y_pos -= 0.03
                    ax.text(0.5, y_pos, f'Total Rejected Records: {len(self.rejected_records)}', 
                           ha='center', fontsize=10)
                    y_pos -= 0.05
                    
                    # Table headers
                    headers = ['Site', 'Cluster', 'Ticket', '1st Wt', '2nd Wt', 'Reason']
                    x_positions = [0.1, 0.25, 0.4, 0.55, 0.7, 0.85]
                    
                    for i, header in enumerate(headers):
                        ax.text(x_positions[i], y_pos, header, ha='center', fontweight='bold', fontsize=8,
                               bbox=dict(boxstyle="round,pad=0.2", facecolor='lightcoral'))
                    
                    # Table data
                    for idx, (_, row) in enumerate(self.rejected_records.head(20).iterrows()):
                        y_pos -= 0.03
                        cluster_name = row.get('cluster_name', row.get('cluster', 'N/A'))
                        ticket_number = row.get('ticket_number', row.get('ticket_no', 'N/A'))
                        
                        data_row = [
                            str(row.get('site_name', 'N/A'))[:8],
                            str(cluster_name)[:8],
                            str(ticket_number)[:8],
                            f"{row.get('first_weight', 0):.0f}",
                            f"{row.get('second_weight', 0):.0f}",
                            str(row.get('rejection_reason', 'Unknown'))[:12]
                        ]
                        
                        bg_color = 'mistyrose' if idx % 2 == 0 else 'white'
                        for i, data in enumerate(data_row):
                            ax.text(x_positions[i], y_pos, data, ha='center', fontsize=7,
                                   bbox=dict(boxstyle="round,pad=0.1", facecolor=bg_color))
                    
                    ax.set_xlim(0, 1)
                    ax.set_ylim(0, 1)
                    pdf.savefig(fig, bbox_inches='tight')
                    plt.close()
                
                # Final page: Attribution
                fig, ax = plt.subplots(figsize=(8.27, 11.69))
                ax.axis('off')
                ax.text(0.5, 0.5, f'Report generated by Legacy Waste Remediation Monitor\nat {datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")}', 
                       ha='center', va='center', fontsize=10, style='italic')
                ax.set_xlim(0, 1)
                ax.set_ylim(0, 1)
                pdf.savefig(fig, bbox_inches='tight')
                plt.close()
            
            return True
            
        except Exception as e:
            print(f"Error creating PDF with matplotlib: {e}")
            return False
    
    def generate_excel_report(self, summaries):
        """Generate Excel report with professional formatting"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"Legacy_Waste_Remediation_Summary_{self.report_date.replace('-', '')}_{timestamp}.xlsx"
        save_path = self.output_folder / filename
        
        with pd.ExcelWriter(str(save_path), engine='openpyxl') as writer:
            
            # Summary Sheet
            summary_data = []
            summary_data.append(['LEGACY WASTE REMEDIATION DAILY REPORT'])
            summary_data.append([f'Daily Summary Report for Legacy Waste Remediation on {self.report_date}'])
            summary_data.append([f'Generated on: {datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")}'])
            summary_data.append([''])
            
            # Executive Summary
            total_waste = summaries['by_site'].sum() if not summaries['by_site'].empty else 0
            total_trips = len(self.valid_records) if not self.valid_records.empty else 0
            total_sites = len(summaries['by_site']) if not summaries['by_site'].empty else 0
            total_clusters = len(summaries['by_cluster']) if not summaries['by_cluster'].empty else 0
            
            summary_data.append(['EXECUTIVE SUMMARY'])
            summary_data.append(['Total Waste Remediated (MT)', f'{total_waste:.3f}'])
            summary_data.append(['Total Successful Trips', f'{total_trips:,}'])
            summary_data.append(['Number of Active Sites', f'{total_sites}'])
            summary_data.append(['Number of Clusters', f'{total_clusters}'])
            summary_data.append(['Rejected Records', f'{len(self.rejected_records)}'])
            summary_data.append([''])
            
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Executive Summary', index=False, header=False)
            
            # Site Summary
            if not summaries['by_site'].empty:
                site_summary = summaries['by_site'].reset_index()
                site_summary.columns = ['Site Name', 'Weight (MT)']
                site_summary['Weight (MT)'] = site_summary['Weight (MT)'].round(3)
                site_summary.to_excel(writer, sheet_name='Site Summary', index=False)
            
            # Cluster Summary
            if not summaries['by_cluster'].empty:
                cluster_summary = summaries['by_cluster'].reset_index()
                cluster_summary.columns = ['Cluster Name', 'Weight (MT)']
                cluster_summary['Weight (MT)'] = cluster_summary['Weight (MT)'].round(3)
                cluster_summary.to_excel(writer, sheet_name='Cluster Summary', index=False)
            
            # Material Type Breakdown
            if 'material_type' in self.valid_records.columns:
                for i, material in enumerate(summaries['materials']):
                    material_data = summaries['by_site_material'][summaries['by_site_material'].index.get_level_values(1) == material]
                    site_data = material_data.groupby(level=0).sum().reset_index()
                    site_data.columns = ['Site Name', 'Weight (MT)']
                    site_data['Weight (MT)'] = site_data['Weight (MT)'].round(3)
                    
                    # Clean sheet name - remove invalid characters and limit length
                    clean_material = str(material).replace('/', '_').replace('\\', '_').replace('?', '').replace('*', '').replace('[', '').replace(']', '').replace(':', '_')
                    sheet_name = f'{clean_material[:20]} by Site'  # Limit sheet name length
                    site_data.to_excel(writer, sheet_name=sheet_name, index=False)
            
            # Rejected Records
            if not self.rejected_records.empty:
                rejected_export = self.rejected_records.copy()
                
                # Get the right column names
                cluster_col = 'cluster_name' if 'cluster_name' in rejected_export.columns else 'cluster'
                ticket_col = 'ticket_number' if 'ticket_number' in rejected_export.columns else 'ticket_no'
                
                # Ensure columns exist before trying to access them
                columns_to_export = ['site_name']
                if cluster_col in rejected_export.columns:
                    columns_to_export.append(cluster_col)
                else:
                    rejected_export[cluster_col] = 'N/A'
                    columns_to_export.append(cluster_col)
                
                if ticket_col in rejected_export.columns:
                    columns_to_export.append(ticket_col)
                else:
                    rejected_export[ticket_col] = 'N/A'
                    columns_to_export.append(ticket_col)
                
                columns_to_export.extend(['first_weight', 'second_weight', 'rejection_reason'])
                
                rejected_summary = rejected_export[columns_to_export].copy()
                rejected_summary.columns = ['Site Name', 'Cluster Name', 'Ticket Number', 'First Weight (kg)', 'Second Weight (kg)', 'Rejection Reason']
                rejected_summary.to_excel(writer, sheet_name='Rejected Records', index=False)
            else:
                # Create empty rejected records sheet
                empty_rejected = pd.DataFrame({
                    'Site Name': ['No rejected records'],
                    'Cluster Name': [''],
                    'Ticket Number': [''],
                    'First Weight (kg)': [''],
                    'Second Weight (kg)': [''],
                    'Rejection Reason': ['']
                })
                empty_rejected.to_excel(writer, sheet_name='Rejected Records', index=False)
        
        print(f"Excel report generated successfully: {save_path}")
        return save_path
    
    def generate_html_content(self, summaries):
        """Generate HTML content for the report"""
        # Calculate summary statistics
        total_waste = summaries['by_site'].sum() if not summaries['by_site'].empty else 0
        total_trips = len(self.valid_records) if not self.valid_records.empty else 0
        total_sites = len(summaries['by_site']) if not summaries['by_site'].empty else 0
        total_clusters = len(summaries['by_cluster']) if not summaries['by_cluster'].empty else 0
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Legacy Waste Remediation Report</title>
            <style>
                body {{
                    font-family: 'Helvetica', Arial, sans-serif;
                    margin: 20px;
                    color: #333;
                    line-height: 1.4;
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                    border: 2px solid #000;
                    padding: 20px;
                    background-color: #f9f9f9;
                }}
                .header h1 {{
                    font-size: 18px;
                    font-weight: bold;
                    margin: 0 0 8px 0;
                    color: #000;
                }}
                .header h2 {{
                    font-size: 14px;
                    font-weight: bold;
                    margin: 0 0 8px 0;
                    color: #1e3a8a;
                }}
                .header p {{
                    font-size: 11px;
                    margin: 0;
                    color: #666;
                }}
                .executive-summary {{
                    margin: 20px 0;
                    text-align: center;
                    border: 1px solid #000;
                    padding: 15px;
                    background-color: #f0f8ff;
                }}
                .section-header {{
                    font-size: 14px;
                    font-weight: bold;
                    text-align: center;
                    margin: 25px 0 15px 0;
                    color: #1e3a8a;
                    border-bottom: 2px solid #1e3a8a;
                    padding-bottom: 5px;
                }}
                .summary-stats {{
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 10px;
                    margin: 15px 0;
                }}
                .summary-stats div {{
                    text-align: center;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 15px 0;
                    font-size: 10px;
                }}
                th {{
                    background-color: #add8e6;
                    color: #000;
                    font-weight: bold;
                    padding: 8px;
                    text-align: center;
                    border: 1px solid #000;
                }}
                td {{
                    padding: 6px;
                    text-align: center;
                    border: 1px solid #000;
                }}
                tr:nth-child(even) {{
                    background-color: #f0f0f0;
                }}
                tr:nth-child(odd) {{
                    background-color: #ffffff;
                }}
                .material-section {{
                    margin: 20px 0;
                    page-break-inside: avoid;
                }}
                .material-header {{
                    font-size: 12px;
                    font-weight: bold;
                    text-align: center;
                    margin: 15px 0 10px 0;
                    color: #1e3a8a;
                }}
                .rejected-table th {{
                    background-color: #ffcccb;
                }}
                .attribution {{
                    margin-top: 30px;
                    text-align: center;
                    font-size: 9px;
                    color: #666;
                    border-top: 1px solid #ccc;
                    padding-top: 10px;
                }}
                .page-break {{
                    page-break-before: always;
                }}
                @media print {{
                    body {{ margin: 15px; }}
                    .page-break {{ page-break-before: always; }}
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Swachha Andhra Corporation</h1>
                <h2>Daily Summary Report for Legacy Waste Remediation on {datetime.datetime.now().strftime('%d-%m-%Y')} by Advitia Labs</h2>
                <p>Generated on: {datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')}</p>
            </div>
            
            <div class="executive-summary">
                <h3 class="section-header">EXECUTIVE SUMMARY</h3>
                <div class="summary-stats">
                    <div><strong>Total Waste Remediated:</strong> {total_waste:.3f} MT</div>
                    <div><strong>Total Successful Trips:</strong> {total_trips:,}</div>
                    <div><strong>Number of Active Sites:</strong> {total_sites}</div>
                    <div><strong>Number of Clusters:</strong> {total_clusters}</div>
                    <div><strong>Rejected Records:</strong> {len(self.rejected_records)}</div>
                    <div></div>
                </div>
            </div>
        """
        
        # Site Summary Table
        html_content += '<h3 class="section-header">TOTAL WASTE REMEDIATED BY SITE</h3>'
        if not summaries['by_site'].empty:
            html_content += '<table><thead><tr><th>Site Name</th><th>Weight (MT)</th></tr></thead><tbody>'
            for site, weight in summaries['by_site'].items():
                html_content += f'<tr><td>{site}</td><td>{weight:.3f}</td></tr>'
            html_content += '</tbody></table>'
        else:
            html_content += '<p style="text-align: center;">No site data available</p>'
        
        # Cluster Summary Table
        if not summaries['by_cluster'].empty:
            html_content += '<h3 class="section-header">TOTAL WASTE REMEDIATED BY CLUSTER</h3>'
            html_content += '<table><thead><tr><th>Cluster Name</th><th>Weight (MT)</th></tr></thead><tbody>'
            for cluster, weight in summaries['by_cluster'].items():
                html_content += f'<tr><td>{cluster}</td><td>{weight:.3f}</td></tr>'
            html_content += '</tbody></table>'
        
        # Material Type Breakdown
        html_content += '<h3 class="section-header">WASTE REMEDIATION BY SITE AND MATERIAL TYPE</h3>'
        
        if 'material_type' in self.valid_records.columns:
            for material in summaries['materials']:
                material_data = summaries['by_site_material'][summaries['by_site_material'].index.get_level_values(1) == material]
                site_data = material_data.groupby(level=0).sum()
                
                html_content += f'<div class="material-section">'
                html_content += f'<h4 class="material-header">Material Type: {material}</h4>'
                html_content += '<table><thead><tr><th>Site Name</th><th>Weight (MT)</th></tr></thead><tbody>'
                
                for site, weight in site_data.items():
                    html_content += f'<tr><td>{site}</td><td>{weight:.3f}</td></tr>'
                
                html_content += '</tbody></table></div>'
        
        # Cluster-wise Final Summary
        if not summaries['by_cluster'].empty:
            html_content += '<div class="page-break"></div>'
            html_content += '<h3 class="section-header">CLUSTER-WISE TOTAL WASTE REMEDIATED</h3>'
            html_content += '<table><thead><tr><th>Cluster Name</th><th>Total Weight (MT)</th></tr></thead><tbody>'
            for cluster, weight in summaries['by_cluster'].items():
                html_content += f'<tr><td>{cluster}</td><td>{weight:.3f}</td></tr>'
            html_content += '</tbody></table>'
        
        # Rejected Records Table
        html_content += '<h3 class="section-header">REJECTED RECORDS DETAILS</h3>'
        html_content += f'<p style="text-align: center;"><strong>Total Rejected Records: {len(self.rejected_records)}</strong></p>'
        
        if not self.rejected_records.empty:
            html_content += '<table class="rejected-table"><thead><tr>'
            html_content += '<th>Site Name</th><th>Cluster Name</th><th>Ticket Number</th>'
            html_content += '<th>First Weight (kg)</th><th>Second Weight (kg)</th><th>Rejection Reason</th>'
            html_content += '</tr></thead><tbody>'
            
            for _, row in self.rejected_records.iterrows():
                cluster_name = row.get('cluster_name', row.get('cluster', 'N/A'))
                ticket_number = row.get('ticket_number', row.get('ticket_no', 'N/A'))
                
                html_content += f'''<tr>
                    <td>{row.get('site_name', 'N/A')}</td>
                    <td>{cluster_name}</td>
                    <td>{ticket_number}</td>
                    <td>{row.get('first_weight', 0):.1f}</td>
                    <td>{row.get('second_weight', 0):.1f}</td>
                    <td>{row.get('rejection_reason', 'Unknown')}</td>
                </tr>'''
            
            html_content += '</tbody></table>'
        else:
            html_content += '<p style="text-align: center;">No rejected records found</p>'
        
        # Attribution
        html_content += f'''
            <div class="attribution">
                <hr>
                <p>Report generated by Advitia Labs for Swachha Andhra Corporation at {datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')}</p>
            </div>
        </body>
        </html>
        '''
        
        return html_content
    
    def generate_report(self, format_type='auto'):
        """Main method to generate the complete report
        
        Args:
            format_type: 'pdf', 'html', 'excel', or 'auto' (tries PDF first, falls back to HTML and Excel)
        """
        try:
            # Load and process data
            print("Loading CSV files...")
            self.load_and_combine_data()
            
            print("Cleaning and filtering data...")
            self.clean_and_filter_data()
            
            print("Calculating summaries...")
            summaries = self.calculate_summaries()
            
            # Generate report based on format type and availability
            report_paths = []
            
            # Try to generate PDF using matplotlib
            if format_type in ['auto', 'pdf'] and PDF_LIB == 'matplotlib':
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                pdf_filename = f"Legacy_Waste_Remediation_Summary_{self.report_date.replace('-', '')}_{timestamp}.pdf"
                pdf_path = self.output_folder / pdf_filename
                
                print(f"Generating PDF using {PDF_LIB}...")
                
                if self.create_pdf_with_matplotlib(summaries, pdf_path):
                    print(f"PDF report generated successfully: {pdf_path}")
                    report_paths.append(pdf_path)
                else:
                    print("PDF generation failed")
            
            # Generate HTML report
            if format_type in ['auto', 'html']:
                html_content = self.generate_html_content(summaries)
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                html_filename = f"Legacy_Waste_Remediation_Summary_{self.report_date.replace('-', '')}_{timestamp}.html"
                html_path = self.output_folder / html_filename
                
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                print(f"HTML report generated: {html_path}")
                report_paths.append(html_path)
            
            # Generate Excel report
            if format_type in ['auto', 'excel']:
                print("Generating Excel report...")
                excel_path = self.generate_excel_report(summaries)
                report_paths.append(excel_path)
            
            print(f"\n✅ Report generation completed successfully!")
            for path in report_paths:
                print(f"📄 Report saved to: {path}")
            print(f"📊 Valid records processed: {len(self.valid_records)}")
            print(f"❌ Rejected records: {len(self.rejected_records)}")
            
            return report_paths
            
        except Exception as e:
            print(f"❌ Error generating report: {str(e)}")
            raise


def install_pdf_dependencies():
    """Instructions for installing PDF generation dependencies"""
    print("\n📋 To enable PDF generation, matplotlib is recommended:")
    print("   pip install matplotlib")
    print("   (Most Python environments already have matplotlib)")
    print("\n💡 The script will generate HTML and Excel reports without dependencies")
    print("\n🖨️  You can also:")
    print("   - Open the HTML file in your browser and print to PDF")
    print("   - Use online HTML to PDF converters")


def main():
    """Example usage of the report generator"""
    print("Legacy Waste Remediation Report Generator")
    print("=" * 50)
    
    if not PDF_LIB:
        install_pdf_dependencies()
    else:
        print(f"PDF generation available using: {PDF_LIB}")
    
    # Specify the folder containing CSV files
    csv_folder = input("\nEnter path to CSV folder (or press Enter for current directory): ").strip()
    if not csv_folder:
        csv_folder = "."
    
    # Create report generator
    generator = LegacyWasteReportGenerator(csv_folder)
    
    # Generate report
    try:
        report_paths = generator.generate_report()
        print(f"\n🎉 Success! Reports available at:")
        for path in report_paths:
            print(f"   📄 {path}")
        
        # Additional instructions for PDF
        if not PDF_LIB:
            html_files = [p for p in report_paths if str(p).endswith('.html')]
            if html_files:
                print(f"\n💡 To convert HTML to PDF:")
                print(f"   1. Open {html_files[0]} in your browser")
                print(f"   2. Press Ctrl+P (Cmd+P on Mac)")
                print(f"   3. Select 'Save as PDF' as destination")
                print(f"   4. Choose A4 paper size for best results")
        
    except Exception as e:
        print(f"\n❌ Failed to generate report: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()