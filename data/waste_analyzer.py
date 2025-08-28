import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import warnings
import os
warnings.filterwarnings('ignore')

# Set up plotting style
plt.style.use('default')
sns.set_palette("husl")

class WasteManagementAnalyzer:
    def __init__(self, data_file_path, target_date=None):
        """
        Initialize the analyzer with data file path and optional target date
        If no target date provided, uses the most recent date in data
        """
        self.data_file_path = data_file_path
        self.df = None
        self.target_date = target_date
        self.load_data()
        if self.df is not None:
            self.prepare_data()
        
    def load_data(self):
        """Load and basic clean the dataset"""
        try:
            # Try multiple possible file paths
            possible_paths = [
                self.data_file_path,
                f"data/{self.data_file_path}",
                f"./{self.data_file_path}",
                f"../{self.data_file_path}",
                f"data/waste_management_data_updated.csv",
                f"./data/waste_management_data_updated.csv",
                f"../data/waste_management_data_updated.csv"
            ]
            
            for path in possible_paths:
                try:
                    if os.path.exists(path):
                        self.df = pd.read_csv(path)
                        print(f"✅ Data loaded successfully from {path}: {len(self.df)} records")
                        self.data_file_path = path
                        return
                except (FileNotFoundError, pd.errors.EmptyDataError):
                    continue
                    
            # If no file found, provide helpful message
            print(f"❌ Error: Could not find file '{self.data_file_path}'")
            print("💡 Please ensure the file is in one of these locations:")
            for path in possible_paths:
                print(f"   - {path}")
            print("\n🔧 Current working directory:", os.getcwd())
            print("📁 Files in current directory:", os.listdir('.'))
            if os.path.exists('data'):
                print("📁 Files in data directory:", os.listdir('data'))
            
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return
    
    def prepare_data(self):
        """Prepare and clean data for analysis"""
        if self.df is None:
            print("❌ No data available to prepare")
            return
            
        try:
            # Convert date columns
            self.df['Date'] = pd.to_datetime(self.df['Date'])
            self.df['fetch_timestamp'] = pd.to_datetime(self.df['fetch_timestamp'])
            
            # Clean time column and create datetime
            self.df['Time_clean'] = self.df['Time'].astype(str)
            self.df['datetime'] = pd.to_datetime(self.df['Date'].astype(str) + ' ' + self.df['Time_clean'], errors='coerce')
            
            # Extract hour from time for hourly analysis
            self.df['hour'] = self.df['datetime'].dt.hour
            
            # Set target date if not provided
            if self.target_date is None:
                self.target_date = self.df['Date'].max()
            else:
                self.target_date = pd.to_datetime(self.target_date)
                
            print(f"📅 Target analysis date: {self.target_date.strftime('%Y-%m-%d')}")
            
        except Exception as e:
            print(f"❌ Error preparing data: {e}")
            import traceback
            traceback.print_exc()
    
    def output_1_agency_name(self):
        """Output 1: Agency Name(s)"""
        print("\n" + "="*50)
        print("📋 OUTPUT 1: AGENCY NAMES")
        print("="*50)
        
        agencies = self.df['agency'].value_counts()
        
        print("Agencies in dataset:")
        for agency, count in agencies.items():
            print(f"  • {agency}: {count:,} trips ({count/len(self.df)*100:.1f}%)")
        
        # Return primary agency (most trips)
        primary_agency = agencies.index[0]
        print(f"\n🏢 Primary Agency: {primary_agency}")
        
        return {
            'primary_agency': primary_agency,
            'all_agencies': agencies.to_dict(),
            'total_agencies': len(agencies)
        }
    
    def output_2_total_trips_day(self):
        """Output 2: Total trips done on target day"""
        print("\n" + "="*50)
        print(f"📊 OUTPUT 2: TOTAL TRIPS ON {self.target_date.strftime('%Y-%m-%d')}")
        print("="*50)
        
        day_data = self.df[self.df['Date'] == self.target_date]
        total_trips = len(day_data)
        
        if total_trips == 0:
            print(f"⚠️  No trips found for {self.target_date.strftime('%Y-%m-%d')}")
            # Get closest date with data
            available_dates = sorted(self.df['Date'].unique())
            closest_date = min(available_dates, key=lambda x: abs((x - self.target_date).days))
            day_data = self.df[self.df['Date'] == closest_date]
            total_trips = len(day_data)
            print(f"📅 Showing data for closest available date: {closest_date.strftime('%Y-%m-%d')}")
            self.target_date = closest_date
        
        # Additional statistics for the day
        total_weight = day_data['Net Weight'].sum() if 'Net Weight' in day_data.columns else 0
        unique_vehicles = day_data['Vehicle No'].nunique() if 'Vehicle No' in day_data.columns else 0
        unique_sites = day_data['site'].nunique() if 'site' in day_data.columns else 0
        
        print(f"🚛 Total Trips: {total_trips:,}")
        print(f"⚖️  Total Net Weight: {total_weight:,.0f} kg")
        print(f"🚚 Unique Vehicles: {unique_vehicles}")
        print(f"📍 Sites Covered: {unique_sites}")
        
        return {
            'date': self.target_date,
            'total_trips': total_trips,
            'total_weight': total_weight,
            'unique_vehicles': unique_vehicles,
            'unique_sites': unique_sites
        }
    
    def output_3_trips_per_hour(self):
        """Output 3: DataFrame with trips per hour for target day"""
        print("\n" + "="*50)
        print(f"⏰ OUTPUT 3: TRIPS PER HOUR ON {self.target_date.strftime('%Y-%m-%d')}")
        print("="*50)
        
        day_data = self.df[self.df['Date'] == self.target_date].copy()
        
        if len(day_data) == 0:
            print("No data available for the target date")
            return pd.DataFrame()
        
        # Create hourly summary
        hourly_stats = day_data.groupby('hour').agg({
            'Ticket No': 'count',
            'Net Weight': ['sum', 'mean'],
            'Vehicle No': 'nunique',
            'site': 'nunique'
        }).round(2)
        
        # Flatten column names
        hourly_stats.columns = ['Trip_Count', 'Total_Weight_kg', 'Avg_Weight_kg', 'Unique_Vehicles', 'Unique_Sites']
        hourly_stats.index.name = 'Hour'
        
        # Add hour labels
        hourly_stats['Time_Period'] = hourly_stats.index.map(lambda x: f"{x:02d}:00-{x+1:02d}:00")
        
        # Reorder columns
        hourly_stats = hourly_stats[['Time_Period', 'Trip_Count', 'Total_Weight_kg', 'Avg_Weight_kg', 'Unique_Vehicles', 'Unique_Sites']]
        
        print("Hourly Trip Distribution:")
        print(hourly_stats.to_string())
        
        # Peak hour analysis
        peak_hour = hourly_stats['Trip_Count'].idxmax()
        peak_trips = hourly_stats.loc[peak_hour, 'Trip_Count']
        print(f"\n🔥 Peak Hour: {peak_hour}:00-{peak_hour+1}:00 with {peak_trips} trips")
        
        return hourly_stats.reset_index()
    
    def output_4_cluster_performance(self):
        """Output 4: DataFrame with cluster-wide performance for all sites"""
        print("\n" + "="*50)
        print("🏘️  OUTPUT 4: CLUSTER-WIDE PERFORMANCE")
        print("="*50)
        
        # Group by cluster and site for comprehensive analysis
        cluster_performance = self.df.groupby(['cluster', 'site']).agg({
            'Ticket No': 'count',
            'Net Weight': ['sum', 'mean', 'std'],
            'Vehicle No': 'nunique',
            'Date': ['min', 'max'],
            'agency': lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else 'Unknown'
        }).round(2)
        
        # Flatten column names
        cluster_performance.columns = [
            'Total_Trips', 'Total_Weight_kg', 'Avg_Weight_per_Trip', 'Weight_Std_Dev',
            'Unique_Vehicles', 'First_Trip_Date', 'Last_Trip_Date', 'Primary_Agency'
        ]
        
        # Calculate additional metrics
        cluster_performance['Days_Active'] = (
            pd.to_datetime(cluster_performance['Last_Trip_Date']) - 
            pd.to_datetime(cluster_performance['First_Trip_Date'])
        ).dt.days + 1
        
        cluster_performance['Trips_per_Day'] = (
            cluster_performance['Total_Trips'] / cluster_performance['Days_Active']
        ).round(2)
        
        cluster_performance['Weight_per_Day_kg'] = (
            cluster_performance['Total_Weight_kg'] / cluster_performance['Days_Active']
        ).round(2)
        
        # Sort by total trips
        cluster_performance = cluster_performance.sort_values('Total_Trips', ascending=False)
        
        print("Cluster Performance Summary:")
        print(cluster_performance.to_string())
        
        # Top performing clusters
        print(f"\n🏆 Top Performing Site: {cluster_performance.index[0]} with {cluster_performance.iloc[0]['Total_Trips']} trips")
        
        return cluster_performance.reset_index()
    
    def output_5_daily_trends(self):
        """Output 5: Daily trends analysis"""
        print("\n" + "="*50)
        print("📈 OUTPUT 5: DAILY TRENDS ANALYSIS")
        print("="*50)
        
        daily_stats = self.df.groupby('Date').agg({
            'Ticket No': 'count',
            'Net Weight': 'sum',
            'Vehicle No': 'nunique',
            'site': 'nunique'
        }).round(2)
        
        daily_stats.columns = ['Daily_Trips', 'Daily_Weight_kg', 'Daily_Vehicles', 'Daily_Sites']
        
        # Calculate moving averages
        daily_stats['Trips_7day_MA'] = daily_stats['Daily_Trips'].rolling(window=7).mean().round(2)
        daily_stats['Weight_7day_MA'] = daily_stats['Daily_Weight_kg'].rolling(window=7).mean().round(2)
        
        # Recent performance (last 7 days)
        recent_data = daily_stats.tail(7)
        avg_recent_trips = recent_data['Daily_Trips'].mean()
        avg_recent_weight = recent_data['Daily_Weight_kg'].mean()
        
        print(f"📊 Recent 7-day Average:")
        print(f"   Trips per day: {avg_recent_trips:.1f}")
        print(f"   Weight per day: {avg_recent_weight:,.0f} kg")
        
        # Show recent trends
        print(f"\n📅 Last 7 Days Performance:")
        print(recent_data[['Daily_Trips', 'Daily_Weight_kg', 'Daily_Vehicles']].to_string())
        
        return daily_stats.reset_index()
    
    def output_6_vehicle_utilization(self):
        """Output 6: Vehicle utilization analysis"""
        print("\n" + "="*50)
        print("🚛 OUTPUT 6: VEHICLE UTILIZATION ANALYSIS")
        print("="*50)
        
        vehicle_stats = self.df.groupby('Vehicle No').agg({
            'Ticket No': 'count',
            'Net Weight': ['sum', 'mean'],
            'Date': ['min', 'max', 'nunique'],
            'site': 'nunique',
            'cluster': lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else 'Unknown'
        }).round(2)
        
        vehicle_stats.columns = [
            'Total_Trips', 'Total_Weight_kg', 'Avg_Weight_per_Trip',
            'First_Trip', 'Last_Trip', 'Days_Active', 'Sites_Served', 'Primary_Cluster'
        ]
        
        # Calculate utilization metrics
        vehicle_stats['Trips_per_Active_Day'] = (
            vehicle_stats['Total_Trips'] / vehicle_stats['Days_Active']
        ).round(2)
        
        # Sort by total trips
        vehicle_stats = vehicle_stats.sort_values('Total_Trips', ascending=False)
        
        # Show top performers
        top_vehicles = vehicle_stats.head(10)
        print("Top 10 Most Active Vehicles:")
        print(top_vehicles[['Total_Trips', 'Total_Weight_kg', 'Days_Active', 'Trips_per_Active_Day']].to_string())
        
        print(f"\n📋 Fleet Summary:")
        print(f"   Total Vehicles: {len(vehicle_stats)}")
        print(f"   Average Trips per Vehicle: {vehicle_stats['Total_Trips'].mean():.1f}")
        print(f"   Most Active Vehicle: {vehicle_stats.index[0]} ({vehicle_stats.iloc[0]['Total_Trips']} trips)")
        
        return vehicle_stats.reset_index()
    
    def output_7_material_breakdown(self):
        """Output 7: Material type analysis"""
        print("\n" + "="*50)
        print("🗂️  OUTPUT 7: MATERIAL TYPE BREAKDOWN")
        print("="*50)
        
        material_stats = self.df.groupby('Material Name').agg({
            'Ticket No': 'count',
            'Net Weight': ['sum', 'mean'],
            'Vehicle No': 'nunique',
            'site': 'nunique'
        }).round(2)
        
        material_stats.columns = ['Total_Trips', 'Total_Weight_kg', 'Avg_Weight_per_Trip', 'Vehicles_Used', 'Sites_Collected']
        
        # Calculate percentages
        material_stats['Percentage_of_Trips'] = (material_stats['Total_Trips'] / material_stats['Total_Trips'].sum() * 100).round(2)
        material_stats['Percentage_of_Weight'] = (material_stats['Total_Weight_kg'] / material_stats['Total_Weight_kg'].sum() * 100).round(2)
        
        material_stats = material_stats.sort_values('Total_Weight_kg', ascending=False)
        
        print("Material Type Analysis:")
        print(material_stats.to_string())
        
        # Dominant material
        dominant_material = material_stats.index[0]
        print(f"\n🏆 Dominant Material: {dominant_material}")
        print(f"   {material_stats.loc[dominant_material, 'Percentage_of_Weight']:.1f}% of total weight")
        
        return material_stats.reset_index()
    
    def output_8_efficiency_metrics(self):
        """Output 8: Overall efficiency and KPI metrics"""
        print("\n" + "="*50)
        print("⚡ OUTPUT 8: EFFICIENCY & KPI METRICS")
        print("="*50)
        
        # Calculate various efficiency metrics
        total_trips = len(self.df)
        total_weight = self.df['Net Weight'].sum()
        total_days = (self.df['Date'].max() - self.df['Date'].min()).days + 1
        unique_vehicles = self.df['Vehicle No'].nunique()
        unique_sites = self.df['site'].nunique()
        
        # Create efficiency metrics DataFrame
        metrics = {
            'Metric': [
                'Total Trips',
                'Total Weight Collected (kg)',
                'Average Weight per Trip (kg)',
                'Total Active Days',
                'Average Trips per Day',
                'Average Weight per Day (kg)',
                'Fleet Size (Unique Vehicles)',
                'Sites Covered',
                'Average Trips per Vehicle',
                'Vehicle Utilization Rate (%)',
                'Weight Efficiency (kg/vehicle/day)'
            ],
            'Value': [
                f"{total_trips:,}",
                f"{total_weight:,.0f}",
                f"{total_weight/total_trips:.1f}",
                f"{total_days}",
                f"{total_trips/total_days:.1f}",
                f"{total_weight/total_days:,.0f}",
                f"{unique_vehicles}",
                f"{unique_sites}",
                f"{total_trips/unique_vehicles:.1f}",
                f"{(self.df.groupby('Vehicle No')['Date'].nunique().mean() / total_days * 100):.1f}",
                f"{(total_weight / unique_vehicles / total_days):,.0f}"
            ]
        }
        
        kpi_df = pd.DataFrame(metrics)
        
        print("Key Performance Indicators:")
        for _, row in kpi_df.iterrows():
            print(f"  📊 {row['Metric']}: {row['Value']}")
        
        # Performance benchmarks
        print(f"\n🎯 Performance Assessment:")
        trips_per_day = total_trips / total_days
        if trips_per_day > 100:
            print(f"   ✅ High Activity: {trips_per_day:.1f} trips/day")
        elif trips_per_day > 50:
            print(f"   🟡 Moderate Activity: {trips_per_day:.1f} trips/day") 
        else:
            print(f"   🔴 Low Activity: {trips_per_day:.1f} trips/day")
            
        return kpi_df
    
    def generate_all_outputs(self):
        """Generate all 8 outputs"""
        if self.df is None:
            print("❌ Cannot generate outputs: No data loaded")
            print("Please fix the file path issue first.")
            return {}
            
        print("🚀 WASTE MANAGEMENT DATA ANALYSIS")
        print("=" * 60)
        
        results = {}
        
        try:
            results['output_1'] = self.output_1_agency_name()
            results['output_2'] = self.output_2_total_trips_day()
            results['output_3'] = self.output_3_trips_per_hour()
            results['output_4'] = self.output_4_cluster_performance()
            results['output_5'] = self.output_5_daily_trends()
            results['output_6'] = self.output_6_vehicle_utilization()
            results['output_7'] = self.output_7_material_breakdown()
            results['output_8'] = self.output_8_efficiency_metrics()
            
            print("\n" + "="*60)
            print("✅ ALL OUTPUTS GENERATED SUCCESSFULLY!")
            print("="*60)
            
        except Exception as e:
            print(f"❌ Error generating outputs: {e}")
            import traceback
            traceback.print_exc()
            
        return results

