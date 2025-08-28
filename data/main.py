# main.py - Complete Cloud Function for Weighbridge Processing + Viz CSV Generation (Multi-Path)
import json
import pandas as pd
from google.cloud import storage
import io
import logging
from typing import Dict, Any, List
from datetime import datetime
import functions_framework
import base64

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
BUCKET_NAME = "advitia-weighbridge-data"

# Multiple watch paths
WATCH_PREFIXES = [
    "Saurashtra_Enviro_Projects_Pvt._Ltd.",
    "Tharuni"
]

# CSV file paths for each source
CSV_PATHS = {
    "Saurashtra_Enviro_Projects_Pvt._Ltd.": "csv_outputs/data/Saurashtra_json.csv",
    "Tharuni": "csv_outputs/data/Tharuni_json.csv"
}

MAPPING_CSV = "csv_outputs/data/mapping.csv"  # Path to mapping CSV
VIZ_CSV = "csv_outputs/data/viz.csv"  # Output visualization CSV

def get_source_from_path(file_path: str) -> str:
    """
    Determine which source/company the file belongs to based on its path.
    
    Args:
        file_path: The full path of the file
        
    Returns:
        Source name or None if not found
    """
    for prefix in WATCH_PREFIXES:
        if file_path.startswith(prefix):
            return prefix
    return None

@functions_framework.cloud_event
def process_new_json_file(cloud_event):
    """
    Cloud Function triggered by Pub/Sub notification from GCS.
    Processes new weighbridge JSON files from multiple sources and updates viz.csv.
    """
    try:
        # Parse Pub/Sub message from GCS notification
        if hasattr(cloud_event, 'data') and 'message' in cloud_event.data:
            # Decode the Pub/Sub message
            message = cloud_event.data['message']
            
            if 'data' in message:
                # Decode base64 message data
                message_data = base64.b64decode(message['data']).decode('utf-8')
                event_data = json.loads(message_data)
            else:
                # Use attributes if no data
                event_data = message.get('attributes', {})
        else:
            # Fallback for direct event
            event_data = cloud_event.data

        # Extract file information from GCS notification
        bucket_name = event_data.get("bucketId", event_data.get("bucket", ""))
        file_name = event_data.get("objectId", event_data.get("name", ""))
        event_type = event_data.get("eventType", "unknown")
        
        logger.info(f"🔔 Pub/Sub Event triggered: {event_type}")
        logger.info(f"📁 Bucket: {bucket_name}")
        logger.info(f"📄 File: {file_name}")
        
        # Validate the event
        if not bucket_name or not file_name:
            logger.warning("⚠️  Missing bucket or file name in event")
            return "ignored_invalid_event"

        # Check if this is the correct bucket
        if bucket_name != BUCKET_NAME:
            logger.info(f"⏭️  Ignoring event from different bucket: {bucket_name}")
            return "ignored_different_bucket"

        # Check if file is in any of our watch paths
        source = get_source_from_path(file_name)
        if not source:
            logger.info(f"⏭️  Ignoring file outside watch paths: {file_name}")
            logger.info(f"📋 Monitored paths: {WATCH_PREFIXES}")
            return "ignored_outside_watch_paths"

        # Only process JSON files
        if not file_name.endswith('.json'):
            logger.info(f"⏭️  Ignoring non-JSON file: {file_name}")
            return "ignored_non_json"

        # Skip temporary files and system files
        if '/.tmp' in file_name or file_name.endswith('.tmp'):
            logger.info(f"⏭️  Ignoring temporary file: {file_name}")
            return "ignored_temp_file"

        logger.info(f"✅ Processing weighbridge JSON file from {source}: {file_name}")

        # Initialize GCS client
        client = storage.Client()
        bucket = client.bucket(bucket_name)

        # Process the JSON file and append to the appropriate CSV
        result = append_weighbridge_json_to_csv(bucket, file_name, source)

        # After updating source CSV, update viz.csv with combined data
        if "success" in result or "appended" in result:
            logger.info("📊 Updating viz.csv with combined data from all sources...")
            viz_result = update_viz_csv_combined(bucket)
            logger.info(f"📈 Viz CSV update result: {viz_result}")

        logger.info(f"🎉 Successfully processed {file_name}: {result}")
        return f"success_{result}"

    except Exception as e:
        error_msg = f"❌ Error processing event: {str(e)}"
        logger.error(error_msg)
        logger.error(f"Event data: {cloud_event.data}")
        return f"error_{str(e)}"

