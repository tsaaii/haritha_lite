#!/usr/bin/env python3
"""
GCS JSON to CSV Processor - Complete Date Filtering Version
Process JSON files from GCS bucket and convert to CSV with strict date filtering
"""

import json
import pandas as pd
from google.cloud import storage
import io
import logging
from typing import Dict, List, Any, Set
from datetime import datetime
import datetime as dt
import sys
import os
import re

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
yesterday = (dt.date.today() - dt.timedelta(days=1)).strftime("%Y-%m-%d")
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
        if 'GOOGLE_CLOUD_PROJECT' in os.environ:
            client = storage.Client(project=os.environ['GOOGLE_CLOUD_PROJECT'])
        else:
            client = storage.Client()
        
        bucket = client.bucket(BUCKET_NAME)
        bucket.reload()
        logger.info(f"✅ Successfully authenticated and connected to bucket: {BUCKET_NAME}")
        return client
    except Exception as e:
        logger.error(f"❌ Authentication failed: {e}")
        logger.error("Try: gcloud auth application-default login")
        return None


def parse_date_from_string(date_str: str) -> str:
    """Parse date from various formats and return in YYYY-MM-DD format"""
    if not date_str or str(date_str).strip() == "" or str(date_str).lower() in ['nan', 'none', 'null']:
        return ""
    
    date_str = str(date_str).strip()
    
    # Remove time part if present
    if " " in date_str:
        date_str = date_str.split(" ")[0]
    
    # Keep only digits and common separators
    date_str = re.sub(r'[^0-9\-/.]', '', date_str)
    
    # Common date formats to try
    date_formats = [
        "%Y-%m-%d",      # 2025-06-29
        "%d-%m-%Y",      # 29-06-2025
        "%Y/%m/%d",      # 2025/06/29
        "%d/%m/%Y",      # 29/06/2025
        "%Y%m%d",        # 20250629
        "%d.%m.%Y",      # 29.06.2025
        "%Y.%m.%d",      # 2025.06.29
    ]
    
    for fmt in date_formats:
        try:
            parsed_date = datetime.strptime(date_str, fmt)
            return parsed_date.strftime("%Y-%m-%d")
        except ValueError:
            continue
    
    # Try to extract YYYYMMDD pattern
    yyyymmdd_match = re.search(r'(\d{8})', date_str)
    if yyyymmdd_match:
        try:
            date_part = yyyymmdd_match.group(1)
            parsed_date = datetime.strptime(date_part, "%Y%m%d")
            return parsed_date.strftime("%Y-%m-%d")
        except ValueError:
            pass
    
    logger.debug(f"Could not parse date: '{date_str}'")
    return ""


def is_target_date_record(record: Dict[str, Any], target_date: str) -> bool:
    """Check if a record matches the target date"""
    date_fields = ["date", "Date", "record_date", "timestamp", "created_date"]
    
    for field in date_fields:
        if field in record:
            record_date = parse_date_from_string(record[field])
            if record_date == target_date:
                return True
    
    # Check timestamp fields
    timestamp_fields = ["cloud_upload_timestamp", "first_timestamp", "second_timestamp"]
    for field in timestamp_fields:
        if field in record:
            timestamp_str = str(record[field]).strip()
            if timestamp_str and " " in timestamp_str:
                date_part = timestamp_str.split(" ")[0]
                record_date = parse_date_from_string(date_part)
                if record_date == target_date:
                    return True
    
    return False


def find_json_backup_folders(client, base_folder: str, target_date: str) -> List[str]:
    """Find all possible json_backups folders for a given base folder and date"""
    bucket = client.bucket(BUCKET_NAME)
    possible_paths = []
    
    patterns = [
        f"{base_folder}/json_backups/{target_date}/",
        f"{base_folder}/{target_date}/json_backups/",
        f"Default_Agency/{base_folder}/{target_date}/json_backups/",
        f"{base_folder}/{target_date}/json_backups/{base_folder}/",
        f"{base_folder}/json_backups/",
    ]
    
    for pattern in patterns:
        try:
            logger.info(f"  Checking pattern: {pattern}")
            blobs = list(bucket.list_blobs(prefix=pattern, max_results=5))
            if blobs:
                possible_paths.append(pattern)
                logger.info(f"  ✅ Found {len(blobs)} files in: {pattern}")
        except Exception as e:
            logger.debug(f"  Pattern {pattern} failed: {e}")
    
    return possible_paths


def get_all_json_files_from_paths(client, folder_paths: List[str]) -> Set[str]:
    """Get all unique JSON files from multiple paths"""
    bucket = client.bucket(BUCKET_NAME)
    json_files = set()
    
    for folder_path in folder_paths:
        try:
            logger.info(f"  Scanning path: {folder_path}")
            blobs = bucket.list_blobs(prefix=folder_path)
            path_files = []
            
            for blob in blobs:
                if blob.name.endswith('.json') and blob.size > 0:
                    json_files.add(blob.name)
                    path_files.append(blob.name)
            
            logger.info(f"    Found {len(path_files)} JSON files in {folder_path}")
        except Exception as e:
            logger.error(f"    Error listing files in {folder_path}: {e}")
    
    logger.info(f"  Total unique JSON files found: {len(json_files)}")
    return json_files


