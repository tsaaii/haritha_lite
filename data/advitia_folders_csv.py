#!/usr/bin/env python3
"""
GCS JSON to CSV Processor - Fixed Version
Process JSON files from GCS bucket and convert to CSV with proper schema mapping
"""

import json
import pandas as pd
from google.cloud import storage
import io
import logging
from typing import Dict, List, Any
from datetime import datetime
import datetime as dt
import sys
import os

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

yesterday = dt.date.today()
#(dt.date.today() - dt.timedelta(days=1)).strftime("%Y-%m-%d")

# Configuration
BUCKET_NAME = "advitia-weighbridge-data"
TARGET_DATE = yesterday

# Base folders to check
BASE_FOLDERS = [
    "Tharuni",
    "Tharuni_Associates", 
    "Saurashtra_Enviro_Projects_Pvt._Ltd./Bethamcherla",
    "Saurashtra_Enviro_Projects_Pvt._Ltd./Kurnool",
    "Saurashtra_Enviro_Projects_Pvt._Ltd./Nandyal",
    "Saurashtra_Enviro_Projects_Pvt._Ltd./Yemmiganur"
]

# Cluster mapping
CLUSTER_MAPPING = {
    "Bethamcherla": "Nandyal",
    "Yemmiganur": "Kurnool", 
    "Nandyal": "Nandyal",
    "Kurnool": "Kurnool"
}

# Target columns for final CSV
TARGET_COLUMNS = [
    "date", "time", "site_name", "cluster", "agency_name", "material", 
    "ticket_no", "vehicle_no", "transfer_party_name", "first_weight", 
    "first_timestamp", "second_weight", "second_timestamp", "net_weight", 
    "material_type", "first_front_image", "first_back_image", 
    "second_front_image", "second_back_image", "site_incharge", 
    "user_name", "cloud_upload_timestamp", "record_status", 
    "net_weight_calculated", "_source_file", "_processed_timestamp", "_folder_source"
]

def check_authentication():
    """Check if user is authenticated with Google Cloud"""
    try:
        # Try different authentication methods
        
        # Method 1: Try with explicit project (if set)
        try:
            if 'GOOGLE_CLOUD_PROJECT' in os.environ:
                client = storage.Client(project=os.environ['GOOGLE_CLOUD_PROJECT'])
            else:
                client = storage.Client()
        except Exception:
            # Method 2: Try without specifying project
            client = storage.Client()
        
        # Test the connection
        bucket = client.bucket(BUCKET_NAME)
        
        # Simple test - just check if bucket exists
        try:
            bucket.reload()
            logger.info(f"✅ Successfully authenticated and connected to bucket: {BUCKET_NAME}")
            return client
        except Exception as e:
            if "404" in str(e):
                logger.error(f"❌ Bucket {BUCKET_NAME} not found or no access")
            else:
                logger.error(f"❌ Bucket access failed: {e}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Authentication failed: {e}")
        logger.error("\nTry these steps:")
        logger.error("1. gcloud auth application-default login")
        logger.error("2. gcloud config set project YOUR_PROJECT_ID")
        logger.error("3. gcloud auth list (to verify)")
        return None

def find_json_backup_folders(client, base_folder: str, target_date: str) -> List[str]:
    """Find all possible json_backups folders for a given base folder and date"""
    bucket = client.bucket(BUCKET_NAME)
    possible_paths = []
    
    # Try different path patterns based on your working code
    patterns = [
        f"{base_folder}/json_backups/{target_date}/",
        f"{base_folder}/{target_date}/json_backups/",
        f"Default_Agency/{base_folder}/{target_date}/json_backups/",
        f"{base_folder}/{target_date}/json_backups/{base_folder}/"
    ]
    
    for pattern in patterns:
        try:
            logger.info(f"  Checking pattern: {pattern}")
            blobs = list(bucket.list_blobs(prefix=pattern, max_results=1))
            if blobs:
                possible_paths.append(pattern)
                logger.info(f"  ✅ Found files in: {pattern}")
        except Exception as e:
            logger.debug(f"  Pattern {pattern} failed: {e}")
            continue
    
    return possible_paths

def get_json_files_from_path(client, folder_path: str) -> List[str]:
    """Get all JSON files from a specific path"""
    bucket = client.bucket(BUCKET_NAME)
    json_files = []
    
    try:
        blobs = bucket.list_blobs(prefix=folder_path)
        for blob in blobs:
            if blob.name.endswith('.json') and blob.size > 0:
                json_files.append(blob.name)
        logger.info(f"  Found {len(json_files)} JSON files in {folder_path}")
    except Exception as e:
        logger.error(f"  Error listing files in {folder_path}: {e}")
    
    return json_files

