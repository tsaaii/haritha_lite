# file_watcher.py - Add this new file to your project root
import os
import time
from threading import Thread
from datetime import datetime
import pandas as pd

class CSVFileWatcher:
    def __init__(self, csv_path, callback_func=None, check_interval=2):
        """
        Simple file watcher that checks for CSV file changes
        
        Args:
            csv_path: Path to your CSV file
            callback_func: Function to call when file changes (optional)
            check_interval: How often to check in seconds (default: 2 seconds)
        """
        self.csv_path = csv_path
        self.callback_func = callback_func
        self.check_interval = check_interval
        self.last_modified = 0
        self.is_watching = False
        self.watch_thread = None
        
    def start_watching(self):
        """Start watching the CSV file in a background thread"""
        if self.is_watching:
            return
            
        self.is_watching = True
        self.last_modified = self._get_file_mtime()
        self.watch_thread = Thread(target=self._watch_loop, daemon=True)
        self.watch_thread.start()
        print(f"🔍 Started watching: {self.csv_path}")
        
    def stop_watching(self):
        """Stop watching the file"""
        self.is_watching = False
        print(f"⏹️ Stopped watching: {self.csv_path}")
        
    def _get_file_mtime(self):
        """Get file modification time"""
        try:
            return os.path.getmtime(self.csv_path)
        except OSError:
            return 0
            
    def _watch_loop(self):
        """Main watching loop that runs in background thread"""
        while self.is_watching:
            try:
                current_mtime = self._get_file_mtime()
                
                if current_mtime > self.last_modified:
                    print(f"📄 File changed detected: {datetime.now().strftime('%H:%M:%S')}")
                    self.last_modified = current_mtime
                    
                    # Call the callback function if provided
                    if self.callback_func:
                        try:
                            self.callback_func()
                        except Exception as e:
                            print(f"❌ Error in callback: {e}")
                            
                time.sleep(self.check_interval)
                
            except Exception as e:
                print(f"❌ Error in file watcher: {e}")
                time.sleep(self.check_interval)

# Global variable to store latest data
_latest_data = None
_data_timestamp = None

def load_csv_data():
    """Load the latest CSV data - this is your existing function with caching"""
    global _latest_data, _data_timestamp
    
    try:
        csv_path = os.path.join('data', 'waste_management_data_updated.csv')
        
        # Check if file exists
        if not os.path.exists(csv_path):
            print(f"❌ CSV file not found: {csv_path}")
            return None
            
        # Load data
        df = pd.read_csv(csv_path)
        _latest_data = df
        _data_timestamp = datetime.now()
        
        print(f"✅ Data loaded: {len(df)} records at {_data_timestamp.strftime('%H:%M:%S')}")
        return df
        
    except Exception as e:
        print(f"❌ Error loading CSV: {e}")
        return None

def get_latest_data():
    """Get the latest cached data"""
    global _latest_data
    return _latest_data

def get_data_timestamp():
    """Get when data was last updated"""
    global _data_timestamp
    return _data_timestamp

# Initialize the file watcher
csv_path = os.path.join('data', 'waste_management_data_updated.csv')
file_watcher = CSVFileWatcher(csv_path, callback_func=load_csv_data)

def start_file_monitoring():
    """Start monitoring the CSV file for changes"""
    # Load initial data
    load_csv_data()
    
    # Start watching for changes
    file_watcher.start_watching()
    
def stop_file_monitoring():
    """Stop monitoring the CSV file"""
    file_watcher.stop_watching()

if __name__ == "__main__":
    # Test the file watcher
    print("🚀 Testing file watcher...")
    start_file_monitoring()
    
    try:
        # Keep running to test
        while True:
            time.sleep(5)
            if _latest_data is not None:
                print(f"📊 Current data: {len(_latest_data)} records, last updated: {_data_timestamp}")
    except KeyboardInterrupt:
        print("\n🛑 Stopping file watcher...")
        stop_file_monitoring()