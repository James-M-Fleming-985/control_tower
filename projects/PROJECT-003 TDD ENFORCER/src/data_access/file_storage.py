"""
File Storage for Data Access Layer - LAY-003-02-01-001
Handles file-based storage integration for test data persistence.
"""
import json
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path

class FileStorage:
    """File-based storage integration for test data"""
    
    def __init__(self, storage_root: str = "./data/file_storage"):
        """Initialize FileStorage with configurable root directory"""
        self.storage_root = Path(storage_root)
        self.storage_root.mkdir(parents=True, exist_ok=True)
        
    def store(self, key: str, data: Dict[str, Any]) -> bool:
        """
        Store data with specified key
        
        Args:
            key: Unique identifier for the data
            data: Data to store
            
        Returns:
            True if storage successful, False otherwise
        """
        try:
            # Sanitize key for filename
            safe_key = "".join(c for c in key if c.isalnum() or c in ('_', '-'))
            filename = f"{safe_key}.json"
            filepath = self.storage_root / filename
            
            # Add metadata
            storage_data = {
                'key': key,
                'data': data,
                'stored_at': datetime.now().isoformat(),
                'storage_type': 'file_storage'
            }
            
            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(storage_data, f, indent=2)
                
            return True
            
        except Exception as e:
            print(f"Error storing data: {e}")
            return False
    
    def retrieve(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve data by key
        
        Args:
            key: Key to retrieve data for
            
        Returns:
            Retrieved data or None if not found
        """
        try:
            # Sanitize key for filename
            safe_key = "".join(c for c in key if c.isalnum() or c in ('_', '-'))
            filename = f"{safe_key}.json"
            filepath = self.storage_root / filename
            
            if not filepath.exists():
                return None
                
            # Read from file
            with open(filepath, 'r', encoding='utf-8') as f:
                storage_data = json.load(f)
                
            # Return the actual data (not the metadata wrapper)
            return storage_data.get('data')
            
        except Exception as e:
            print(f"Error retrieving data: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """Delete data by key"""
        try:
            safe_key = "".join(c for c in key if c.isalnum() or c in ('_', '-'))
            filename = f"{safe_key}.json"
            filepath = self.storage_root / filename
            
            if filepath.exists():
                filepath.unlink()
                return True
                
            return False
            
        except Exception as e:
            print(f"Error deleting data: {e}")
            return False
    
    def list_keys(self) -> list:
        """List all available keys"""
        keys = []
        try:
            for filepath in self.storage_root.glob("*.json"):
                with open(filepath, 'r', encoding='utf-8') as f:
                    storage_data = json.load(f)
                    keys.append(storage_data.get('key', filepath.stem))
        except Exception as e:
            print(f"Error listing keys: {e}")
            
        return keys
