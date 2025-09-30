"""
Test Repository for Data Access Layer - LAY-003-02-01-001
Enhanced with caching, structured data classes, and comprehensive error handling.
"""
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass
from functools import lru_cache

@dataclass
class TestMetadata:
    """Structured test metadata with validation"""
    test_id: str
    position_context: str
    test_type: str
    created_at: str
    stored_at: Optional[str] = None
    mobile_context: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'test_id': self.test_id,
            'position_context': self.position_context,
            'test_type': self.test_type,
            'created_at': self.created_at,
            'stored_at': self.stored_at,
            'mobile_context': self.mobile_context
        }

class TestRepository:
    """Enhanced repository for test metadata with caching and mobile support"""
    
    def __init__(self, storage_path: str = "./data/tests", cache_size: int = 128):
        """Initialize TestRepository with configurable caching"""
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.cache_size = cache_size
        self._position_cache = {}  # Position-based cache
        self._mobile_cache = {}   # Mobile context cache
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # Performance metrics
        self.metrics = {
            'store_operations': 0,
            'retrieve_operations': 0,
            'cache_hits': 0,
            'cache_misses': 0
        }
        
    def store_test(self, test_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Store basic test information with enhanced validation
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Validate required fields
            required_fields = ['test_id', 'position_context', 'test_type']
            missing_fields = [field for field in required_fields 
                            if field not in test_data]
            
            if missing_fields:
                error_msg = f"Missing required fields: {', '.join(missing_fields)}"
                return False, error_msg
            
            # Create structured metadata
            metadata = TestMetadata(
                test_id=test_data['test_id'],
                position_context=test_data['position_context'],
                test_type=test_data['test_type'],
                created_at=test_data.get('created_at', 
                                       datetime.now().isoformat()),
                stored_at=datetime.now().isoformat(),
                mobile_context=test_data.get('mobile_context')
            )
            
            # Store to file
            filename = f"{metadata.test_id}.json"
            filepath = self.storage_path / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(metadata.to_dict(), f, indent=2)
            
            # Update cache
            if metadata.position_context in self._position_cache:
                self._position_cache[metadata.position_context].append(
                    metadata.to_dict())
            
            # Update metrics
            self.metrics['store_operations'] += 1
            
            self.logger.info(f"Successfully stored test {metadata.test_id}")
            return True, "Test stored successfully"
            
        except Exception as e:
            self.logger.error(f"Error storing test data: {e}")
            return False, f"Storage error: {str(e)}"
    
    @lru_cache(maxsize=64)
    def get_tests_by_position(self, position_context: str) -> Tuple[
            List[Dict[str, Any]], str]:
        """
        Retrieve tests by contextual position with caching
        
        Returns:
            Tuple of (tests: List, status_message: str)
        """
        try:
            # Check cache first
            if position_context in self._position_cache:
                self.metrics['cache_hits'] += 1
                return (self._position_cache[position_context], 
                       "Retrieved from cache")
            
            self.metrics['cache_misses'] += 1
            tests = []
            
            # Scan all test files
            for filepath in self.storage_path.glob("*.json"):
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        test_data = json.load(f)
                        
                    # Filter by position context
                    if test_data.get('position_context') == position_context:
                        tests.append(test_data)
                        
                except json.JSONDecodeError:
                    self.logger.warning(f"Corrupted file skipped: {filepath}")
                    continue
                    
            # Update cache
            self._position_cache[position_context] = tests
            self.metrics['retrieve_operations'] += 1
            
            return tests, f"Retrieved {len(tests)} tests"
            
        except Exception as e:
            self.logger.error(f"Error retrieving tests: {e}")
            return [], f"Retrieval error: {str(e)}"
    
    def store_mobile_context(self, test_id: str, 
                           mobile_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Store mobile context for responsive testing with validation
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Validate mobile data
            if not isinstance(mobile_data, dict):
                return False, "Mobile data must be a dictionary"
                
            filename = f"{test_id}.json"
            filepath = self.storage_path / filename
            
            if not filepath.exists():
                return False, f"Test {test_id} not found"
                
            with open(filepath, 'r', encoding='utf-8') as f:
                test_data = json.load(f)
                
            test_data['mobile_context'] = mobile_data
            test_data['last_updated'] = datetime.now().isoformat()
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(test_data, f, indent=2)
            
            # Update mobile cache
            self._mobile_cache[test_id] = mobile_data
            
            self.logger.info(f"Mobile context updated for test {test_id}")
            return True, "Mobile context stored successfully"
            
        except Exception as e:
            self.logger.error(f"Error storing mobile context: {e}")
            return False, f"Storage error: {str(e)}"
    
    def get_responsive_data(self, test_id: str) -> Tuple[
            Dict[str, Any], str]:
        """
        Retrieve responsive/mobile data for test with caching
        
        Returns:
            Tuple of (mobile_data: Dict, status_message: str)
        """
        try:
            # Check mobile cache first
            if test_id in self._mobile_cache:
                self.metrics['cache_hits'] += 1
                return (self._mobile_cache[test_id], 
                       "Retrieved from mobile cache")
            
            filename = f"{test_id}.json"
            filepath = self.storage_path / filename
            
            if not filepath.exists():
                return {}, f"Test {test_id} not found"
                
            with open(filepath, 'r', encoding='utf-8') as f:
                test_data = json.load(f)
            
            mobile_context = test_data.get('mobile_context', {})
            
            # Update cache
            self._mobile_cache[test_id] = mobile_context
            self.metrics['cache_misses'] += 1
            
            return mobile_context, f"Retrieved mobile data for {test_id}"
            
        except Exception as e:
            self.logger.error(f"Error retrieving mobile data: {e}")
            return {}, f"Retrieval error: {str(e)}"
    
    def get_responsive_data(self, device_type: str) -> Optional[Dict[str, Any]]:
        """
        Test responsive data access patterns
        
        Args:
            device_type: Type of device (mobile, tablet, desktop)
            
        Returns:
            Responsive data configuration or None
        """
        try:
            responsive_config = {
                'device_type': device_type,
                'timestamp': datetime.now().isoformat(),
                'data_available': True
            }
            
            if device_type == 'mobile':
                responsive_config.update({
                    'max_items': 10,
                    'compact_view': True,
                    'touch_optimized': True,
                    'reduced_data': True
                })
            elif device_type == 'tablet':
                responsive_config.update({
                    'max_items': 20,
                    'grid_view': True,
                    'touch_optimized': True
                })
            else:  # desktop
                responsive_config.update({
                    'max_items': 50,
                    'full_view': True,
                    'keyboard_optimized': True
                })
                
            return responsive_config
            
        except Exception as e:
            print(f"Error getting responsive data: {e}")
            return None
