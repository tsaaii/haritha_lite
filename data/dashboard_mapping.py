import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

# Initialize logger
logger = logging.getLogger(__name__)

def load_and_explore_csv_data(csv_path='data/public_mini_processed_dates_fixed.csv'):
    """
    Load CSV data and explore its structure to understand clusters, sites, agencies, etc.
    """
    try:
        # Load the CSV file
        df = pd.read_csv(csv_path)
        logger.info(f"✅ Loaded {len(df)} records from CSV")
        
        # Convert date columns to datetime
        date_columns = ['start_date', 'planned_end_date', 'expected_end_date']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Clean column names
        df.columns = df.columns.str.strip()
        
        print("📊 CSV DATA EXPLORATION:")
        print("=" * 50)
        print(f"Total Records: {len(df)}")
        print(f"Total Columns: {len(df.columns)}")
        print("\nColumn Names:")
        for i, col in enumerate(df.columns, 1):
            print(f"  {i:2d}. {col}")
        
        # Explore key entities
        explore_agencies(df)
        explore_clusters(df)
        explore_sites(df)
        explore_machines(df)
        explore_site_status(df)
        
        return df
        
    except Exception as e:
        logger.error(f"❌ Error loading CSV: {e}")
        return pd.DataFrame()

def explore_agencies(df):
    """Find and analyze all agencies in the data"""
    print("\n🏢 AGENCIES ANALYSIS:")
    print("-" * 30)
    
    if 'Agency' in df.columns:
        agencies = df['Agency'].dropna().unique()
        print(f"Total Agencies: {len(agencies)}")
        
        for agency in agencies:
            agency_data = df[df['Agency'] == agency]
            clusters_count = agency_data['Cluster'].nunique() if 'Cluster' in df.columns else 0
            sites_count = agency_data['Site'].nunique() if 'Site' in df.columns else 0
            print(f"  • {agency}: {clusters_count} clusters, {sites_count} sites")
    else:
        print("❌ No 'Agency' column found")

def explore_clusters(df):
    """Find and analyze all clusters in the data"""
    print("\n🗺️ CLUSTERS ANALYSIS:")
    print("-" * 30)
    
    if 'Cluster' in df.columns:
        clusters = df['Cluster'].dropna().unique()
        print(f"Total Clusters: {len(clusters)}")
        
        # Group by cluster to get detailed info
        cluster_summary = df.groupby('Cluster').agg({
            'Site': 'nunique',
            'Agency': 'nunique',
            'Quantity to be remediated in MT': 'sum',
            'Cumulative Quantity remediated till date in MT': 'sum'
        }).reset_index()
        
        # Calculate completion rate for each cluster
        cluster_summary['completion_rate'] = (
            cluster_summary['Cumulative Quantity remediated till date in MT'] / 
            cluster_summary['Quantity to be remediated in MT'] * 100
        ).fillna(0).round(1)
        
        print("\nCluster Details:")
        for _, row in cluster_summary.iterrows():
            print(f"  • {row['Cluster']}: {row['Site']} sites, {row['completion_rate']}% complete")
    else:
        print("❌ No 'Cluster' column found")

def explore_sites(df):
    """Find and analyze all sites in the data"""
    print("\n🏗️ SITES ANALYSIS:")
    print("-" * 30)
    
    if 'Site' in df.columns:
        sites = df['Site'].dropna().unique()
        print(f"Total Sites: {len(sites)}")
        
        # Analyze active vs inactive sites
        if 'Active_site' in df.columns:
            active_sites = len(df[df['Active_site'].str.lower() == 'yes'])
            inactive_sites = len(df[df['Active_site'].str.lower() == 'no'])
            print(f"Active Sites: {active_sites}")
            print(f"Inactive Sites: {inactive_sites}")
        
        # Show sample of sites with their details
        print("\nSample Sites:")
        for site in sites[:5]:  # Show first 5 sites
            site_data = df[df['Site'] == site].iloc[0]
            cluster = site_data.get('Cluster', 'Unknown')
            agency = site_data.get('Agency', 'Unknown')
            active = site_data.get('Active_site', 'Unknown')
            print(f"  • {site} ({cluster}) - Agency: {agency}, Active: {active}")
    else:
        print("❌ No 'Site' column found")

