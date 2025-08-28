import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def analyze_existing_data_and_add_records():
    """
    Analyze existing waste management data and add new records
    for Kurnool, Nandyal, and Ongole within the last 3 days (excluding June 8th)
    """
    
    # Load existing data
    try:
        df = pd.read_csv('waste_management_data_20250606_004558.csv')
        print(f"Loaded existing data: {len(df)} records")
        print(f"Columns: {df.columns.tolist()}")
    except FileNotFoundError:
        print("CSV file not found. Please ensure the file is in the current directory.")
        return
    
    # Analyze existing weights for realistic random generation
    existing_empty_weights = df['Empty Weight'].dropna()
    existing_loaded_weights = df['Loaded Weight'].dropna()
    existing_net_weights = df['Net Weight'].dropna()
    
    # Calculate statistics for weight generation
    empty_weight_stats = {
        'median': existing_empty_weights.median(),
        'mean': existing_empty_weights.mean(),
        'std': existing_empty_weights.std(),
        'min': existing_empty_weights.min(),
        'max': existing_empty_weights.max()
    }
    
    loaded_weight_stats = {
        'median': existing_loaded_weights.median(),
        'mean': existing_loaded_weights.mean(),
        'std': existing_loaded_weights.std(),
        'min': existing_loaded_weights.min(),
        'max': existing_loaded_weights.max()
    }
    
    net_weight_stats = {
        'median': existing_net_weights.median(),
        'mean': existing_net_weights.mean(),
        'std': existing_net_weights.std(),
        'min': existing_net_weights.min(),
        'max': existing_net_weights.max()
    }
    
    print("\nExisting Weight Statistics:")
    print(f"Empty Weight - Median: {empty_weight_stats['median']:.0f}, Mean: {empty_weight_stats['mean']:.0f}")
    print(f"Loaded Weight - Median: {loaded_weight_stats['median']:.0f}, Mean: {loaded_weight_stats['mean']:.0f}")
    print(f"Net Weight - Median: {net_weight_stats['median']:.0f}, Mean: {net_weight_stats['mean']:.0f}")
    
    def generate_realistic_weight(stats, base_range_factor=0.8):
        """Generate realistic weight based on existing data statistics"""
        # Use a combination of median and mean with some variation
        base_weight = (stats['median'] + stats['mean']) / 2
        # Add realistic variation (±20% of the base weight)
        variation = base_weight * base_range_factor * (random.random() - 0.5)
        weight = int(base_weight + variation)
        # Ensure it's within reasonable bounds
        return max(stats['min'], min(stats['max'], weight))
    
    # Define date range (last 3 days excluding June 8th)
    # Assuming current date context, using June 6, 7, and 9, 2025
    valid_dates = [
        datetime(2025, 6, 6),
        datetime(2025, 6, 7),
        datetime(2025, 6, 9)
    ]
    
    # Location configurations
    locations_config = {
        'Kurnool': {'ticket_start': 214, 'ticket_end': 233},
        'Nandyal': {'ticket_start': 1766, 'ticket_end': 1783},
        'Ongole': {'ticket_start': 144, 'ticket_end': 159}
    }
    
    # Get the current maximum record_index to continue numbering
    max_record_index = df['record_index'].max() if 'record_index' in df.columns else 0
    
    new_records = []
    current_record_index = max_record_index + 1
    
    # Generate records for each location
    for location, config in locations_config.items():
        ticket_numbers = list(range(config['ticket_start'], config['ticket_end'] + 1))
        
        print(f"\nGenerating records for {location}:")
        print(f"Ticket numbers: {config['ticket_start']} to {config['ticket_end']} ({len(ticket_numbers)} tickets)")
        
        for ticket_no in ticket_numbers:
            # Select random date from valid dates
            selected_date = random.choice(valid_dates)
            
            # Generate realistic weights
            empty_weight = generate_realistic_weight(empty_weight_stats)
            loaded_weight = generate_realistic_weight(loaded_weight_stats)
            
            # Ensure loaded weight is greater than empty weight
            if loaded_weight <= empty_weight:
                loaded_weight = empty_weight + random.randint(500, 2000)
            
            # Calculate net weight
            net_weight = loaded_weight - empty_weight
            
            # Create new record
            new_record = {
                'source_location': location,
                'fetch_timestamp': None,  # NULL
                'record_index': current_record_index,
                'Date': selected_date.strftime('%Y-%m-%d'),
                'Empty Weight': empty_weight,
                'Empty Weight Date': None,  # NULL
                'Empty Weight Time': None,  # NULL
                'Load Weight Date': None,  # NULL
                'Load Weight Time': None,  # NULL
                'Loaded Weight': loaded_weight,
                'Material Name': None,  # NULL
                'Net Weight': net_weight,
                'Site': location,  # Same as source_location as specified
                'Supplier Name': None,  # NULL
                'Ticket No': ticket_no,
                'Time': None,  # NULL
                'Vehicle No': None  # NULL
            }
            
            new_records.append(new_record)
            current_record_index += 1
            
            print(f"  Ticket {ticket_no}: Date={selected_date.strftime('%Y-%m-%d')}, "
                  f"Empty={empty_weight}, Loaded={loaded_weight}, Net={net_weight}")
    
    # Convert new records to DataFrame
    new_df = pd.DataFrame(new_records)
    print(f"\nGenerated {len(new_df)} new records")
    
    # Combine with existing data
    combined_df = pd.concat([df, new_df], ignore_index=True)
    print(f"Total records after addition: {len(combined_df)}")
    
    # Save to new file
    output_filename = 'waste_management_data_updated.csv'
    combined_df.to_csv(output_filename, index=False)
    print(f"\nData saved to: {output_filename}")
    
    # Show summary of new records by location and date
    print("\nSummary of new records:")
    for location in locations_config.keys():
        location_records = new_df[new_df['source_location'] == location]
        print(f"\n{location}: {len(location_records)} records")
        for date in valid_dates:
            date_str = date.strftime('%Y-%m-%d')
            count = len(location_records[location_records['Date'] == date_str])
            if count > 0:
                print(f"  {date_str}: {count} records")
    
    return combined_df

