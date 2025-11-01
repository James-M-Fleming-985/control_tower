# Correlation Analysis

Advanced correlation calculator supporting multiple methods with concurrent processing

Generated from template: `tpl-correlation-analysis` v2.0.0

## Overview

This module provides a comprehensive correlation analysis engine with:

- **Pearson Correlation**: Pearson product-moment correlation coefficient
- **Spearman Correlation**: Spearman rank correlation coefficient
- **Kendall Correlation**: Kendall tau rank correlation coefficient
- **Partial Correlation**: Partial correlation controlling for other variables
- **Lagged Correlation**: Lagged correlation for time series
- **Concurrent Processing**: Parallel computation for large datasets
- **Missing Data Handling**: Multiple strategies (interpolate, drop, fill)
- **Feature Orchestrator Integration**: Seamless integration with orchestrator patterns
- **Comprehensive Testing**: Full test coverage with benchmarks

## Quick Start

### Basic Usage

```python
from correlation_engine import CorrelationCalculator, CorrelationConfig
import numpy as np

# Create sample data
data = np.random.randn(1000, 10)

# Initialize calculator with default configuration
calculator = CorrelationCalculator()

# Calculate correlations
result = calculator.calculate(data)

print(f"Processing time: {result['metadata']['processing_time']:.3f}s")
print(f"Data shape: {result['metadata']['shape']}")
print(f"Method used: {result['config']['method']}")
```

### Advanced Configuration

```python
# Custom configuration
config = CorrelationConfig(
    method='pearson',
    missing_data_strategy='interpolate',
    concurrent=true,
    normalize=true,
    max_workers=4,
    chunk_size=1000
)

calculator = CorrelationCalculator(config)
result = calculator.calculate(data)
```

### Feature Orchestrator Integration

```python
# Register with feature orchestrator
orchestrator = YourFeatureOrchestrator()
calculator.register_with_orchestrator(orchestrator)

# Calculator is now registered as 'correlation_analysis'
result = calculator.calculate(data)
```

## Configuration Options

The `CorrelationConfig` class supports the following parameters:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `method` | str | `'pearson'` | Correlation calculation method |
| `missing_data_strategy` | str | `'interpolate'` | How to handle missing data |
| `fill_value` | float | `0.0` | Value for 'fill' strategy |
| `normalize` | bool | `true` | Whether to normalize results |
| `concurrent` | bool | `true` | Enable concurrent processing |
| `max_workers` | int/None | `4` | Number of worker threads |
| `chunk_size` | int | `1000` | Data chunk size for processing |
| `timeout` | int | `300` | Processing timeout in seconds |

## Supported Methods

### Pearson Correlation

Pearson product-moment correlation coefficient

```python
config = CorrelationConfig(method='pearson')
calculator = CorrelationCalculator(config)
result = calculator.calculate(data)
```

### Spearman Correlation

Spearman rank correlation coefficient

```python
config = CorrelationConfig(method='spearman')
calculator = CorrelationCalculator(config)
result = calculator.calculate(data)
```

### Kendall Correlation

Kendall tau rank correlation coefficient

```python
config = CorrelationConfig(method='kendall')
calculator = CorrelationCalculator(config)
result = calculator.calculate(data)
```

### Partial Correlation

Partial correlation controlling for other variables

```python
config = CorrelationConfig(method='partial')
calculator = CorrelationCalculator(config)
result = calculator.calculate(data)
```
**Parameters:**
- `control_variables`: []

### Lagged Correlation

Lagged correlation for time series

```python
config = CorrelationConfig(method='lagged')
calculator = CorrelationCalculator(config)
result = calculator.calculate(data)
```
**Parameters:**
- `max_lag`: 10


## Missing Data Strategies

### Interpolate (Default)
Linear interpolation fills missing values based on surrounding data points.

```python
config = CorrelationConfig(missing_data_strategy='interpolate')
```

### Drop
Removes rows containing any missing values.

```python
config = CorrelationConfig(missing_data_strategy='drop')
```

### Fill
Replaces missing values with a constant.

```python
config = CorrelationConfig(
    missing_data_strategy='fill',
    fill_value=0.0
)
```

## Performance

The calculator includes several performance optimizations:

- **Concurrent Processing**: Automatically enabled for datasets > 1000 elements
- **Chunked Processing**: Data split into 1000-element chunks
- **Memory Efficient**: Streaming processing for large datasets
- **Timeout Protection**: 300s timeout prevents hanging

### Benchmarks

Typical performance on modern hardware:

| Data Size | Method | Processing Time | Memory Usage |
|-----------|--------|-----------------|--------------|
| 1K x 10 | pearson | ~0.01s | ~1MB |
| 10K x 50 | pearson | ~0.1s | ~10MB |
| 100K x 100 | pearson | ~2s | ~100MB |

With concurrent processing enabled, performance scales with available CPU cores.

## Error Handling

The calculator includes comprehensive error handling:

- **Type Validation**: Input data type checking
- **Shape Validation**: Ensures compatible data dimensions
- **Timeout Protection**: Prevents infinite processing
- **Graceful Degradation**: Falls back to simpler methods on errors

```python
try:
    result = calculator.calculate(problematic_data)
except TypeError as e:
    print(f"Data type error: {e}")
except ValueError as e:
    print(f"Data value error: {e}")
except Exception as e:
    print(f"Calculation error: {e}")
```

## Testing

Run the comprehensive test suite:

```bash
pytest tests/test_correlation_engine.py -v
```

The test suite includes:
- Unit tests for all methods
- Integration tests
- Performance benchmarks
- Error handling validation
- Concurrent processing tests

## Dependencies

Required packages:
- `numpy`
- `scipy`
- `pandas`
- `concurrent.futures`

Install dependencies:

```bash
pip install numpy \pip install scipy \pip install pandas \pip install concurrent.futures```

## Integration Examples

### With Pandas DataFrames

```python
import pandas as pd

# Load data
df = pd.read_csv('financial_data.csv')

# Calculate correlations
calculator = CorrelationCalculator()
result = calculator.calculate(df)

# Convert back to DataFrame for analysis
correlation_matrix = pd.DataFrame(
    result['data'], 
    index=df.columns, 
    columns=df.columns
)
```

### With Time Series Data

```python
# Time series correlation with lag analysis
config = CorrelationConfig(method='lagged')
calculator = CorrelationCalculator(config)

# Calculate lagged correlations
result = calculator.calculate(time_series_data)
```

### Batch Processing

```python
# Process multiple datasets
datasets = [data1, data2, data3]
results = []

calculator = CorrelationCalculator()
for i, dataset in enumerate(datasets):
    result = calculator.calculate(dataset)
    result['dataset_id'] = i
    results.append(result)
```

## API Reference

### CorrelationCalculator

Main correlation calculation engine.

#### Methods

- `__init__(config: Optional[CorrelationConfig] = None)`: Initialize calculator
- `calculate(data: Union[np.ndarray, pd.DataFrame, List, Dict], **kwargs) -> Dict[str, Any]`: Main calculation method
- `set_feature_orchestrator(orchestrator: Any) -> None`: Set orchestrator integration
- `register_with_orchestrator(orchestrator: Any) -> None`: Register with orchestrator

### CorrelationConfig

Configuration dataclass for correlation calculations.

#### Attributes

All configuration parameters as listed in the configuration table above.

## License

Generated code follows your project's licensing terms.

---

*Template: tpl-correlation-analysis v2.0.0*  
*Generated: 2025-10-31T11:04:13.121698*