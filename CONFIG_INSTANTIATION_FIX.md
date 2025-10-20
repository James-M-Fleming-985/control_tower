# Config Instantiation & Architecture-Specific Fixes

**Date**: October 20, 2025  
**Scope**: CLI Desktop Applications only  
**Status**: Backward compatible with all existing projects

## Root Cause Analysis

### The Config Instantiation Problem

**Symptom**:
```python
AttributeError: 'dict' object has no attribute 'log_level'
```

**Why it happens**:

1. **Feature implementations use @dataclass**:
```python
@dataclass
class FeatureConfig:
    log_level: str = "INFO"
    enable_caching: bool = True
```

2. **System integration passes raw dict**:
```python
config_dict = {'log_level': 'DEBUG', 'enable_caching': False}
orchestrator = FeatureOrchestrator(config_dict)  # ❌ Wrong!
```

3. **FeatureOrchestrator expects dataclass instance**:
```python
def __init__(self, config: FeatureConfig):
    self.config = config
    log_level = self.config.log_level  # ❌ Fails if config is dict!
```

### Why FastAPI Projects Don't Have This Issue

FastAPI projects use **Pydantic BaseSettings** which auto-convert from dicts:

```python
from pydantic import BaseSettings

class AppConfig(BaseSettings):
    log_level: str = "INFO"
    
config = AppConfig(**dict_from_yaml)  # Pydantic handles conversion
```

But **dataclasses don't auto-convert** - they need explicit instantiation:

```python
from dataclasses import dataclass

@dataclass
class FeatureConfig:
    log_level: str = "INFO"

# Must unpack dict:
config = FeatureConfig(**dict_from_yaml)
```

## Solution: Architecture-Specific Config Patterns

### CLI Desktop Architecture Only

Added config instantiation example to `DesktopCLIArchitecture.build_prompt()`:

```python
def load_feature_orchestrator(feature_folder_name):
    # Load the feature module
    path = Path(__file__).parent / feature_folder_name / "src" / "feature_integration.py"
    spec = importlib.util.spec_from_file_location(f"{feature_folder_name}.integration", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# When loading features with config:
for feature_key, folder_name in FEATURE_FOLDERS.items():
    module = load_feature_orchestrator(folder_name)
    feature_config_dict = config.get(feature_key, {})
    
    # FeatureConfig is a @dataclass - instantiate with **kwargs
    if feature_config_dict and hasattr(module, 'FeatureConfig'):
        feature_config = module.FeatureConfig(**feature_config_dict)
        orchestrator = module.FeatureOrchestrator(feature_config)
    else:
        orchestrator = module.FeatureOrchestrator()
```

**Key points**:
1. Load the entire module (not just FeatureOrchestrator class)
2. Check if FeatureConfig exists
3. Instantiate with `**kwargs` unpacking
4. Falls back to default config if no config dict

### FastAPI Architecture (No Changes Needed)

FastAPI projects don't need this pattern because:
- They use Pydantic models (auto-convert from dicts)
- Features are typically called via REST endpoints (no direct instantiation)
- Configuration handled through environment variables and BaseSettings

## Impact on Existing Projects

| Project | Type | Status | Change Needed? |
|---------|------|--------|----------------|
| SYSTEM-001 FitTrack Calculator | FastAPI (Railway) | ✅ Working | No |
| SYSTEM-002 FitTrack Frontend | Web App (SSR) | ✅ Working | No |
| SYSTEM-003 Report Generator | CLI Desktop | ❌ Config Error | Yes - Regenerate |

## Files Modified

### `/workspaces/control_tower/build_system.py`

**Lines 145-150**: Added folder names to feature list
```python
for f in spec.features:
    folder_name = f.feature_dir.name
    feature_list.append(f"- {f.feature_id}: {f.feature_name}")
    feature_list.append(f"  Folder: {folder_name}")  # NEW
```

**Lines 197-218**: Added config instantiation pattern (CLI only)
```python
Example import and instantiation pattern:
[... code example showing **kwargs unpacking ...]
```

**Lines 250-254**: Architecture selection logic (unchanged)
```python
def select_architecture(deployment_model: str, ...):
    if 'CLI' in deployment_model or 'Desktop Application' in deployment_model:
        return DesktopCLIArchitecture(...)  # Uses new pattern
    else:
        return FastAPIArchitecture(...)     # No changes
```

## Backward Compatibility Guarantee

✅ **FastAPI projects**: No prompt changes affecting generated code  
✅ **Web App projects**: No prompt changes affecting generated code  
✅ **CLI projects**: New architecture, new pattern (no existing projects to break)  
✅ **Architecture isolation**: Each strategy has independent prompt generation

## Testing Checklist

- [ ] Rebuild SYSTEM-003 with new CLI pattern
- [ ] Verify config instantiation works for all 6 features
- [ ] Test end-to-end PowerPoint generation
- [ ] Verify SYSTEM-001 (FastAPI) still works unchanged
- [ ] Verify SYSTEM-002 (Web App) still works unchanged

## Best Practices for Future

### When to Use Dataclasses vs Pydantic

**Use Pydantic BaseModel when**:
- Building FastAPI applications
- Need data validation and conversion
- Working with external data (JSON, env vars)

**Use @dataclass when**:
- Simple configuration objects
- Internal data structures
- Type hints are enough (no validation needed)

**System Integration Pattern**:
- Always unpack dicts when instantiating dataclasses: `Config(**dict)`
- Check if config class exists: `hasattr(module, 'FeatureConfig')`
- Provide fallback to default: `orchestrator()` if no config

## Related Fixes

This fix is part of the broader **Method Signature & Config Fix** initiative:

1. ✅ Method signature extraction (build_feature.py)
2. ✅ Enhanced AI prompts with actual methods
3. ✅ Folder name in system prompts
4. ✅ Config instantiation pattern (this document)

See [`METHOD_SIGNATURE_FIX_SUMMARY.md`](METHOD_SIGNATURE_FIX_SUMMARY.md) for complete context.