def transform_json_record(record: Dict[str, Any], source_file: str, folder_source: str) -> Dict[str, Any]:
    """Transform a JSON record to match target schema"""
    transformed = {}
    
    # Initialize all columns with empty strings
    for col in TARGET_COLUMNS:
        transformed[col] = ""
    
    # Map fields (adjust these based on your actual JSON structure)
    field_mapping = {
        "date": ["date", "Date"],
        "time": ["time", "Time"], 
        "site_name": ["site_name", "Site", "site"],
        "agency_name": ["agency_name", "Agency", "agency"],
        "material": ["material", "Material", "Material Name"],
        "ticket_no": ["ticket_no", "Ticket No", "ticket_number"],
        "vehicle_no": ["vehicle_no", "Vehicle No", "vehicle_number"],
        "transfer_party_name": ["transfer_party_name", "Transfer Party"],
        "first_weight": ["first_weight", "Loaded Weight", "loaded_weight"],
        "first_timestamp": ["first_timestamp", "Load Weight Time"],
        "second_weight": ["second_weight", "Empty Weight", "empty_weight"],
        "second_timestamp": ["second_timestamp", "Empty Weight Time"],
        "net_weight": ["net_weight", "Net Weight"],
        "material_type": ["material_type", "Material Type", "material"],
        "first_front_image": ["first_front_image", "First Front Image"],
        "first_back_image": ["first_back_image", "First Back Image"],
        "second_front_image": ["second_front_image", "Second Front Image"],
        "second_back_image": ["second_back_image", "Second Back Image"],
        "site_incharge": ["site_incharge", "Site Incharge"],
        "user_name": ["user_name", "User Name"],
        "cloud_upload_timestamp": ["cloud_upload_timestamp", "Upload Time"],
        "record_status": ["record_status", "Status"],
        "net_weight_calculated": ["net_weight_calculated", "Calculated Weight"]
    }
    
    # Apply field mapping
    for target_field, possible_sources in field_mapping.items():
        for source_field in possible_sources:
            if source_field in record:
                transformed[target_field] = str(record[source_field]).strip()
                break
    
    # Add cluster mapping
    site_name = transformed["site_name"]
    transformed["cluster"] = CLUSTER_MAPPING.get(site_name, "")
    
    # Add metadata
    transformed["_source_file"] = source_file
    transformed["_processed_timestamp"] = datetime.now().isoformat()
    transformed["_folder_source"] = folder_source
    
    return transformed

def process_json_files(client, json_files: List[str], folder_source: str) -> List[Dict[str, Any]]:
    """Process all JSON files and return list of transformed records"""
    bucket = client.bucket(BUCKET_NAME)
    all_records = []
    
    for json_file in json_files:
        try:
            logger.info(f"    Processing: {json_file}")
            blob = bucket.blob(json_file)
            json_content = blob.download_as_text()
            json_data = json.loads(json_content)
            
            # Handle both single records and arrays
            if isinstance(json_data, list):
                records = json_data
            elif isinstance(json_data, dict):
                records = [json_data]
            else:
                logger.warning(f"    Unexpected JSON structure in {json_file}")
                continue
            
            # Transform each record
            for record in records:
                transformed = transform_json_record(record, json_file, folder_source)
                all_records.append(transformed)
                
        except Exception as e:
            logger.error(f"    Failed to process {json_file}: {e}")
            continue
    
    return all_records

def main():
    """Main processing function"""
    print("🚀 GCS JSON to CSV Processor")
    print("=" * 50)
    
    # Check authentication
    client = check_authentication()
    if not client:
        sys.exit(1)
    
    all_records = []
    
    # Process each base folder
    for base_folder in BASE_FOLDERS:
        print(f"\n📁 Processing folder: {base_folder}")
        print("-" * 40)
        
        # Find possible json_backups paths
        json_backup_paths = find_json_backup_folders(client, base_folder, TARGET_DATE)
        
        if not json_backup_paths:
            logger.warning(f"⚠️  No json_backups folders found for {base_folder}")
            continue
        
        # Process each found path
        for path in json_backup_paths:
            json_files = get_json_files_from_path(client, path)
            
            if json_files:
                logger.info(f"  Processing {len(json_files)} files from {path}")
                records = process_json_files(client, json_files, base_folder)
                all_records.extend(records)
                logger.info(f"  Added {len(records)} records")
    
    # Create final CSV
    if not all_records:
        logger.error("❌ No records found to process")
        sys.exit(1)
    
    logger.info(f"\n📊 Creating final CSV with {len(all_records)} total records")
    
    # Create DataFrame
    df = pd.DataFrame(all_records)
    
    # Ensure all target columns exist
    for col in TARGET_COLUMNS:
        if col not in df.columns:
            df[col] = ""
    
    # Reorder columns
    df = df[TARGET_COLUMNS]
    
    # Save locally
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_filename = f"weighbridge_records_{TARGET_DATE.replace('-', '')}_{timestamp}.csv"
    
    df.to_csv(csv_filename, index=False)
    logger.info(f"✅ CSV saved locally: {csv_filename}")
    
    # Also save to GCS
    try:
        bucket = client.bucket(BUCKET_NAME)
        gcs_path = f"processed_csv/{csv_filename}"
        csv_blob = bucket.blob(gcs_path)
        
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_blob.upload_from_string(csv_buffer.getvalue(), content_type='text/csv')
        
        logger.info(f"✅ CSV also saved to GCS: gs://{BUCKET_NAME}/{gcs_path}")
    except Exception as e:
        logger.warning(f"⚠️  Could not save to GCS: {e}")
    
    # Print summary
    print(f"\n🎉 Processing Complete!")
    print(f"📊 Total records: {len(all_records):,}")
    print(f"📁 CSV file: {csv_filename}")
    print(f"🔗 Columns: {len(df.columns)}")
    
    # Show sample of cluster distribution
    cluster_counts = df['cluster'].value_counts()
    if not cluster_counts.empty:
        print(f"\n📈 Cluster Distribution:")
        for cluster, count in cluster_counts.items():
            print(f"   {cluster or 'Unknown'}: {count:,} records")

if __name__ == "__main__":
    main()