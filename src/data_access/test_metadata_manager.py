"""
Test Metadata Manager - Test case metadata storage, retrieval, and search
Minimal GREEN phase implementation
"""
import json
import os
from typing import Dict, Any, List, Optional
from pathlib import Path

class TestMetadataManager:
    """REAL test metadata management with storage, retrieval, and search"""
    
    def __init__(self, metadata_dir: str):
        self.metadata_dir = Path(metadata_dir)
        self.metadata_dir.mkdir(exist_ok=True)
        self.metadata_file = self.metadata_dir / 'metadata.json'
        self._metadata = self._load_metadata()
    
    def _load_metadata(self) -> Dict[str, Any]:
        """Load metadata from file"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}
    
    def _save_metadata(self) -> bool:
        """Save metadata to file"""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self._metadata, f, indent=2)
            return True
        except Exception:
            return False
    
    def store_metadata(self, test_id: str, metadata: Dict[str, Any]) -> bool:
        """Store test metadata"""
        try:
            self._metadata[test_id] = metadata
            return self._save_metadata()
        except Exception:
            return False
    
    def get_metadata(self, test_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve test metadata"""
        return self._metadata.get(test_id)
    
    def search_by_tags(self, tags: List[str]) -> List[Dict[str, Any]]:
        """Search metadata by tags"""
        results = []
        for test_id, metadata in self._metadata.items():
            test_tags = metadata.get('tags', [])
            if any(tag in test_tags for tag in tags):
                result = metadata.copy()
                result['test_id'] = test_id
                results.append(result)
        return results
    
    def search_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Search metadata by category"""
        results = []
        for test_id, metadata in self._metadata.items():
            if metadata.get('category') == category:
                result = metadata.copy()
                result['test_id'] = test_id
                results.append(result)
        return results
    
    def update_metadata(self, test_id: str, updates: Dict[str, Any]) -> bool:
        """Update test metadata"""
        if test_id in self._metadata:
            self._metadata[test_id].update(updates)
            return self._save_metadata()
        return False