def explore_machines(df):
    """Find and analyze machine types in the data"""
    print("\n🚛 MACHINES ANALYSIS:")
    print("-" * 30)
    
    if 'Machine' in df.columns:
        machines = df['Machine'].dropna().unique()
        print(f"Total Machine Types: {len(machines)}")
        
        # Count machines by type
        machine_counts = df['Machine'].value_counts()
        print("\nMachine Distribution:")
        for machine, count in machine_counts.items():
            print(f"  • {machine}: {count} deployments")
    else:
        print("❌ No 'Machine' column found")

def explore_site_status(df):
    """Analyze site status and completion rates"""
    print("\n📈 SITE STATUS & COMPLETION ANALYSIS:")
    print("-" * 40)
    
    required_cols = ['Quantity to be remediated in MT', 'Cumulative Quantity remediated till date in MT']
    if all(col in df.columns for col in required_cols):
        # Calculate overall completion rate
        total_planned = df['Quantity to be remediated in MT'].sum()
        total_completed = df['Cumulative Quantity remediated till date in MT'].sum()
        overall_completion = (total_completed / total_planned * 100) if total_planned > 0 else 0
        
        print(f"Overall Completion Rate: {overall_completion:.1f}%")
        print(f"Total Planned Quantity: {total_planned:,.0f} MT")
        print(f"Total Completed Quantity: {total_completed:,.0f} MT")
        print(f"Remaining Quantity: {total_planned - total_completed:,.0f} MT")
    else:
        print("❌ Quantity columns not found")

def find_clusters_by_agency(df, agency_name):
    """Find all clusters for a specific agency"""
    print(f"\n🎯 CLUSTERS FOR AGENCY: {agency_name}")
    print("-" * 40)
    
    if 'Agency' not in df.columns:
        print("❌ No 'Agency' column found")
        return []
    
    agency_data = df[df['Agency'] == agency_name]
    if agency_data.empty:
        print(f"❌ No data found for agency: {agency_name}")
        return []
    
    clusters = agency_data['Cluster'].dropna().unique().tolist()
    print(f"Found {len(clusters)} clusters:")
    
    for cluster in clusters:
        cluster_data = agency_data[agency_data['Cluster'] == cluster]
        sites_count = cluster_data['Site'].nunique() if 'Site' in agency_data.columns else 0
        print(f"  • {cluster}: {sites_count} sites")
    
    return clusters

def find_sites_by_cluster(df, cluster_name):
    """Find all sites in a specific cluster"""
    print(f"\n🏗️ SITES IN CLUSTER: {cluster_name}")
    print("-" * 40)
    
    if 'Cluster' not in df.columns:
        print("❌ No 'Cluster' column found")
        return []
    
    cluster_data = df[df['Cluster'] == cluster_name]
    if cluster_data.empty:
        print(f"❌ No data found for cluster: {cluster_name}")
        return []
    
    sites = cluster_data['Site'].dropna().unique().tolist()
    print(f"Found {len(sites)} sites:")
    
    for site in sites:
        site_data = cluster_data[cluster_data['Site'] == site].iloc[0]
        agency = site_data.get('Agency', 'Unknown')
        active = site_data.get('Active_site', 'Unknown')
        
        # Calculate completion rate if data is available
        if all(col in site_data.index for col in ['Quantity to be remediated in MT', 'Cumulative Quantity remediated till date in MT']):
            planned = site_data['Quantity to be remediated in MT']
            completed = site_data['Cumulative Quantity remediated till date in MT']
            completion_rate = (completed / planned * 100) if planned > 0 else 0
            print(f"  • {site} - Agency: {agency}, Active: {active}, Completion: {completion_rate:.1f}%")
        else:
            print(f"  • {site} - Agency: {agency}, Active: {active}")
    
    return sites

