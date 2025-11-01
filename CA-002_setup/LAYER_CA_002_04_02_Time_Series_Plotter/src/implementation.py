```python
"""Time Series Plotter implementation for correlation overlays."""

import asyncio
import time
from typing import Dict, List, Optional, Tuple, Any, Union
import numpy as np
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.figure import Figure
from matplotlib.axes import Axes
import seaborn as sns
from concurrent.futures import ThreadPoolExecutor
import warnings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TimeSeriesPlotter:
    """Renders time series plots with correlation overlays."""
    
    def __init__(self, max_workers: int = 4):
        """Initialize the Time Series Plotter.
        
        Args:
            max_workers: Maximum number of worker threads for concurrent execution.
        """
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.feature_orchestrator = None
        
    def set_feature_orchestrator(self, orchestrator: Any) -> None:
        """Set the feature orchestrator for integration.
        
        Args:
            orchestrator: The feature orchestrator instance.
        """
        self.feature_orchestrator = orchestrator
        
    def plot_time_series_with_correlation(
        self, 
        data: Union[pd.DataFrame, Dict[str, List]], 
        correlation_data: Optional[Union[pd.DataFrame, Dict[str, List]]] = None,
        title: str = "Time Series with Correlation Overlay",
        figsize: Tuple[int, int] = (12, 8),
        date_column: str = "date",
        value_columns: Optional[List[str]] = None,
        correlation_threshold: float = 0.7,
        handle_missing: str = "interpolate"
    ) -> Dict[str, Any]:
        """Plot time series data with correlation overlays.
        
        Args:
            data: Time series data as DataFrame or dict.
            correlation_data: Optional correlation data.
            title: Plot title.
            figsize: Figure size as (width, height).
            date_column: Name of the date column.
            value_columns: List of value columns to plot.
            correlation_threshold: Threshold for highlighting correlations.
            handle_missing: How to handle missing data ('interpolate', 'drop', 'fill').
            
        Returns:
            Dict containing plot figure, statistics, and metadata.
            
        Raises:
            ValueError: If data format is invalid.
            RuntimeError: If plotting fails.
        """
        start_time = time.time()
        
        try:
            # Convert data to DataFrame if needed
            df = self._prepare_data(data, date_column)
            
            # Handle missing data
            df = self._handle_missing_data(df, handle_missing)
            
            # Determine value columns
            if value_columns is None:
                value_columns = [col for col in df.columns if col != date_column]
            
            # Create figure and axes
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize, height_ratios=[3, 1])
            
            # Plot time series
            self._plot_time_series(ax1, df, date_column, value_columns)
            
            # Calculate and plot correlations
            corr_matrix = self._calculate_correlations(df[value_columns])
            self._plot_correlation_overlay(ax2, corr_matrix, correlation_threshold)
            
            # Set title and layout
            fig.suptitle(title, fontsize=16)
            plt.tight_layout()
            
            # Calculate statistics
            stats = self._calculate_statistics(df[value_columns])
            
            # Prepare result
            result = {
                'figure': fig,
                'statistics': stats,
                'correlation_matrix': corr_matrix,
                'data_points': len(df),
                'columns_plotted': value_columns,
                'processing_time': time.time() - start_time,
                'missing_data_handled': handle_missing,
                'metadata': {
                    'date_range': (df[date_column].min(), df[date_column].max()),
                    'correlation_threshold': correlation_threshold,
                    'figsize': figsize
                }
            }
            
            # Integrate with feature orchestrator if available
            if self.feature_orchestrator:
                self._notify_orchestrator(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error plotting time series: {str(e)}")
            raise RuntimeError(f"Failed to plot time series: {str(e)}")
    
    async def plot_time_series_async(
        self,
        data: Union[pd.DataFrame, Dict[str, List]],
        **kwargs
    ) -> Dict[str, Any]:
        """Asynchronously plot time series with correlation overlays.
        
        Args:
            data: Time series data.
            **kwargs: Additional arguments for plot_time_series_with_correlation.
            
        Returns:
            Plot result dictionary.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor, 
            self.plot_time_series_with_correlation,
            data,
            **kwargs
        )
    
    def plot_multiple_series(
        self,
        datasets: List[Union[pd.DataFrame, Dict[str, List]]],
        titles: Optional[List[str]] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """Plot multiple time series concurrently.
        
        Args:
            datasets: List of datasets to plot.
            titles: Optional list of titles for each plot.
            **kwargs: Additional arguments for plotting.
            
        Returns:
            List of plot results.
        """
        if titles is None:
            titles = [f"Time Series {i+1}" for i in range(len(datasets))]
        
        futures = []
        for data, title in zip(datasets, titles):
            future = self.executor.submit(
                self.plot_time_series_with_correlation,
                data,
                title=title,
                **kwargs
            )
            futures.append(future)
        
        results = []
        for future in futures:
            try:
                result = future.result(timeout=10)
                results.append(result)
            except Exception as e:
                logger.error(f"Error in concurrent plotting: {str(e)}")
                results.append({'error': str(e)})
        
        return results
    
    def _prepare_data(
        self, 
        data: Union[pd.DataFrame, Dict[str, List]], 
        date_column: str
    ) -> pd.DataFrame:
        """Prepare data for plotting.
        
        Args:
            data: Input data.
            date_column: Name of date column.
            
        Returns:
            Prepared DataFrame.
            
        Raises:
            ValueError: If data format is invalid.
        """
        if isinstance(data, dict):
            df = pd.DataFrame(data)
        elif isinstance(data, pd.DataFrame):
            df = data.copy()
        else:
            raise ValueError("Data must be DataFrame or dict")
        
        # Ensure date column exists
        if date_column not in df.columns:
            raise ValueError(f"Date column '{date_column}' not found")
        
        # Convert to datetime if needed
        if not pd.api.types.is_datetime64_any_dtype(df[date_column]):
            df[date_column] = pd.to_datetime(df[date_column])
        
        # Sort by date
        df = df.sort_values(date_column)
        
        return df
    
    def _handle_missing_data(
        self, 
        df: pd.DataFrame, 
        method: str
    ) -> pd.DataFrame:
        """Handle missing data in DataFrame.
        
        Args:
            df: Input DataFrame.
            method: Method to handle missing data.
            
        Returns:
            DataFrame with handled missing data.
        """
        if method == 'interpolate':
            # Interpolate numeric columns
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            df[numeric_cols] = df[numeric_cols].interpolate(method='linear')
        elif method == 'drop':
            df = df.dropna()
        elif method == 'fill':
            # Forward fill then backward fill
            df = df.fillna(method='ffill').fillna(method='bfill')
        
        return df
    
    def _plot_time_series(
        self, 
        ax: Axes, 
        df: pd.DataFrame, 
        date_column: str, 
        value_columns: List[str]
    ) -> None:
        """Plot time series on axes.
        
        Args:
            ax: Matplotlib axes.
            df: DataFrame with data.
            date_column: Date column name.
            value_columns: Value columns to plot.
        """
        for col in value_columns:
            ax.plot(df[date_column], df[col], label=col, alpha=0.8)
        
        ax.set_xlabel('Date')
        ax.set_ylabel('Value')
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
        
        # Format x-axis dates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    
    def _calculate_correlations(
        self, 
        df: pd.DataFrame
    ) -> pd.DataFrame:
        """Calculate correlation matrix.
        
        Args:
            df: DataFrame with numeric data.
            
        Returns:
            Correlation matrix.
        """
        return df.corr()
    
    def _plot_correlation_overlay(
        self, 
        ax: Axes, 
        corr_matrix: pd.DataFrame, 
        threshold: float
    ) -> None:
        """Plot correlation heatmap overlay.
        
        Args:
            ax: Matplotlib axes.
            corr_matrix: Correlation matrix.
            threshold: Correlation threshold for highlighting.
        """
        # Create mask for values below threshold
        mask = np.abs(corr_matrix) < threshold
        
        # Plot heatmap
        sns.heatmap(
            corr_matrix, 
            mask=mask,
            annot=True,
            fmt='.2f',
            cmap='coolwarm',
            center=0,
            ax=ax,
            cbar_kws={'label': 'Correlation'}
        )
        
        ax.set_title(f'Correlations above {threshold}')
    
    def _calculate_statistics(
        self, 
        df: pd.DataFrame
    ) -> Dict[str, Any]:
        """Calculate statistics for the data.
        
        Args:
            df: DataFrame with numeric data.
            
        Returns:
            Dictionary of statistics.
        """
        stats = {
            'mean': df.mean().to_dict(),
            'std': df.std().to_dict(),
            'min': df.min().to_dict(),
            'max': df.max().to_dict(),
            'median': df.median().to_dict(),
            'skew': df.skew().to_dict(),
            'kurtosis': df.kurtosis().to_dict()
        }
        
        return stats
    
    def _notify_orchestrator(self, result: Dict[str, Any]) -> None:
        """Notify feature orchestrator of plot completion.
        
        Args:
            result: Plot result to send.
        """
        if hasattr(self.feature_orchestrator, 'notify'):
            self.feature_orchestrator.notify('plot_completed', result)
    
    def close(self) -> None:
        """Close the plotter and cleanup resources."""
        self.executor.shutdown(wait=True)
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# Performance optimization for large datasets
class OptimizedTimeSeriesPlotter(TimeSeriesPlotter):
    """Optimized version for handling large datasets efficiently."""
    
    def plot_time_series_with_correlation(
        self,
        data: Union[pd.DataFrame, Dict[str, List]],
        **kwargs
    ) -> Dict[str, Any]:
        """Optimized plotting for large datasets.
        
        Implements downsampling for datasets > 10K points to ensure
        performance requirements are met.
        """
        # Convert to DataFrame for size check
        df = self._prepare_data(
            data, 
            kwargs.get('date_column', 'date')
        )
        
        # Downsample if needed for performance
        if len(df) > 10000:
            # Calculate appropriate sample size
            sample_size = min(5000, len(df) // 2)
            step = len(df) // sample_size
            df = df.iloc[::step]
            logger.info(f"Downsampled from {len(data)} to {len(df)} points")
        
        # Call parent implementation with downsampled data
        return super().plot_time_series_with_correlation(df, **kwargs)


# Utility functions
def create_sample_time_series(
    n_points: int = 1000,
    n_series: int = 3,
    start_date: str = '2023-01-01',
    freq: str = 'D',
    noise_level: float = 0.1,
    correlation: float = 0.8
) -> pd.DataFrame:
    """Create sample time series data for testing.
    
    Args:
        n_points: Number of data points.
        n_series: Number of time series.
        start_date: Start date for series.
        freq: Frequency of dates.
        noise_level: Amount of noise to add.
        correlation: Desired correlation between series.
        
    Returns:
        DataFrame with sample time series.
    """
    dates = pd.date_range(start=start_date, periods=n_points, freq=freq)
    
    # Create base signal
    t = np.linspace(0, 4 * np.pi, n_points)
    base_signal = np.sin(t)
    
    data = {'date': dates}
    
    for i in range(n_series):
        # Add correlated noise
        noise = np.random.normal(0, noise_level, n_points)
        if i > 0:
            # Make series correlated
            signal = correlation * base_signal + (1 - correlation) * np.random.randn(n_points)
        else:
            signal = base_signal
        
        data[f'series_{i+1}'] = signal + noise
    
    return pd.DataFrame(data)
```