def debug_dates_in_files(client, json_files: Set[str], target_date: str):
    """Debug function to show what dates are in JSON files"""
    logger.info(f"🔍 DEBUG: Analyzing dates in sample JSON files...")
    
    bucket = client.bucket(BUCKET_NAME)
    found_dates = {}
    sample_records = []
    
    for json_file in list(json_files)[:5]:  # Check first 5 files
        try:
            blob = bucket.blob(json_file)
            json_content = blob.download_as_text()
            json_data = json.loads(json_content)
            
            if isinstance(json_data, list):
                records = json_data
            elif isinstance(json_data, dict):
                records = [json_data]
            else:
                continue
            
            for record in records[:3]:  # Check first 3 records per file
                date_fields = ["date", "Date", "record_date", "timestamp"]
                
                record_info = {"file": json_file.split("/")[-1], "dates": {}}
                
                for field in date_fields:
                    if field in record:
                        raw_value = str(record[field])
                        parsed_value = parse_date_from_string(raw_value)
                        record_info["dates"][field] = f"'{raw_value}' -> '{parsed_value}'"
                        
                        if parsed_value:
                            found_dates[parsed_value] = found_dates.get(parsed_value, 0) + 1
                
                if record_info["dates"]:
                    sample_records.append(record_info)
                    if len(sample_records) >= 10:
                        break
            
            if len(sample_records) >= 10:
                break
        except Exception as e:
            logger.debug(f"Error analyzing {json_file}: {e}")
    
    logger.info(f"🎯 Looking for: {target_date}")
    logger.info(f"📅 Dates found in files:")
    for date, count in sorted(found_dates.items()):
        status = "✅" if date == target_date else "❌"
        logger.info(f"   {status} {date}: {count} records")
    
    logger.info(f"📋 Sample date formats:")
    for record in sample_records[:3]:
        logger.info(f"   File: {record['file']}")
        for field, value in record['dates'].items():
            logger.info(f"      {field}: {value}")
    
    return found_dates


def transform_json_record(record: Dict[str, Any], source_file: str, folder_source: str) -> Dict[str, Any]:
    """Transform a JSON record to match target schema"""
    transformed = {}
    
    # Initialize all columns
    for col in TARGET_COLUMNS:
        transformed[col] = ""
    
    # Field mapping
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
    
    # Ensure date is in consistent format
    if transformed["date"]:
        parsed_date = parse_date_from_string(transformed["date"])
        if parsed_date:
            transformed["date"] = parsed_date
    
    # Add cluster mapping
    site_name = transformed["site_name"]
    transformed["cluster"] = CLUSTER_MAPPING.get(site_name, "")
    
    # Add metadata
    transformed["_source_file"] = source_file
    transformed["_processed_timestamp"] = datetime.now().isoformat()
    transformed["_folder_source"] = folder_source
    
    return transformed


def process_json_files(client, json_files: Set[str], folder_source: str, target_date: str) -> List[Dict[str, Any]]:
    """Process JSON files and filter by target date"""
    
    # Debug what dates are in the files
    debug_dates_in_files(client, json_files, target_date)
    
    bucket = client.bucket(BUCKET_NAME)
    all_records = []
    target_date_records = 0
    other_date_records = 0
    
    for json_file in json_files:
        try:
            logger.info(f"    Processing: {json_file}")
            blob = bucket.blob(json_file)
            json_content = blob.download_as_text()
            json_data = json.loads(json_content)
            
            if isinstance(json_data, list):
                records = json_data
            elif isinstance(json_data, dict):
                records = [json_data]
            else:
                logger.warning(f"    Unexpected JSON structure in {json_file}")
                continue
            
            file_records = []
            for record in records:
                if is_target_date_record(record, target_date):
                    transformed = transform_json_record(record, json_file, folder_source)
                    # Double check the date after transformation
                    final_date = parse_date_from_string(transformed.get('date', ''))
                    if final_date == target_date:
                        file_records.append(transformed)
                        target_date_records += 1
                    else:
                        other_date_records += 1
                else:
                    other_date_records += 1
            
            all_records.extend(file_records)
            
            if file_records:
                logger.info(f"    Added {len(file_records)} records from {json_file}")
            else:
                logger.info(f"    No records from {target_date} found in {json_file}")
                
        except Exception as e:
            logger.error(f"    Failed to process {json_file}: {e}")
    
    logger.info(f"  📊 Processing results:")
    logger.info(f"    Records from {target_date}: {target_date_records}")
    logger.info(f"    Records from other dates (skipped): {other_date_records}")
    
    return all_records


