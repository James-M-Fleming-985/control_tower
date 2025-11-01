```python
"""
Heatmap Generator Module

This module provides functionality for generating heatmaps with support for
missing data handling, concurrent execution, and integration with feature orchestrator.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Union, Any, Tuple
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import logging
from functools import wraps
import time
from dataclasses import dataclass
import json
import warnings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class HeatmapConfig:
    """Configuration for heatmap generation."""
    missing_data_strategy: str = 'interpolate'  # 'interpolate', 'drop', 'fill'
    fill_value: float = 0.0
    normalize: bool = True
    color_map: str = 'viridis'
    concurrent: bool = True
    max_workers: Optional[int] = None
    chunk_size: int = 1000


class HeatmapGenerator:
    """
    Generates heatmaps from various data sources with support for missing data
    and concurrent processing.
    """
    
    def __init__(self, config: Optional[HeatmapConfig] = None):
        """
        Initialize the HeatmapGenerator.
        
        Args:
            config: Configuration object for heatmap generation
        """
        self.config = config or HeatmapConfig()
        self._feature_orchestrator = None
        
    def set_feature_orchestrator(self, orchestrator: Any) -> None:
        """
        Set the feature orchestrator for integration.
        
        Args:
            orchestrator: Feature orchestrator instance
        """
        self._feature_orchestrator = orchestrator
        
    def generate(self, data: Union[np.ndarray, pd.DataFrame, List, Dict],
                 x_labels: Optional[List[str]] = None,
                 y_labels: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Generate a heatmap from the provided data.
        
        Args:
            data: Input data (array, dataframe, list, or dict)
            x_labels: Labels for x-axis
            y_labels: Labels for y-axis
            
        Returns:
            Dictionary containing heatmap data and metadata
        """
        start_time = time.time()
        
        try:
            # Convert data to numpy array
            data_array = self._convert_to_array(data)
            
            # Handle missing data
            data_array = self._handle_missing_data(data_array)
            
            # Process data (potentially in parallel)
            if self.config.concurrent and data_array.size > self.config.chunk_size:
                processed_data = self._process_concurrent(data_array)
            else:
                processed_data = self._process_data(data_array)
                
            # Normalize if requested
            if self.config.normalize:
                processed_data = self._normalize_data(processed_data)
                
            # Generate labels if not provided
            if x_labels is None:
                x_labels = [f"X{i}" for i in range(processed_data.shape[1])]
            if y_labels is None:
                y_labels = [f"Y{i}" for i in range(processed_data.shape[0])]
                
            # Calculate statistics
            stats = self._calculate_statistics(processed_data)
            
            # Create result
            result = {
                'data': processed_data.tolist(),
                'x_labels': x_labels,
                'y_labels': y_labels,
                'statistics': stats,
                'config': {
                    'color_map': self.config.color_map,
                    'normalized': self.config.normalize,
                    'missing_data_strategy': self.config.missing_data_strategy
                },
                'metadata': {
                    'processing_time': time.time() - start_time,
                    'shape': processed_data.shape,
                    'dtype': str(processed_data.dtype)
                }
            }
            
            # Integrate with feature orchestrator if available
            if self._feature_orchestrator:
                self._feature_orchestrator.register_heatmap(result)
                
            logger.info(f"Heatmap generated in {result['metadata']['processing_time']:.3f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating heatmap: {str(e)}")
            raise
            
    def _convert_to_array(self, data: Union[np.ndarray, pd.DataFrame, List, Dict]) -> np.ndarray:
        """Convert various data types to numpy array."""
        if isinstance(data, np.ndarray):
            return data.copy()
        elif isinstance(data, pd.DataFrame):
            return data.values
        elif isinstance(data, list):
            return np.array(data)
        elif isinstance(data, dict):
            # Convert dict to 2D array
            if all(isinstance(v, (list, np.ndarray)) for v in data.values()):
                return np.array(list(data.values()))
            else:
                raise ValueError("Dictionary values must be lists or arrays")
        else:
            raise TypeError(f"Unsupported data type: {type(data)}")
            
    def _handle_missing_data(self, data: np.ndarray) -> np.ndarray:
        """Handle missing data according to strategy."""
        if not np.isnan(data).any():
            return data
            
        logger.info(f"Handling missing data with strategy: {self.config.missing_data_strategy}")
        
        if self.config.missing_data_strategy == 'drop':
            # Remove rows and columns with any NaN
            mask_rows = ~np.isnan(data).any(axis=1)
            mask_cols = ~np.isnan(data).any(axis=0)
            return data[mask_rows][:, mask_cols]
            
        elif self.config.missing_data_strategy == 'fill':
            # Fill with specified value
            data = data.copy()
            data[np.isnan(data)] = self.config.fill_value
            return data
            
        elif self.config.missing_data_strategy == 'interpolate':
            # Linear interpolation
            data = data.copy()
            if data.ndim == 1:
                data = pd.Series(data).interpolate(method='linear', limit_direction='both').values
            else:
                df = pd.DataFrame(data)
                df = df.interpolate(method='linear', axis=0, limit_direction='both')
                df = df.interpolate(method='linear', axis=1, limit_direction='both')
                data = df.values
            # Fill any remaining NaN with fill_value
            data[np.isnan(data)] = self.config.fill_value
            return data
            
        else:
            raise ValueError(f"Unknown missing data strategy: {self.config.missing_data_strategy}")
            
    def _process_data(self, data: np.ndarray) -> np.ndarray:
        """Process data array."""
        # Ensure 2D array
        if data.ndim == 1:
            data = data.reshape(-1, 1)
        elif data.ndim > 2:
            # Flatten higher dimensions
            data = data.reshape(data.shape[0], -1)
            
        return data
        
    def _process_concurrent(self, data: np.ndarray) -> np.ndarray:
        """Process data using concurrent execution."""
        # Ensure 2D array first
        data = self._process_data(data)
        
        # Split data into chunks for parallel processing
        n_chunks = max(1, data.shape[0] // self.config.chunk_size)
        chunks = np.array_split(data, n_chunks, axis=0)
        
        # Process chunks in parallel
        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            processed_chunks = list(executor.map(self._process_chunk, chunks))
            
        return np.vstack(processed_chunks)
        
    def _process_chunk(self, chunk: np.ndarray) -> np.ndarray:
        """Process a single chunk of data."""
        # Add any chunk-specific processing here
        return chunk
        
    def _normalize_data(self, data: np.ndarray) -> np.ndarray:
        """Normalize data to [0, 1] range."""
        data_min = np.nanmin(data)
        data_max = np.nanmax(data)
        
        if data_max == data_min:
            return np.zeros_like(data)
            
        return (data - data_min) / (data_max - data_min)
        
    def _calculate_statistics(self, data: np.ndarray) -> Dict[str, float]:
        """Calculate statistics for the data."""
        return {
            'mean': float(np.nanmean(data)),
            'std': float(np.nanstd(data)),
            'min': float(np.nanmin(data)),
            'max': float(np.nanmax(data)),
            'median': float(np.nanmedian(data)),
            'non_zero_count': int(np.count_nonzero(data)),
            'shape': list(data.shape)
        }
        

class BatchHeatmapGenerator(HeatmapGenerator):
    """Extended heatmap generator with batch processing capabilities."""
    
    def generate_batch(self, data_list: List[Union[np.ndarray, pd.DataFrame, List, Dict]],
                      labels: Optional[List[Tuple[List[str], List[str]]]] = None) -> List[Dict[str, Any]]:
        """
        Generate multiple heatmaps in batch.
        
        Args:
            data_list: List of data inputs
            labels: Optional list of (x_labels, y_labels) tuples
            
        Returns:
            List of heatmap results
        """
        if labels is None:
            labels = [(None, None)] * len(data_list)
            
        results = []
        
        # Use process pool for CPU-bound batch operations
        if self.config.concurrent and len(data_list) > 1:
            with ProcessPoolExecutor(max_workers=self.config.max_workers) as executor:
                futures = []
                for data, (x_labels, y_labels) in zip(data_list, labels):
                    future = executor.submit(self.generate, data, x_labels, y_labels)
                    futures.append(future)
                    
                for future in futures:
                    results.append(future.result())
        else:
            for data, (x_labels, y_labels) in zip(data_list, labels):
                results.append(self.generate(data, x_labels, y_labels))
                
        return results
        

def create_heatmap(data: Union[np.ndarray, pd.DataFrame, List, Dict],
                   config: Optional[HeatmapConfig] = None,
                   **kwargs) -> Dict[str, Any]:
    """
    Convenience function to create a heatmap.
    
    Args:
        data: Input data
        config: Optional configuration
        **kwargs: Additional arguments passed to generate()
        
    Returns:
        Heatmap result dictionary
    """
    generator = HeatmapGenerator(config)
    return generator.generate(data, **kwargs)


def benchmark_heatmap_performance(n_points: int = 10000) -> Dict[str, float]:
    """
    Benchmark heatmap generation performance.
    
    Args:
        n_points: Number of data points to test
        
    Returns:
        Performance metrics
    """
    # Generate random data
    data = np.random.randn(int(np.sqrt(n_points)), int(np.sqrt(n_points)))
    
    # Add some NaN values
    mask = np.random.random(data.shape) < 0.1
    data[mask] = np.nan
    
    # Test different configurations
    configs = [
        HeatmapConfig(concurrent=False),
        HeatmapConfig(concurrent=True),
        HeatmapConfig(missing_data_strategy='drop'),
        HeatmapConfig(missing_data_strategy='fill'),
        HeatmapConfig(missing_data_strategy='interpolate'),
    ]
    
    results = {}
    for i, config in enumerate(configs):
        generator = HeatmapGenerator(config)
        start_time = time.time()
        generator.generate(data)
        elapsed_time = time.time() - start_time
        results[f'config_{i}'] = elapsed_time
        
    return results
```