# USAGE EXAMPLE:
if __name__ == "__main__":
    # Method 1: Try with just the filename (if in same directory)
    print("🔍 Attempting to load data...")
    print("📁 Current working directory:", os.getcwd())
    
    # Check what files are available
    print("📄 Files in current directory:")
    for f in os.listdir('.'):
        print(f"   - {f}")
    
    if os.path.exists('data'):
        print("📄 Files in data directory:")
        for f in os.listdir('data'):
            print(f"   - {f}")
    
    analyzer = WasteManagementAnalyzer(
        data_file_path='waste_management_data_updated.csv',
        target_date='2025-06-05'  # Optional: specify target date or leave None for latest
    )
    
    # Only proceed if data was loaded successfully
    if analyzer.df is not None:
        # Generate all outputs
        all_results = analyzer.generate_all_outputs()
        
        # Access individual outputs:
        if all_results:
            print("\n" + "="*60)
            print("📊 QUICK ACCESS TO KEY RESULTS:")
            print("="*60)
            if 'output_1' in all_results:
                print(f"🏢 Primary Agency: {all_results['output_1']['primary_agency']}")
            if 'output_2' in all_results:
                print(f"🚛 Total trips on target date: {all_results['output_2']['total_trips']}")
            
            # Save specific DataFrames if needed:
            # all_results['output_3'].to_csv('hourly_trips.csv', index=False)
            # all_results['output_4'].to_csv('cluster_performance.csv', index=False)
    else:
        print("\n" + "="*60)
        print("🚨 SETUP INSTRUCTIONS")
        print("="*60)
        print("To run this script successfully:")
        print("1. Save your CSV file as 'waste_management_data_updated.csv'")
        print("2. Put it in the same folder as this Python script")
        print("3. OR create a 'data' folder and put the CSV there")
        print("4. OR update the file path in the script to match your file location")
        print("\nExample file structure:")
        print("📁 your_project_folder/")
        print("   📄 waste_analyzer.py")
        print("   📄 waste_management_data_updated.csv")
        print("\nOR:")
        print("📁 your_project_folder/")
        print("   📄 waste_analyzer.py")
        print("   📁 data/")
        print("      📄 waste_management_data_updated.csv")
        print("\n💡 You can also modify the script to use a different file path:")
        print("   analyzer = WasteManagementAnalyzer('/full/path/to/your/file.csv')")