def create_record_hash(record: Dict[str, Any]) -> str:
    """Create a hash for duplicate detection"""
    key_fields = ['ticket_no', 'vehicle_no', 'date', 'time', 'site_name']
    key_values = []
    
    for field in key_fields:
        value = record.get(field, "").strip()
        key_values.append(value)
    
    return "|".join(key_values)


def remove_duplicate_records(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Remove duplicate records"""
    seen_hashes = set()
    unique_records = []
    duplicate_count = 0
    
    for record in records:
        record_hash = create_record_hash(record)
        
        if record_hash not in seen_hashes:
            seen_hashes.add(record_hash)
            unique_records.append(record)
        else:
            duplicate_count += 1
    
    if duplicate_count > 0:
        logger.warning(f"⚠️  Removed {duplicate_count} duplicate records")
    
    return unique_records


def strict_date_filter(records: List[Dict[str, Any]], target_date: str) -> List[Dict[str, Any]]:
    """Final strict date filtering before CSV creation"""
    logger.info(f"🔍 Applying final strict date filter for {target_date}...")
    
    date_filtered_records = []
    wrong_date_count = 0
    empty_date_count = 0
    
    for record in records:
        record_date = parse_date_from_string(record.get('date', ''))
        
        if not record_date:
            empty_date_count += 1
            logger.debug(f"Skipping record with empty date: {record.get('ticket_no', 'Unknown')}")
        elif record_date == target_date:
            date_filtered_records.append(record)
        else:
            wrong_date_count += 1
            logger.debug(f"Skipping record from {record_date}: {record.get('ticket_no', 'Unknown')}")
    
    logger.info(f"📊 Final date filtering:")
    logger.info(f"   ✅ Records from {target_date}: {len(date_filtered_records)}")
    logger.info(f"   ❌ Records from other dates: {wrong_date_count}")
    logger.info(f"   ⚠️  Records with empty dates: {empty_date_count}")
    
    return date_filtered_records


def main():
    """Main processing function"""
    print("🚀 GCS JSON to CSV Processor (Strict Date Filtering)")
    print("=" * 55)
    print(f"🎯 Target Date: {TARGET_DATE}")
    print("")
    
    # Check authentication
    client = check_authentication()
    if not client:
        sys.exit(1)
    
    all_records = []
    
    # Process each base folder
    for base_folder in BASE_FOLDERS:
        print(f"\n📁 Processing folder: {base_folder}")
        print("-" * 40)
        
        json_backup_paths = find_json_backup_folders(client, base_folder, TARGET_DATE)
        
        if not json_backup_paths:
            logger.warning(f"⚠️  No json_backups folders found for {base_folder}")
            continue
        
        json_files = get_all_json_files_from_paths(client, json_backup_paths)
        
        if json_files:
            logger.info(f"  Processing {len(json_files)} unique files from {base_folder}")
            records = process_json_files(client, json_files, base_folder, TARGET_DATE)
            all_records.extend(records)
            logger.info(f"  Added {len(records)} records from {base_folder}")
    
    # Check if we have any records
    if not all_records:
        logger.error(f"❌ No records found for date {TARGET_DATE}")
        sys.exit(1)
    
    # Remove duplicates
    logger.info(f"\n🔍 Removing duplicate records...")
    unique_records = remove_duplicate_records(all_records)
    
    # Apply final strict date filtering
    final_records = strict_date_filter(unique_records, TARGET_DATE)
    
    if not final_records:
        logger.error(f"❌ No records remain after strict date filtering for {TARGET_DATE}")
        sys.exit(1)
    
    # Create DataFrame
    df = pd.DataFrame(final_records)
    
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
    
    # Save to GCS
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
    print(f"🎯 Target Date: {TARGET_DATE}")
    print(f"📊 Total records from {TARGET_DATE}: {len(final_records):,}")
    print(f"📁 CSV file: {csv_filename}")
    
    # Verify dates in final CSV
    date_counts = df['date'].value_counts()
    print(f"\n📅 Date Distribution in Final CSV:")
    for date, count in date_counts.items():
        status = "✅" if date == TARGET_DATE else "❌"
        print(f"   {status} {date}: {count:,} records")
    
    # Final verification
    wrong_dates = df[df['date'] != TARGET_DATE]
    if len(wrong_dates) > 0:
        print(f"\n❌ ERROR: Found {len(wrong_dates)} records with wrong dates!")
    else:
        print(f"\n✅ VERIFIED: All {len(df)} records are from {TARGET_DATE}")
    
    # Show cluster distribution
    cluster_counts = df['cluster'].value_counts()
    if not cluster_counts.empty:
        print(f"\n📈 Cluster Distribution:")
        for cluster, count in cluster_counts.items():
            print(f"   {cluster or 'Unknown'}: {count:,} records")


if __name__ == "__main__":
    main()