def calculate_lagging_sites_analysis(df):
    """Find sites that cannot complete before September 30, 2025"""
    print("\n🚨 LAGGING SITES ANALYSIS:")
    print("-" * 40)
    
    if df.empty or 'Site' not in df.columns:
        print("❌ No site data available")
        return []
    
    if 'days_required' not in df.columns:
        print("❌ No 'days_required' column found")
        return []
    
    # Calculate days until September 30, 2025
    today = datetime.now().date()
    sept_30 = datetime(2025, 9, 30).date()
    days_until_sept30 = (sept_30 - today).days
    
    print(f"Days until Sept 30, 2025: {days_until_sept30}")
    
    lagging_sites = []
    
    for site_name in df['Site'].unique():
        site_data = df[df['Site'] == site_name].iloc[0]
        days_required = site_data.get('days_required', None)
        
        if pd.notna(days_required) and days_required > 0:
            try:
                days_required = float(days_required)
                if days_required > days_until_sept30:
                    days_overdue = days_required - days_until_sept30
                    cluster = site_data.get('Cluster', 'Unknown')
                    agency = site_data.get('Agency', 'Unknown')
                    
                    lagging_sites.append({
                        'site': site_name,
                        'cluster': cluster,
                        'agency': agency,
                        'days_required': days_required,
                        'days_overdue': days_overdue
                    })
            except (ValueError, TypeError):
                continue
    
    # Sort by most overdue first
    lagging_sites.sort(key=lambda x: x['days_overdue'], reverse=True)
    
    print(f"\nFound {len(lagging_sites)} lagging sites:")
    for site in lagging_sites[:10]:  # Show top 10 most critical
        print(f"  • {site['site']} ({site['cluster']}) - {site['agency']}: {site['days_overdue']:.1f} days overdue")
    
    return lagging_sites

def get_performance_rankings(df):
    """Calculate performance rankings for sites"""
    print("\n🏆 SITE PERFORMANCE RANKINGS:")
    print("-" * 40)
    
    if df.empty or 'Site' not in df.columns:
        print("❌ No site data available")
        return []
    
    required_cols = ['Quantity to be remediated in MT', 'Cumulative Quantity remediated till date in MT']
    if not all(col in df.columns for col in required_cols):
        print("❌ Missing required quantity columns")
        return []
    
    performance_sites = []
    
    for site_name in df['Site'].unique():
        site_data = df[df['Site'] == site_name].iloc[0]
        
        total_to_remediate = site_data.get('Quantity to be remediated in MT', 0)
        total_remediated = site_data.get('Cumulative Quantity remediated till date in MT', 0)
        
        if total_to_remediate > 0:
            completion_rate = (total_remediated / total_to_remediate) * 100
            cluster = site_data.get('Cluster', 'Unknown')
            agency = site_data.get('Agency', 'Unknown')
            
            performance_sites.append({
                'site': site_name,
                'cluster': cluster,
                'agency': agency,
                'completion_rate': round(completion_rate, 1),
                'total_to_remediate': total_to_remediate,
                'total_remediated': total_remediated
            })
    
    # Sort by completion rate (highest first)
    performance_sites.sort(key=lambda x: x['completion_rate'], reverse=True)
    
    print(f"\nTop 10 Performing Sites:")
    for i, site in enumerate(performance_sites[:10], 1):
        print(f"  {i:2d}. {site['site']} ({site['cluster']}) - {site['agency']}: {site['completion_rate']}%")
    
    return performance_sites

def main_analysis():
    """Main function to run complete CSV analysis"""
    print("🔍 STARTING CSV DATA ANALYSIS")
    print("=" * 60)
    
    # Load and explore the data
    df = load_and_explore_csv_data()
    
    if df.empty:
        print("❌ No data loaded. Exiting.")
        return
    
    # Example: Find clusters for a specific agency
    if 'Agency' in df.columns:
        first_agency = df['Agency'].dropna().iloc[0]
        find_clusters_by_agency(df, first_agency)
    
    # Example: Find sites in a specific cluster
    if 'Cluster' in df.columns:
        first_cluster = df['Cluster'].dropna().iloc[0]
        find_sites_by_cluster(df, first_cluster)
    
    # Analyze lagging sites
    calculate_lagging_sites_analysis(df)
    
    # Get performance rankings
    get_performance_rankings(df)
    
    print("\n✅ Analysis Complete!")

if __name__ == "__main__":
    main_analysis()