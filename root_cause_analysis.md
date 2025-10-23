
## Why This Keeps Happening

### What We HAVE Fixed:
```python
# build_feature.py and build_system.py now extract:
methods = extract_class_methods(layer_file)
# Returns: {"ClassName": ["method1", "method2"]}

config_fields = extract_config_fields(feature_file) 
# Returns: ["field1", "field2", "field3"]
```

### What Gets Sent to AI:
```
Layer 1 Methods:
  Class: DataReader
    - read_file
    - parse_yaml
  
CRITICAL: Only call these methods!

FeatureConfig Fields:
  - input_file
  - validate_schema
  
Generate feature_integration.py that uses these layers.
```

### What AI Does Wrong:

**Problem 1: Markdown Wrapping**
AI returns:
```python
import pandas
...
```
Instead of:
```
import pandas
...
```

**Problem 2: API Invention**
Even with methods listed, AI still invents:
- `response.status.is_success()` - doesn't exist
- `layer.validate_strict()` - method is `validate_data()`

**Problem 3: Incomplete Imports**
Uses `Tuple` but only imports `Dict, List, Optional`

**Problem 4: Lost Context**
Each regeneration:
- Forgets previous settings.yaml
- Generates new incompatible settings
- No memory of what worked before

## The Missing Piece

We extract APIs and put them in prompts, but:
- ❌ No validation that generated code USES extracted APIs
- ❌ No feedback loop when AI invents methods
- ❌ No syntax checking before saving
- ❌ No import analysis

**Example of what's needed:**
```python
# After AI generates code:
def validate_generated_code(generated_code, extracted_methods):
    # Parse the code
    tree = ast.parse(generated_code)
    
    # Find all method calls
    called_methods = find_all_calls(tree)
    
    # Check against extracted methods
    for call in called_methods:
        if call not in extracted_methods:
            return False, f"Invalid method: {call}"
    
    return True, "Valid"
```

We give AI the right information but don't verify it uses it!