def process_weighbridge_json(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process weighbridge JSON data to ensure proper formatting for CSV.
    
    Args:
        data: JSON data from weighbridge system
        
    Returns:
        Processed dictionary ready for CSV
    """
    processed_data = {}
    
    # Expected fields from weighbridge JSON (based on user's format)
    expected_fields = [
        'date', 'time', 'site_name', 'agency_name', 'material', 'ticket_no',
        'vehicle_no', 'transfer_party_name', 'first_weight', 'first_timestamp',
        'second_weight', 'second_timestamp', 'net_weight', 'material_type',
        'first_front_image', 'first_back_image', 'second_front_image', 
        'second_back_image', 'site_incharge', 'user_name', 'cloud_upload_timestamp',
        'record_status', 'net_weight_calculated'
    ]
    
    # Process each expected field
    for field in expected_fields:
        if field in data:
            value = data[field]
            
            # Handle numeric fields (weights)
            if field in ['first_weight', 'second_weight', 'net_weight', 'net_weight_calculated']:
                try:
                    if value is not None and str(value).strip():
                        # Remove commas and convert to float
                        float_val = float(str(value).replace(',', '').strip())
                        processed_data[field] = int(float_val) if float_val.is_integer() else float_val
                    else:
                        processed_data[field] = 0
                except (ValueError, TypeError):
                    logger.warning(f"⚠️  Invalid numeric value for {field}: {value}")
                    processed_data[field] = 0
            else:
                # Handle string fields
                processed_data[field] = str(value).strip() if value is not None else ""
        else:
            # Add missing fields with default values
            if field in ['first_weight', 'second_weight', 'net_weight', 'net_weight_calculated']:
                processed_data[field] = 0
            else:
                processed_data[field] = ""
    
    # Handle any additional fields not in the expected list
    for key, value in data.items():
        if key not in expected_fields:
            logger.info(f"📝 Additional field found: {key} = {value}")
            processed_data[key] = str(value) if value is not None else ""
    
    return processed_data

def append_weighbridge_json_to_csv(bucket, json_file_path: str, source: str) -> str:
    """
    Process a weighbridge JSON file and append its data to the appropriate source CSV.
    
    Args:
        bucket: GCS bucket object
        json_file_path: Path to the JSON file
        source: Source company/prefix (e.g., "Tharuni" or "Saurashtra_Enviro_Projects_Pvt._Ltd.")
        
    Returns:
        Status message about what was done
    """
    try:
        # Get the target CSV path for this source
        target_csv = CSV_PATHS.get(source)
        if not target_csv:
            raise ValueError(f"No CSV path configured for source: {source}")
        
        # Read the JSON file
        logger.info(f"📖 Reading weighbridge JSON file from {source}: {json_file_path}")
        json_blob = bucket.blob(json_file_path)
        
        if not json_blob.exists():
            raise FileNotFoundError(f"JSON file not found: {json_file_path}")
        
        json_content = json_blob.download_as_text()
        json_data = json.loads(json_content)
        
        # Process JSON data into weighbridge records
        new_records = []
        
        if isinstance(json_data, list):
            # If JSON contains a list of weighbridge records
            for item in json_data:
                if isinstance(item, dict):
                    processed_item = process_weighbridge_json(item)
                    processed_item['_source_file'] = json_file_path
                    processed_item['_source_company'] = source
                    processed_item['_processed_timestamp'] = datetime.now().isoformat()
                    new_records.append(processed_item)
                else:
                    logger.warning(f"⚠️  Skipping non-dict item in JSON list: {type(item)}")
        elif isinstance(json_data, dict):
            # If JSON contains a single weighbridge record
            processed_item = process_weighbridge_json(json_data)
            processed_item['_source_file'] = json_file_path
            processed_item['_source_company'] = source
            processed_item['_processed_timestamp'] = datetime.now().isoformat()
            new_records.append(processed_item)
        else:
            # Handle unexpected JSON structure
            logger.warning(f"⚠️  Unexpected JSON structure: {type(json_data)}")
            new_records.append({
                'date': '',
                'time': '',
                'site_name': '',
                'agency_name': '',
                'material': '',
                'ticket_no': '',
                'vehicle_no': '',
                'transfer_party_name': '',
                'first_weight': 0,
                'first_timestamp': '',
                'second_weight': 0,
                'second_timestamp': '',
                'net_weight': 0,
                'material_type': '',
                'first_front_image': '',
                'first_back_image': '',
                'second_front_image': '',
                'second_back_image': '',
                'site_incharge': '',
                'user_name': '',
                'cloud_upload_timestamp': '',
                'record_status': '',
                'net_weight_calculated': 0,
                'raw_data': str(json_data),
                '_source_file': json_file_path,
                '_source_company': source,
                '_processed_timestamp': datetime.now().isoformat()
            })
        
        if not new_records:
            logger.warning(f"⚠️  No records extracted from {json_file_path}")
            return "no_records_extracted"
        
        logger.info(f"📊 Extracted {len(new_records)} weighbridge records from {source} JSON")
        
        # Log details of the weighbridge data being processed
        for i, record in enumerate(new_records):
            ticket_no = record.get('ticket_no', 'Unknown')
            vehicle_no = record.get('vehicle_no', 'Unknown')
            site_name = record.get('site_name', 'Unknown')
            net_weight = record.get('net_weight', 0)
            logger.info(f"   Record {i+1}: Ticket {ticket_no}, Vehicle {vehicle_no}, Site {site_name}, Net Weight {net_weight}kg")
        
        # Convert new records to DataFrame
        df_new = pd.DataFrame(new_records)
        
        # Ensure consistent data types for numeric columns
        numeric_columns = ['first_weight', 'second_weight', 'net_weight', 'net_weight_calculated']
        for col in numeric_columns:
            if col in df_new.columns:
                df_new[col] = pd.to_numeric(df_new[col], errors='coerce').fillna(0)
        
        # Check if target CSV exists
        csv_blob = bucket.blob(target_csv)
        
        if csv_blob.exists():
            logger.info(f"📄 Target CSV exists for {source}, reading: {target_csv}")
            # Read existing CSV
            existing_csv_content = csv_blob.download_as_text()
            df_existing = pd.read_csv(io.StringIO(existing_csv_content))
            
            logger.info(f"📊 Existing {source} CSV has {len(df_existing)} rows and {len(df_existing.columns)} columns")
            
            # Ensure consistent data types in existing CSV
            for col in numeric_columns:
                if col in df_existing.columns:
                    df_existing[col] = pd.to_numeric(df_existing[col], errors='coerce').fillna(0)
            
            # Get all columns that should be in the final CSV
            all_columns = set(df_existing.columns) | set(df_new.columns)
            
            # Add missing columns to both DataFrames with appropriate defaults
            for col in all_columns:
                if col not in df_existing.columns:
                    if col in numeric_columns:
                        df_existing[col] = 0
                    else:
                        df_existing[col] = ""
                if col not in df_new.columns:
                    if col in numeric_columns:
                        df_new[col] = 0
                    else:
                        df_new[col] = ""
            
            # Reorder columns to match existing CSV structure + new columns at the end
            existing_column_order = list(df_existing.columns)
            new_columns = [col for col in df_new.columns if col not in existing_column_order]
            final_column_order = existing_column_order + new_columns
            
            df_existing = df_existing[final_column_order]
            df_new = df_new[final_column_order]
            
            # Combine DataFrames
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
            
            # Remove duplicates based on ticket_no and timestamp (more specific than just source_file)
            if 'ticket_no' in df_combined.columns and 'cloud_upload_timestamp' in df_combined.columns:
                # Check for duplicates by ticket_no and cloud_upload_timestamp
                duplicate_mask = df_combined.duplicated(subset=['ticket_no', 'cloud_upload_timestamp'], keep='last')
                if duplicate_mask.any():
                    duplicates_count = duplicate_mask.sum()
                    logger.info(f"🔄 Removing {duplicates_count} duplicate records based on ticket_no and timestamp")
                    df_combined = df_combined[~duplicate_mask]
            else:
                # Fallback to source_file deduplication
                df_combined = df_combined.drop_duplicates(subset=['_source_file'], keep='last')
            
            action = f"appended_{len(df_new)}_records_to_existing_{len(df_existing)}_records_for_{source}"
            
        else:
            logger.info(f"📄 Target CSV doesn't exist for {source}, creating new: {target_csv}")
            
            # Ensure the csv_outputs/data directory structure exists
            test_blob = bucket.blob("csv_outputs/data/.keep")
            if not test_blob.exists():
                test_blob.upload_from_string("", content_type='text/plain')
                logger.info("📁 Created csv_outputs/data directory structure")
            
            df_combined = df_new
            action = f"created_new_csv_with_{len(df_new)}_records_for_{source}"
        
        # Save updated CSV
        logger.info(f"💾 Saving {source} CSV with {len(df_combined)} total records")
        csv_buffer = io.StringIO()
        df_combined.to_csv(csv_buffer, index=False)
        
        # Upload to GCS
        csv_blob.upload_from_string(
            csv_buffer.getvalue(),
            content_type='text/csv'
        )
        
        logger.info(f"✅ Successfully updated {target_csv}")
        logger.info(f"📈 Final {source} CSV stats:")
        logger.info(f"   - Total rows: {len(df_combined)}")
        logger.info(f"   - Total columns: {len(df_combined.columns)}")
        logger.info(f"   - New records added: {len(df_new)}")
        
        # Show sample of new data added
        if len(df_new) > 0:
            sample_record = df_new.iloc[0]
            logger.info(f"📋 Sample new {source} record:")
            logger.info(f"   - Date: {sample_record.get('date', 'N/A')}")
            logger.info(f"   - Ticket: {sample_record.get('ticket_no', 'N/A')}")
            logger.info(f"   - Vehicle: {sample_record.get('vehicle_no', 'N/A')}")
            logger.info(f"   - Site: {sample_record.get('site_name', 'N/A')}")
            logger.info(f"   - Net Weight: {sample_record.get('net_weight', 0)}kg")
        
        return action
        
    except Exception as e:
        logger.error(f"❌ Error processing {source} weighbridge JSON {json_file_path}: {str(e)}")
        raise

def update_viz_csv_combined(bucket) -> str:
    """
    Create/update viz.csv by combining data from all source CSVs and joining with mapping.csv
    
    Args:
        bucket: GCS bucket object
        
    Returns:
        Status message about the viz update
    """
    try:
        logger.info("📊 Starting combined viz.csv update process...")
        
        # Read mapping.csv
        mapping_blob = bucket.blob(MAPPING_CSV)
        if not mapping_blob.exists():
            logger.warning(f"⚠️  Mapping file not found: {MAPPING_CSV}")
            logger.info("💡 Upload mapping.csv first using the setup script")
            return "mapping_file_not_found"
        
        mapping_content = mapping_blob.download_as_text()
        df_mapping = pd.read_csv(io.StringIO(mapping_content))
        logger.info(f"📋 Loaded mapping data: {len(df_mapping)} rows, {len(df_mapping.columns)} columns")
        
        # Read and combine all source CSV files
        all_dataframes = []
        total_records = 0
        
        for source, csv_path in CSV_PATHS.items():
            csv_blob = bucket.blob(csv_path)
            if csv_blob.exists():
                logger.info(f"📄 Reading {source} data from: {csv_path}")
                csv_content = csv_blob.download_as_text()
                df_source = pd.read_csv(io.StringIO(csv_content))
                
                # Ensure source company column exists
                if '_source_company' not in df_source.columns:
                    df_source['_source_company'] = source
                
                all_dataframes.append(df_source)
                total_records += len(df_source)
                logger.info(f"   📊 {source}: {len(df_source)} records")
            else:
                logger.warning(f"⚠️  CSV file not found for {source}: {csv_path}")
        
        if not all_dataframes:
            logger.warning("⚠️  No source CSV files found")
            return "no_source_csvs_found"
        
        # Combine all source dataframes
        logger.info(f"🔗 Combining {len(all_dataframes)} source datasets with {total_records} total records")
        df_combined = pd.concat(all_dataframes, ignore_index=True, sort=False)
        
        logger.info(f"📋 Combined data: {len(df_combined)} rows, {len(df_combined.columns)} columns")
        logger.info(f"📋 Sources in combined data: {sorted(df_combined['_source_company'].unique())}")
        
        # Clean column names (remove extra spaces)
        df_mapping.columns = df_mapping.columns.str.strip()
        df_combined.columns = df_combined.columns.str.strip()
        
        # Ensure join columns exist
        if 'Site' not in df_mapping.columns:
            logger.error(f"❌ Column 'Site' not found in mapping.csv. Available columns: {list(df_mapping.columns)}")
            return "missing_site_column_in_mapping"
        
        if 'site_name' not in df_combined.columns:
            logger.error(f"❌ Column 'site_name' not found in combined data. Available columns: {list(df_combined.columns)}")
            return "missing_site_name_column_in_combined"
        
        # Clean the join columns (remove extra spaces, handle case)
        df_mapping['Site'] = df_mapping['Site'].astype(str).str.strip()
        df_combined['site_name'] = df_combined['site_name'].astype(str).str.strip()
        
        logger.info(f"🔗 Joining combined data with mapping on site_name = Site")
        logger.info(f"   Mapping sites: {sorted(df_mapping['Site'].unique()[:5])}...")
        logger.info(f"   Combined sites: {sorted(df_combined['site_name'].unique()[:5])}...")
        
        # Perform inner join
        df_joined = pd.merge(
            df_combined, 
            df_mapping, 
            left_on='site_name', 
            right_on='Site', 
            how='inner'
        )
        
        logger.info(f"🔗 Join result: {len(df_joined)} rows (from {len(df_combined)} combined + {len(df_mapping)} mapping)")
        
        if len(df_joined) == 0:
            logger.warning("⚠️  No matching records found between combined data and mapping")
            # Show some sample values for debugging
            logger.warning(f"Sample mapping Sites: {list(df_mapping['Site'].head())}")
            logger.warning(f"Sample combined site_names: {list(df_combined['site_name'].head())}")
            return "no_matching_sites"
        
        # Select required columns for viz.csv including source company
        required_columns = [
            'Agency', 'Sub_contractor', 'Cluster', 'Site', 'Machines', 
            'Total_capacity_per_day', 'Total_waste_to_be_remediated',
            'date', 'ticket_no', 'net_weight_calculated', '_source_company'
        ]
        
        # Check if all required columns exist
        missing_columns = [col for col in required_columns if col not in df_joined.columns]
        if missing_columns:
            logger.warning(f"⚠️  Missing columns in joined data: {missing_columns}")
            logger.info(f"Available columns: {list(df_joined.columns)}")
            
            # Add missing columns with default values
            for col in missing_columns:
                if col in ['net_weight_calculated']:
                    df_joined[col] = 0
                else:
                    df_joined[col] = ""
        
        # Create viz dataframe with required columns
        df_viz = df_joined[required_columns].copy()
        
        # Sort by source company, date and ticket_no for better organization
        if 'date' in df_viz.columns and 'ticket_no' in df_viz.columns:
            df_viz = df_viz.sort_values(['_source_company', 'date', 'ticket_no'], ascending=[True, False, True])
        
        # Save viz.csv
        logger.info(f"💾 Saving combined viz.csv with {len(df_viz)} records and {len(df_viz.columns)} columns")
        
        viz_buffer = io.StringIO()
        df_viz.to_csv(viz_buffer, index=False)
        
        viz_blob = bucket.blob(VIZ_CSV)
        viz_blob.upload_from_string(
            viz_buffer.getvalue(),
            content_type='text/csv'
        )
        
        logger.info(f"✅ Successfully updated {VIZ_CSV}")
        logger.info(f"📊 Combined Viz CSV stats:")
        logger.info(f"   - Total records: {len(df_viz)}")
        logger.info(f"   - Columns: {list(df_viz.columns)}")
        
        # Show breakdown by source company
        if '_source_company' in df_viz.columns:
            source_counts = df_viz['_source_company'].value_counts()
            logger.info(f"📋 Records by source:")
            for source, count in source_counts.items():
                logger.info(f"   - {source}: {count} records")
        
        # Show sample of latest records
        if len(df_viz) > 0:
            logger.info(f"📋 Sample viz records:")
            for i, row in df_viz.head(3).iterrows():
                site = row.get('Site', 'N/A')
                agency = row.get('Agency', 'N/A')
                source_company = row.get('_source_company', 'N/A')
                date = row.get('date', 'N/A')
                ticket = row.get('ticket_no', 'N/A')
                weight = row.get('net_weight_calculated', 0)
                logger.info(f"   {source_company} | {site} | {agency} | {date} | {ticket} | {weight}kg")
        
        return f"updated_combined_viz_with_{len(df_viz)}_records_from_{len(all_dataframes)}_sources"
        
    except Exception as e:
        logger.error(f"❌ Error updating combined viz.csv: {str(e)}")
        return f"viz_update_failed_{str(e)}"
