"""
Position Repository for Data Access Layer - LAY-003-02-01-001
Handles contextual position information storage and retrieval.
"""
import json
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path

class PositionRepository:
    """Repository for context position tracking"""
    
    def __init__(self, storage_path: str = "./data/positions"):
        """Initialize PositionRepository with file-based storage"""
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
    def store_position(self, position_data: Dict[str, Any]) -> bool:
        """
        Store contextual position information
        
        Args:
            position_data: Dictionary containing position information
            
        Returns:
            True if storage successful, False otherwise
        """
        try:
            # Generate filename from position_id
            position_id = position_data.get('position_id', f'pos_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
            filename = f"{position_id}.json"
            filepath = self.storage_path / filename
            
            # Add storage timestamp
            position_data['stored_at'] = datetime.now().isoformat()
            
            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(position_data, f, indent=2)
                
            return True
            
        except Exception as e:
            print(f"Error storing position data: {e}")
            return False
    
    def get_positions_by_layer(self, layer: str) -> List[Dict[str, Any]]:
        """
        Get all positions for a specific layer
        
        Args:
            layer: The layer to filter positions by
            
        Returns:
            List of positions for the specified layer
        """
        positions = []
        
        try:
            # Scan all position files
            for filepath in self.storage_path.glob("*.json"):
                with open(filepath, 'r', encoding='utf-8') as f:
                    position_data = json.load(f)
                    
                # Filter by layer
                if position_data.get('layer') == layer:
                    positions.append(position_data)
                    
        except Exception as e:
            print(f"Error retrieving positions by layer: {e}")
            
        return positions
    
    def get_position_by_id(self, position_id: str) -> Dict[str, Any]:
        """Get specific position by ID"""
        try:
            filename = f"{position_id}.json"
            filepath = self.storage_path / filename
            
            if not filepath.exists():
                return {}
                
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        except Exception as e:
            print(f"Error retrieving position: {e}")
            return {}
