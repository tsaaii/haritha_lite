#!/usr/bin/env python3
"""
GCS Image Collector - Recursive JPG Downloader
Recursively finds all JPG images in specified GCS folders and downloads them to a local directory
Designed to run in Google Cloud Shell or any GCS-enabled environment
"""

import os
import logging
from typing import List, Dict, Set, Optional
from datetime import datetime
import re

# Google Cloud Storage
from google.cloud import storage

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GCSImageCollector:
    """Collect and organize JPG images from GCS folders"""
    
    def __init__(self, bucket_name: str, credentials_path: Optional[str] = None):
        """
        Initialize GCS Image Collector
        
        Args:
            bucket_name: Name of the GCS bucket
            credentials_path: Path to GCS service account credentials JSON file (optional)
        """
        self.bucket_name = bucket_name
        
        # Initialize GCS client
        if credentials_path:
            self.client = storage.Client.from_service_account_json(credentials_path)
        else:
            # Use default credentials (ADC - Application Default Credentials)
            self.client = storage.Client()
        
        self.bucket = self.client.bucket(bucket_name)
        
        # Statistics tracking
        self.stats = {
            'total_images_found': 0,
            'total_images_downloaded': 0,
            'failed_downloads': 0,
            'duplicate_names': 0,
            'folders_scanned': set(),
            'file_types_found': {},
            'errors': []
        }
    
    def is_image_file(self, filename: str) -> bool:
        """
        Check if file is a JPG image
        
        Args:
            filename: Name of the file
            
        Returns:
            True if file is a JPG image, False otherwise
        """
        if not filename:
            return False
        
        # Check for JPG/JPEG extensions (case insensitive)
        jpg_extensions = ['.jpg', '.jpeg', '.JPG', '.JPEG']
        return any(filename.lower().endswith(ext.lower()) for ext in jpg_extensions)
    
    def sanitize_filename(self, filename: str, source_path: str) -> str:
        """
        Create a unique filename to avoid conflicts in destination folder
        
        Args:
            filename: Original filename
            source_path: Source path of the file
            
        Returns:
            Sanitized unique filename
        """
        try:
            # Extract just the filename without path
            base_name = os.path.basename(filename)
            
            # If filename is already unique enough, return it
            if len(base_name) > 20:  # Assuming long filenames are already unique
                return base_name
            
            # Create a unique name by incorporating part of the source path
            path_parts = source_path.split('/')
            
            # Try to find date or ticket information in path
            unique_parts = []
            for part in path_parts:
                # Look for date patterns (YYYY-MM-DD)
                if re.match(r'\d{4}-\d{2}-\d{2}', part):
                    unique_parts.append(part.replace('-', ''))
                # Look for ticket patterns (T followed by numbers)
                elif re.match(r'[Tt]\d+', part):
                    unique_parts.append(part)
                # Look for time patterns or other identifiers
                elif len(part) > 3 and any(c.isdigit() for c in part):
                    unique_parts.append(part)
            
            # Create unique filename
            if unique_parts:
                name_without_ext = os.path.splitext(base_name)[0]
                extension = os.path.splitext(base_name)[1]
                unique_name = f"{name_without_ext}_{'_'.join(unique_parts[:2])}{extension}"
                return unique_name
            else:
                # Fallback: add timestamp
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                name_without_ext = os.path.splitext(base_name)[0]
                extension = os.path.splitext(base_name)[1]
                return f"{name_without_ext}_{timestamp}{extension}"
            
        except Exception as e:
            logger.warning(f"Error sanitizing filename {filename}: {e}")
            return filename
    
    def find_all_images(self, source_folders: List[str]) -> List[Dict]:
        """
        Recursively find all JPG images in specified folders
        
        Args:
            source_folders: List of source folder paths to search
            
        Returns:
            List of dictionaries containing image information
        """
        all_images = []
        
        for folder_path in source_folders:
            logger.info(f"Scanning folder: {folder_path}")
            
            try:
                # List all blobs with the folder prefix
                blobs = self.bucket.list_blobs(prefix=folder_path)
                
                folder_image_count = 0
                for blob in blobs:
                    # Track file types for statistics
                    if '.' in blob.name:
                        ext = os.path.splitext(blob.name)[1].lower()
                        self.stats['file_types_found'][ext] = self.stats['file_types_found'].get(ext, 0) + 1
                    
                    # Check if it's an image file
                    if self.is_image_file(blob.name):
                        image_info = {
                            'source_path': blob.name,
                            'filename': os.path.basename(blob.name),
                            'size': blob.size,
                            'folder': folder_path,
                            'subfolder_depth': len(blob.name.replace(folder_path, '').strip('/').split('/')) - 1
                        }
                        all_images.append(image_info)
                        folder_image_count += 1
                
                logger.info(f"Found {folder_image_count} images in {folder_path}")
                self.stats['folders_scanned'].add(folder_path)
                
            except Exception as e:
                error_msg = f"Error scanning folder {folder_path}: {e}"
                logger.error(error_msg)
                self.stats['errors'].append(error_msg)
        
        self.stats['total_images_found'] = len(all_images)
        logger.info(f"Total images found: {len(all_images)}")
        
        return all_images
    
    def download_images_to_local(self, images: List[Dict], local_destination: str) -> bool:
        """
        Download all found images from GCS to local directory
        
        Args:
            images: List of image information dictionaries
            local_destination: Local directory path to save images
            
        Returns:
            True if successful, False if errors occurred
        """
        if not images:
            logger.warning("No images to download")
            return True

        logger.info(f"Starting to download {len(images)} images to local directory: {local_destination}")
        
        # Create local destination directory
        os.makedirs(local_destination, exist_ok=True)
        
        used_filenames = set()

        for i, image_info in enumerate(images, 1):
            try:
                source_path = image_info['source_path']
                original_filename = image_info['filename']

                # Ensure unique name
                unique_filename = self.sanitize_filename(original_filename, source_path)
                counter = 1
                final_filename = unique_filename
                while final_filename.lower() in used_filenames:
                    name_without_ext, extension = os.path.splitext(unique_filename)
                    final_filename = f"{name_without_ext}_{counter:03d}{extension}"
                    counter += 1

                used_filenames.add(final_filename.lower())
                local_path = os.path.join(local_destination, final_filename)

                # Download blob to local file
                blob = self.bucket.blob(source_path)
                blob.download_to_filename(local_path)

                self.stats['total_images_downloaded'] += 1
                
                # Progress logging
                if i % 50 == 0 or i == len(images):
                    logger.info(f"Progress: {i}/{len(images)} downloaded ({(i/len(images)*100):.1f}%)")

            except Exception as e:
                error_msg = f"Failed to download {source_path}: {e}"
                logger.error(error_msg)
                self.stats['errors'].append(error_msg)
                self.stats['failed_downloads'] += 1

        logger.info(f"Download completed: {self.stats['total_images_downloaded']} successful, {self.stats['failed_downloads']} failed")
        return self.stats['failed_downloads'] == 0
    
    def generate_summary_report(self) -> str:
        """
        Generate a summary report of the collection process
        
        Returns:
            Summary report as string
        """
        report = f"""
GCS IMAGE DOWNLOAD SUMMARY REPORT
=================================

OPERATION DETAILS:
- Bucket: {self.bucket_name}
- Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

FOLDERS SCANNED:
{chr(10).join(f"  - {folder}" for folder in sorted(self.stats['folders_scanned']))}

RESULTS:
- Total images found: {self.stats['total_images_found']}
- Images successfully downloaded: {self.stats['total_images_downloaded']}
- Failed downloads: {self.stats['failed_downloads']}
- Filename conflicts resolved: {self.stats['duplicate_names']}

FILE TYPES ENCOUNTERED:
{chr(10).join(f"  {ext}: {count} files" for ext, count in sorted(self.stats['file_types_found'].items()))}

SUCCESS RATE: {(self.stats['total_images_downloaded'] / max(1, self.stats['total_images_found']) * 100):.2f}%

"""
        
        if self.stats['errors']:
            report += f"""
ERRORS ENCOUNTERED ({len(self.stats['errors'])}):
{chr(10).join(f"  - {error}" for error in self.stats['errors'][:10])}
"""
            if len(self.stats['errors']) > 10:
                report += f"  ... and {len(self.stats['errors']) - 10} more errors\n"
        
        return report
    
    def collect_images(self, source_folders: List[str], local_destination: str) -> bool:
        """
        Main function to download images from GCS folders to local directory
        
        Args:
            source_folders: List of source folder paths in GCS
            local_destination: Local directory path to save images
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info("Starting GCS image download process...")
            logger.info(f"Source folders: {source_folders}")
            logger.info(f"Local destination: {local_destination}")
            
            # Step 1: Find all images
            images = self.find_all_images(source_folders)
            
            if not images:
                logger.warning("No images found in source folders")
                return True
            
            # Step 2: Download images to local directory
            success = self.download_images_to_local(images, local_destination)
            
            # Step 3: Generate and display summary
            report = self.generate_summary_report()
            print(report)
            
            # Save report to local directory
            try:
                report_filename = f"download_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                local_report_path = os.path.join(local_destination, report_filename)
                with open(local_report_path, "w", encoding="utf-8") as f:
                    f.write(report)
                logger.info(f"Report saved to: {local_report_path}")
            except Exception as e:
                logger.warning(f"Could not save report locally: {e}")

            return success
            
        except Exception as e:
            logger.error(f"Fatal error in collect_images: {e}")
            return False


def main():
    """Main execution function"""
    
    # Configuration
    BUCKET_NAME = "advitia-weighbridge-data"
    CREDENTIALS_PATH = None  # None for ADC (Application Default Credentials)
    
    # Source folders to scan
    SOURCE_FOLDERS = [
        "Tharuni_Associates/Guntur",
    ]
    
    # Local destination directory
    LOCAL_DESTINATION = "downloaded_images_guntur"
    
    try:
        print("GCS Image Downloader - Download JPG Images Locally")
        print("=" * 60)
        print("This script finds all JPG images in specified GCS folders")
        print("and downloads them to a local directory on your computer.")
        print()
        
        # Allow user to customize settings
        bucket_name = input(f"Enter GCS bucket name [{BUCKET_NAME}]: ").strip()
        if not bucket_name:
            bucket_name = BUCKET_NAME
        
        local_dest = input(f"Enter local destination directory [{LOCAL_DESTINATION}]: ").strip()
        if not local_dest:
            local_dest = LOCAL_DESTINATION
        
        print(f"\nConfiguration:")
        print(f"  Bucket: {bucket_name}")
        print(f"  Source folders: {SOURCE_FOLDERS}")
        print(f"  Local destination: {os.path.abspath(local_dest)}")
        print()
        
        confirm = input("Proceed with image download? [y/N]: ").strip().lower()
        if confirm not in ['y', 'yes']:
            print("Operation cancelled.")
            return 0
        
        # Initialize collector
        collector = GCSImageCollector(bucket_name, CREDENTIALS_PATH)
        
        # Run download process
        success = collector.collect_images(SOURCE_FOLDERS, local_dest)
        
        if success:
            print(f"\n✓ Image download completed successfully!")
            print(f"✓ All JPG images saved to: {os.path.abspath(local_dest)}")
        else:
            print(f"\n⚠ Image download completed with some errors.")
            print(f"Check the logs and report for details.")
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n\nProcess interrupted by user.")
        return 1
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"\n❌ Fatal error: {e}")
        return 1


if __name__ == "__main__":
    import sys
    
    # Check for required dependencies
    try:
        from google.cloud import storage
    except ImportError:
        print("❌ Missing required package: google-cloud-storage")
        print("Install with: pip install google-cloud-storage")
        sys.exit(1)
    
    print("✓ google-cloud-storage: Available")
    print()
    
    # Run main function
    exit_code = main()
    sys.exit(exit_code)