def verify_data_integrity():
    """Verify the integrity of the generated data"""
    try:
        df = pd.read_csv('waste_management_data_updated.csv')
        
        print("\nData Integrity Check:")
        print(f"Total records: {len(df)}")
        
        # Check new locations
        new_locations = ['Kurnool', 'Nandyal', 'Ongole']
        for location in new_locations:
            location_data = df[df['source_location'] == location]
            print(f"\n{location}:")
            print(f"  Records: {len(location_data)}")
            print(f"  Ticket range: {location_data['Ticket No'].min()} - {location_data['Ticket No'].max()}")
            print(f"  Dates: {sorted(location_data['Date'].unique())}")
            print(f"  Weight ranges - Empty: {location_data['Empty Weight'].min()}-{location_data['Empty Weight'].max()}")
            print(f"                   Loaded: {location_data['Loaded Weight'].min()}-{location_data['Loaded Weight'].max()}")
            print(f"                   Net: {location_data['Net Weight'].min()}-{location_data['Net Weight'].max()}")
        
        # Check for data consistency
        inconsistent_records = df[df['Loaded Weight'] <= df['Empty Weight']]
        if len(inconsistent_records) > 0:
            print(f"\nWARNING: {len(inconsistent_records)} records have loaded weight <= empty weight")
        else:
            print("\n✓ All records have consistent weight relationships (Loaded > Empty)")
        
        # Check date exclusions
        june_8_records = df[df['Date'] == '2025-06-08']
        if len(june_8_records) == 0:
            print("✓ No records on June 8th (as requested)")
        else:
            print(f"WARNING: Found {len(june_8_records)} records on June 8th")
            
    except FileNotFoundError:
        print("Updated CSV file not found. Please run the data generation first.")

if __name__ == "__main__":
    print("=== Waste Management Data Generator ===")
    print("Adding records for Kurnool, Nandyal, and Ongole")
    print("Date range: Last 3 days (excluding June 8th)")
    print("=" * 50)
    
    # Generate and add new records
    combined_data = analyze_existing_data_and_add_records()
    
    # Verify the results
    print("\n" + "=" * 50)
    verify_data_integrity()
    
    print("\n=== Generation Complete ===")
    print("New file created: waste_management_data_updated.csv")
    print("You can now use this updated file in your application.")