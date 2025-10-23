# Hybrid Template + AI Workflow Design

**Date**: October 21, 2025  
**Purpose**: Define granular workflow for intelligent code generation with template library  
**Problem Solved**: Current AI regenerates all layers if one fails; expensive and wasteful

---

## 🎯 CORE PROBLEM STATEMENT

### Current Workflow Issues

```text
CURRENT (PROJECT-004 Only):
┌─────────────────────────────────────────────┐
│ Feature: User Authentication (4 layers)     │
├─────────────────────────────────────────────┤
│ Layer 1: User Model         → AI ($2.80)   │
│ Layer 2: Auth Repository    → AI ($2.80)   │
│ Layer 3: Auth Service       → AI ($2.80)   │
│ Layer 4: Auth Controller    → AI ($2.80)   │
│                                             │
│ ❌ Layer 3 has bug (missing validation)    │
│                                             │
│ FIX ATTEMPT:                                │
│ Layer 1: User Model         → AI ($2.80) ← Regenerate
│ Layer 2: Auth Repository    → AI ($2.80) ← Regenerate
│ Layer 3: Auth Service       → AI ($2.80) ← Regenerate (fixed)
│ Layer 4: Auth Controller    → AI ($2.80) ← Regenerate
│                                             │
│ TOTAL COST: $22.40 (8 generations)         │
│ WASTE: $16.80 (6 unnecessary regenerations)│
└─────────────────────────────────────────────┘
```

**Problems**:
1. ❌ No granular control (all-or-nothing)
2. ❌ Can't resume from failure point
3. ❌ Regenerates working layers
4. ❌ No layer-level caching
5. ❌ Expensive iteration cycles

---

## 💡 PROPOSED SOLUTION: Hybrid Template + AI System

### Architecture Overview

```text
HYBRID SYSTEM:
┌──────────────────────────────────────────────────────────┐
│  INPUT: LAYER YAML Specification                         │
└──────────────────┬───────────────────────────────────────┘
                   ↓
┌──────────────────────────────────────────────────────────┐
│  PATTERN MATCHER                                         │
│  ├─ Analyze YAML structure                               │
│  ├─ Detect layer type                                    │
│  ├─ Check pattern library                                │
│  └─ Return: [exact|similar|none]                         │
└──────────────────┬───────────────────────────────────────┘
                   ↓
         ┌─────────┴─────────┐
         │                   │
    ✅ PATTERN            ❌ NO PATTERN
    MATCH FOUND           FOUND
         │                   │
         ↓                   ↓
┌─────────────────┐   ┌─────────────────┐
│ TEMPLATE GEN    │   │   AI GEN        │
│ Cost: $0        │   │   Cost: $2.80   │
│ Time: 5 sec     │   │   Time: 90 sec  │
└────────┬────────┘   └────────┬────────┘
         │                     │
         └──────────┬──────────┘
                    ↓
         ┌──────────────────────┐
         │  TDD VALIDATOR       │
         │  ├─ Tests exist?     │
         │  ├─ Coverage > 80%?  │
         │  ├─ Requirements OK? │
         │  └─ Return: pass|fail│
         └──────────┬───────────┘
                    ↓
              ┌─────┴─────┐
              │           │
           PASS         FAIL
              │           │
              ↓           ↓
         ✅ DONE    🔧 AUTO-FIX
                    (Targeted AI)
                    Cost: $0.50
                    Time: 20 sec
```

---

## 🔄 DETAILED WORKFLOW

### Phase 1: Feature Initialization

```python
# build_feature.py (enhanced)

class HybridFeatureBuilder:
    def __init__(self, feature_yaml):
        self.feature_yaml = feature_yaml
        self.pattern_lib = PatternLibrary()
        self.ai_generator = AICodeGenerator()
        self.validator = TDDValidator()
        
        # NEW: Layer state management
        self.layer_states = {}  # Track each layer independently
        self.build_cache = {}   # Cache successful generations
        
    def build_feature(self):
        """Build feature with granular control"""
        
        # Step 1: Load feature spec
        spec = self.load_feature_spec()
        
        # Step 2: Discover layers
        layers = self.discover_layers(spec)
        
        # Step 3: Build layers independently (NEW!)
        for layer in layers:
            self.build_single_layer(layer)
        
        # Step 4: Integrate layers
        self.generate_feature_integration()
```

---

### Phase 2: Single Layer Build

```python
def build_single_layer(self, layer_yaml):
    """
    Build single layer with template/AI decision.
    
    KEY FEATURE: Granular control - can rebuild just this layer
    """
    
    layer_id = layer_yaml['layer_id']
    
    # Check if already built and valid
    if self.is_layer_cached(layer_id):
        print(f"✅ Using cached: {layer_id}")
        return self.load_from_cache(layer_id)
    
    print(f"\n{'='*60}")
    print(f"🏗️  Building Layer: {layer_id}")
    print(f"{'='*60}")
    
    # DECISION POINT 1: Template or AI?
    generation_result = self.decide_generation_method(layer_yaml)
    
    if generation_result['method'] == 'template':
        print(f"📋 Using Template: {generation_result['template_name']}")
        code = self.generate_from_template(layer_yaml, generation_result)
        cost = 0
        
    elif generation_result['method'] == 'template_adapt':
        print(f"📝 Adapting Template: {generation_result['template_name']}")
        code = self.adapt_template_with_ai(layer_yaml, generation_result)
        cost = 0.50
        
    else:  # 'ai_full'
        print(f"🤖 AI Full Generation")
        code = self.generate_with_ai(layer_yaml)
        cost = 2.80
    
    # VALIDATION (always happens)
    print(f"🔍 Validating layer...")
    validation = self.validator.validate(code, layer_yaml)
    
    if validation['passed']:
        print(f"✅ Validation PASSED")
        self.cache_layer(layer_id, code, cost)
        return code
    
    else:
        print(f"⚠️  Validation FAILED: {validation['issues']}")
        
        # DECISION POINT 2: Auto-fix or manual?
        if self.can_auto_fix(validation['issues']):
            print(f"🔧 Attempting auto-fix...")
            code = self.auto_fix_issues(code, validation['issues'])
            cost += 0.30
            
            # Re-validate
            validation = self.validator.validate(code, layer_yaml)
            if validation['passed']:
                print(f"✅ Auto-fix successful")
                self.cache_layer(layer_id, code, cost)
                return code
        
        # Manual intervention needed
        print(f"❌ Manual fix required")
        self.save_failed_state(layer_id, code, validation)
        raise LayerBuildException(layer_id, validation['issues'])
```

---

### Phase 3: Template vs AI Decision Logic

```python
def decide_generation_method(self, layer_yaml):
    """
    Intelligent decision: template, adapt, or full AI?
    
    Returns decision with confidence score
    """
    
    layer_type = layer_yaml['layer_type']
    operations = layer_yaml.get('operations', [])
    complexity = self._calculate_complexity(layer_yaml)
    
    # RULE 1: Exact template match (100% confidence)
    exact_match = self.pattern_lib.find_exact_match(layer_yaml)
    if exact_match:
        return {
            'method': 'template',
            'template_name': exact_match['name'],
            'confidence': 1.0,
            'reason': 'Exact pattern match'
        }
    
    # RULE 2: Similar template (80%+ similarity)
    similar = self.pattern_lib.find_similar(layer_yaml, threshold=0.80)
    if similar:
        return {
            'method': 'template_adapt',
            'template_name': similar['name'],
            'confidence': similar['similarity'],
            'reason': f"{similar['similarity']:.0%} similar to known pattern"
        }
    
    # RULE 3: Standard patterns (CRUD, validators, etc.)
    if self._is_standard_pattern(layer_type, operations):
        template = self.pattern_lib.get_standard_template(layer_type)
        return {
            'method': 'template',
            'template_name': template['name'],
            'confidence': 0.90,
            'reason': 'Standard pattern detected'
        }
    
    # RULE 4: Low complexity + known structure
    if complexity < 3 and self._has_known_structure(layer_yaml):
        return {
            'method': 'template_adapt',
            'template_name': 'generic_' + layer_type,
            'confidence': 0.70,
            'reason': 'Low complexity, adaptable structure'
        }
    
    # RULE 5: Fallback to AI
    return {
        'method': 'ai_full',
        'template_name': None,
        'confidence': 0.0,
        'reason': f'Complex/novel pattern (complexity={complexity})'
    }
```

---

## 📚 TEMPLATE LIBRARY STRUCTURE

### Directory Layout

```text
pattern_library/
├── data_access/
│   ├── crud_repository.py.template
│   ├── read_only_repository.py.template
│   ├── cache_repository.py.template
│   └── aggregate_repository.py.template
│
├── business_logic/
│   ├── service_pattern.py.template
│   ├── validator_pattern.py.template
│   ├── calculator_pattern.py.template
│   └── state_machine_pattern.py.template
│
├── integration/
│   ├── rest_api_controller.py.template
│   ├── graphql_resolver.py.template
│   ├── api_client.py.template
│   └── event_handler.py.template
│
├── feature/
│   ├── feature_integration.py.template
│   ├── dto_model.py.template
│   └── error_handler.py.template
│
├── custom/                          ← YOUR DOMAIN-SPECIFIC
│   ├── aerospace/
│   │   ├── part_tracker.py.template
│   │   ├── quality_checker.py.template
│   │   └── compliance_validator.py.template
│   │
│   ├── health_fitness/
│   │   ├── nutrition_calculator.py.template
│   │   ├── workout_planner.py.template
│   │   └── progress_tracker.py.template
│   │
│   └── financial/
│       ├── transaction_processor.py.template
│       └── account_reconciler.py.template
│
└── meta/
    ├── pattern_matcher.py           ← Detects which template
    ├── template_adapter.py          ← Customizes template
    ├── template_validator.py        ← Ensures template quality
    └── template_learner.py          ← Learns new patterns
```

---

## 🎨 TEMPLATE ANATOMY

### Example: CRUD Repository Template

```python
# pattern_library/data_access/crud_repository.py.template
"""
CRUD Repository Pattern Template

This template generates 70% of typical data access layers.

TEMPLATE VARIABLES (required):
- {entity_name}: Name of entity (e.g., "User", "Product")
- {entity_name_lower}: Lowercase entity name
- {table_name}: Database table name
- {primary_key}: Primary key field name (default: "id")
- {fields}: List of field definitions

TEMPLATE VARIABLES (optional):
- {soft_delete}: Enable soft delete (default: false)
- {audit_fields}: Add created_at/updated_at (default: true)
- {cache_enabled}: Enable caching (default: false)

CONFIDENCE SCORE: 0.95 (highly reliable)
USAGE COUNT: 487 (proven pattern)
LAST_UPDATED: 2025-10-15
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class {entity_name}Repository:
    """
    Data access layer for {entity_name} entities.
    
    Implements standard CRUD operations with:
    - Input validation
    - Error handling
    - Logging
    {% if cache_enabled %}
    - Caching layer
    {% endif %}
    {% if soft_delete %}
    - Soft delete support
    {% endif %}
    """
    
    def __init__(self, db_connection):
        """Initialize repository with database connection"""
        self.db = db_connection
        self.table = "{table_name}"
        {% if cache_enabled %}
        self.cache = CacheManager(ttl=300)  # 5-minute cache
        {% endif %}
        logger.info(f"Initialized {entity_name}Repository")
    
    def create(self, {entity_name_lower}: Dict[str, Any]) -> str:
        """
        Create new {entity_name} entity.
        
        Args:
            {entity_name_lower}: Entity data dictionary
            
        Returns:
            str: Created entity ID
            
        Raises:
            ValidationError: If data validation fails
            DatabaseError: If database operation fails
        """
        logger.info(f"Creating {entity_name}")
        
        # Validate required fields
        self._validate_create_data({entity_name_lower})
        
        {% if audit_fields %}
        # Add audit fields
        {entity_name_lower}['created_at'] = datetime.utcnow()
        {entity_name_lower}['updated_at'] = datetime.utcnow()
        {% endif %}
        
        try:
            # Build INSERT query
            fields = ', '.join({entity_name_lower}.keys())
            placeholders = ', '.join(['?' for _ in {entity_name_lower}])
            query = f"INSERT INTO {self.table} ({fields}) VALUES ({placeholders})"
            
            # Execute
            cursor = self.db.execute(query, list({entity_name_lower}.values()))
            entity_id = cursor.lastrowid
            
            {% if cache_enabled %}
            # Cache result
            self.cache.invalidate(f"{self.table}:*")
            {% endif %}
            
            logger.info(f"Created {entity_name} with ID: {entity_id}")
            return str(entity_id)
            
        except Exception as e:
            logger.error(f"Failed to create {entity_name}: {e}")
            raise DatabaseError(f"Create operation failed: {e}")
    
    def read(self, {entity_name_lower}_id: str) -> Optional[Dict[str, Any]]:
        """
        Read {entity_name} by ID.
        
        Args:
            {entity_name_lower}_id: Entity ID
            
        Returns:
            Optional[Dict]: Entity data or None if not found
        """
        logger.debug(f"Reading {entity_name} ID: {{entity_name_lower}_id}")
        
        {% if cache_enabled %}
        # Check cache first
        cache_key = f"{self.table}:{{entity_name_lower}_id}"
        cached = self.cache.get(cache_key)
        if cached:
            logger.debug(f"Cache hit for {entity_name} {{entity_name_lower}_id}")
            return cached
        {% endif %}
        
        try:
            query = f"""
                SELECT * FROM {self.table} 
                WHERE {primary_key} = ?
                {% if soft_delete %}
                AND deleted_at IS NULL
                {% endif %}
            """
            
            result = self.db.fetchone(query, [{entity_name_lower}_id])
            
            {% if cache_enabled %}
            if result:
                self.cache.set(cache_key, result)
            {% endif %}
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to read {entity_name}: {e}")
            raise DatabaseError(f"Read operation failed: {e}")
    
    def update(self, {entity_name_lower}_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update {entity_name} entity.
        
        Args:
            {entity_name_lower}_id: Entity ID
            updates: Dictionary of fields to update
            
        Returns:
            bool: True if updated, False if not found
        """
        logger.info(f"Updating {entity_name} ID: {{entity_name_lower}_id}")
        
        # Validate update data
        self._validate_update_data(updates)
        
        {% if audit_fields %}
        # Update timestamp
        updates['updated_at'] = datetime.utcnow()
        {% endif %}
        
        try:
            # Build UPDATE query
            set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
            query = f"""
                UPDATE {self.table} 
                SET {set_clause}
                WHERE {primary_key} = ?
                {% if soft_delete %}
                AND deleted_at IS NULL
                {% endif %}
            """
            
            # Execute
            cursor = self.db.execute(
                query, 
                list(updates.values()) + [{entity_name_lower}_id]
            )
            
            {% if cache_enabled %}
            # Invalidate cache
            self.cache.invalidate(f"{self.table}:{{entity_name_lower}_id}")
            self.cache.invalidate(f"{self.table}:*")
            {% endif %}
            
            updated = cursor.rowcount > 0
            logger.info(f"Update result: {updated}")
            return updated
            
        except Exception as e:
            logger.error(f"Failed to update {entity_name}: {e}")
            raise DatabaseError(f"Update operation failed: {e}")
    
    def delete(self, {entity_name_lower}_id: str) -> bool:
        """
        Delete {entity_name} entity.
        
        Args:
            {entity_name_lower}_id: Entity ID
            
        Returns:
            bool: True if deleted, False if not found
        """
        logger.info(f"Deleting {entity_name} ID: {{entity_name_lower}_id}")
        
        try:
            {% if soft_delete %}
            # Soft delete
            query = f"""
                UPDATE {self.table} 
                SET deleted_at = ?
                WHERE {primary_key} = ?
                AND deleted_at IS NULL
            """
            cursor = self.db.execute(query, [datetime.utcnow(), {entity_name_lower}_id])
            {% else %}
            # Hard delete
            query = f"DELETE FROM {self.table} WHERE {primary_key} = ?"
            cursor = self.db.execute(query, [{entity_name_lower}_id])
            {% endif %}
            
            {% if cache_enabled %}
            # Invalidate cache
            self.cache.invalidate(f"{self.table}:{{entity_name_lower}_id}")
            self.cache.invalidate(f"{self.table}:*")
            {% endif %}
            
            deleted = cursor.rowcount > 0
            logger.info(f"Delete result: {deleted}")
            return deleted
            
        except Exception as e:
            logger.error(f"Failed to delete {entity_name}: {e}")
            raise DatabaseError(f"Delete operation failed: {e}")
    
    def list(self, 
             limit: int = 100, 
             offset: int = 0,
             filters: Optional[Dict[str, Any]] = None,
             order_by: str = "{primary_key}") -> List[Dict[str, Any]]:
        """
        List {entity_name} entities with pagination.
        
        Args:
            limit: Maximum results to return
            offset: Number of records to skip
            filters: Optional filter criteria
            order_by: Field to sort by
            
        Returns:
            List[Dict]: List of entity data dictionaries
        """
        logger.debug(f"Listing {entity_name} (limit={limit}, offset={offset})")
        
        try:
            # Build WHERE clause
            where_clauses = []
            params = []
            
            {% if soft_delete %}
            where_clauses.append("deleted_at IS NULL")
            {% endif %}
            
            if filters:
                for key, value in filters.items():
                    where_clauses.append(f"{key} = ?")
                    params.append(value)
            
            where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"
            
            # Build query
            query = f"""
                SELECT * FROM {self.table}
                WHERE {where_clause}
                ORDER BY {order_by}
                LIMIT ? OFFSET ?
            """
            params.extend([limit, offset])
            
            results = self.db.fetchall(query, params)
            logger.debug(f"Found {len(results)} {entity_name} records")
            return results
            
        except Exception as e:
            logger.error(f"Failed to list {entity_name}: {e}")
            raise DatabaseError(f"List operation failed: {e}")
    
    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count {entity_name} entities.
        
        Args:
            filters: Optional filter criteria
            
        Returns:
            int: Total count
        """
        try:
            where_clauses = []
            params = []
            
            {% if soft_delete %}
            where_clauses.append("deleted_at IS NULL")
            {% endif %}
            
            if filters:
                for key, value in filters.items():
                    where_clauses.append(f"{key} = ?")
                    params.append(value)
            
            where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"
            
            query = f"SELECT COUNT(*) as total FROM {self.table} WHERE {where_clause}"
            result = self.db.fetchone(query, params)
            return result['total'] if result else 0
            
        except Exception as e:
            logger.error(f"Failed to count {entity_name}: {e}")
            raise DatabaseError(f"Count operation failed: {e}")
    
    # ========================================================================
    # PRIVATE HELPER METHODS
    # ========================================================================
    
    def _validate_create_data(self, data: Dict[str, Any]) -> None:
        """Validate data for create operation"""
        required_fields = {{% for field in required_fields %}"{{field}}"{% if not loop.last %}, {% endif %}{% endfor %}}
        missing = required_fields - set(data.keys())
        if missing:
            raise ValidationError(f"Missing required fields: {missing}")
    
    def _validate_update_data(self, data: Dict[str, Any]) -> None:
        """Validate data for update operation"""
        if not data:
            raise ValidationError("No fields to update")
        
        # Prevent updating immutable fields
        immutable_fields = {"{primary_key}", {% if audit_fields %}"created_at"{% endif %}}
        invalid = immutable_fields & set(data.keys())
        if invalid:
            raise ValidationError(f"Cannot update immutable fields: {invalid}")


# Custom exceptions
class DatabaseError(Exception):
    """Database operation error"""
    pass


class ValidationError(Exception):
    """Data validation error"""
    pass


{% if cache_enabled %}
class CacheManager:
    """Simple in-memory cache manager"""
    
    def __init__(self, ttl: int = 300):
        self.cache = {}
        self.ttl = ttl
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached value"""
        if key in self.cache:
            entry = self.cache[key]
            if datetime.utcnow().timestamp() < entry['expires']:
                return entry['value']
            else:
                del self.cache[key]
        return None
    
    def set(self, key: str, value: Any) -> None:
        """Set cached value"""
        self.cache[key] = {
            'value': value,
            'expires': datetime.utcnow().timestamp() + self.ttl
        }
    
    def invalidate(self, pattern: str) -> None:
        """Invalidate cache entries matching pattern"""
        if pattern.endswith('*'):
            prefix = pattern[:-1]
            keys_to_delete = [k for k in self.cache if k.startswith(prefix)]
            for key in keys_to_delete:
                del self.cache[key]
        elif pattern in self.cache:
            del self.cache[pattern]
{% endif %}
```

---

## 🔧 TEMPLATE CUSTOMIZATION

### How to Use Template

```yaml
# LAYER-001-02-01_user_repository.yaml

layer_id: LAYER-001-02-01
layer_name: User Repository
layer_type: DATA_ACCESS
template_hint: crud_repository  # Optional: suggest template

# Template variables
template_variables:
  entity_name: User
  entity_name_lower: user
  table_name: users
  primary_key: id
  required_fields:
    - username
    - email
    - password_hash
  soft_delete: true
  audit_fields: true
  cache_enabled: true

# Standard layer spec
operations:
  - create
  - read
  - update
  - delete
  - list
  - count

acceptance_criteria:
  - User can be created with username, email, password
  - User can be retrieved by ID
  - User can be updated
  - User can be soft-deleted
  - Users can be listed with pagination
```

**Result**: Template generates complete repository in **5 seconds** for **$0**

---

### How to Adapt Template

```yaml
# LAYER-001-02-02_product_repository.yaml

layer_id: LAYER-001-02-02
layer_name: Product Repository
layer_type: DATA_ACCESS
template_hint: crud_repository

template_variables:
  entity_name: Product
  entity_name_lower: product
  table_name: products
  primary_key: product_id  # ← Different primary key
  required_fields:
    - name
    - sku
    - price
    - category_id
  soft_delete: false  # ← Hard delete
  audit_fields: true
  cache_enabled: true

# CUSTOM: Add product-specific methods
custom_operations:
  - search_by_sku
  - find_by_category
  - update_stock_quantity

acceptance_criteria:
  - Standard CRUD operations
  - Search products by SKU
  - Find all products in category
  - Update stock quantity atomically
```

**Process**:
1. Template generates base CRUD (5 sec, $0)
2. AI adds custom methods (20 sec, $0.50)
3. **Total**: 25 seconds, **$0.50** (vs $2.80 full AI)

---

## 🚨 FAILURE RECOVERY WORKFLOW

### Scenario: Layer 3 Fails

```text
PROBLEM: Building 4-layer feature, Layer 3 has validation error

OLD APPROACH (Wasteful):
┌─────────────────────────────────────────────┐
│ Feature Build Started                       │
├─────────────────────────────────────────────┤
│ Layer 1: ✅ Generated ($2.80)              │
│ Layer 2: ✅ Generated ($2.80)              │
│ Layer 3: ❌ FAILED - Missing validation    │
│ Layer 4: ⏭️  Skipped                       │
├─────────────────────────────────────────────┤
│ FIX: Regenerate ALL                         │
├─────────────────────────────────────────────┤
│ Layer 1: ✅ Regenerated ($2.80) ← Waste    │
│ Layer 2: ✅ Regenerated ($2.80) ← Waste    │
│ Layer 3: ✅ Fixed ($2.80)                  │
│ Layer 4: ✅ Generated ($2.80)              │
├─────────────────────────────────────────────┤
│ TOTAL: $22.40                               │
│ WASTE: $11.20 (Layers 1 & 2 regenerated)   │
└─────────────────────────────────────────────┘

NEW APPROACH (Efficient):
┌─────────────────────────────────────────────┐
│ Feature Build Started                       │
├─────────────────────────────────────────────┤
│ Layer 1: ✅ Template ($0) → Cached         │
│ Layer 2: ✅ Template ($0) → Cached         │
│ Layer 3: ❌ FAILED - Missing validation    │
│ Layer 4: ⏭️  Paused (dependency failed)    │
├─────────────────────────────────────────────┤
│ FIX: Targeted regeneration                  │
├─────────────────────────────────────────────┤
│ Layer 1: ✅ Load from cache ($0) ← Reuse   │
│ Layer 2: ✅ Load from cache ($0) ← Reuse   │
│ Layer 3: ✅ Auto-fix ($0.50) ← Targeted    │
│ Layer 4: ✅ Template ($0)                  │
├─────────────────────────────────────────────┤
│ TOTAL: $0.50                                │
│ SAVINGS: $21.90 (98% cost reduction!)      │
└─────────────────────────────────────────────┘
```

---

### Recovery Commands

```python
# Scenario 1: Auto-fix single layer
python build_feature.py \
  --feature FEATURE-001-02 \
  --rebuild-layer LAYER-001-02-03 \  # Only rebuild this layer
  --auto-fix                         # Attempt automated fix

# Output:
# ✅ Layer 1: Loaded from cache
# ✅ Layer 2: Loaded from cache
# 🔧 Layer 3: Auto-fixing validation issue...
#    - Added missing input validation
#    - Added error handling
#    - Cost: $0.30
# ✅ Layer 3: Fixed and validated
# ✅ Layer 4: Loaded from cache
# 
# Total cost: $0.30
# Time: 25 seconds


# Scenario 2: Manual fix + continue
python build_feature.py \
  --feature FEATURE-001-02 \
  --continue-from LAYER-001-02-03  # Resume from this layer
  --skip-validation                 # I fixed it manually

# Output:
# ✅ Layer 1: Using existing (validated)
# ✅ Layer 2: Using existing (validated)
# ⏭️  Layer 3: Using manual fix (validation skipped)
# 🏗️  Layer 4: Building...
# 
# Total cost: $0 (using manual fix)
# Time: 15 seconds


# Scenario 3: Force regenerate single layer
python build_feature.py \
  --feature FEATURE-001-02 \
  --force-rebuild LAYER-001-02-03 \  # Regenerate from scratch
  --method ai                         # Force AI (ignore templates)

# Output:
# ✅ Layer 1: Loaded from cache
# ✅ Layer 2: Loaded from cache
# 🤖 Layer 3: Full AI regeneration...
#    - Generated 250 lines
#    - Added 15 methods
#    - Cost: $2.80
# ✅ Layer 3: Validated
# ✅ Layer 4: Loaded from cache
# 
# Total cost: $2.80
# Time: 120 seconds
```

---

## 📝 TEMPLATE MANAGEMENT

### Creating Domain-Specific Templates

```python
# Step 1: Generate with AI (learn from AI output)
python build_feature.py \
  --feature FEATURE-AEROSPACE-001 \
  --learn-patterns  # Extract patterns from AI generation

# Output:
# 🤖 Generating with AI...
# ✅ Layer 1: Part Tracker Service generated
# 📚 Learning patterns...
#    - Detected: Tracking pattern (confidence: 0.92)
#    - Similar to: Generic service pattern
#    - Unique elements: Status transitions, audit trail
# 💾 Saved pattern: aerospace/part_tracker.py.template


# Step 2: Review and refine template
code templates/custom/aerospace/part_tracker.py.template

# Step 3: Test template
python test_template.py \
  --template aerospace/part_tracker \
  --test-cases 5

# Output:
# ✅ Test 1: Landing gear tracker - PASS
# ✅ Test 2: Engine component tracker - PASS
# ✅ Test 3: Avionics part tracker - PASS
# ✅ Test 4: Structural element tracker - PASS
# ✅ Test 5: Consumable tracker - PASS
# 
# Template quality score: 0.96
# Ready for production use: YES


# Step 4: Use your template
python build_feature.py \
  --feature FEATURE-AEROSPACE-002 \
  --prefer-templates custom/aerospace  # Use domain templates first

# Output:
# 🎯 Using custom template: aerospace/part_tracker
# ✅ Generated in 5 seconds
# ✅ Cost: $0
```

---

### Template Update Workflow

```python
# Scenario: Need to add security checks to all repositories

# Step 1: Update template
code templates/data_access/crud_repository.py.template
# Add security validation to all CRUD methods

# Step 2: Validate template changes
python validate_template.py \
  --template data_access/crud_repository \
  --check-breaking-changes

# Output:
# ⚠️  WARNING: Breaking changes detected:
#    - Added required parameter: security_context
#    - This will require YAML updates
# 
# Affected features: 24
# Recommend: Create v2 template, migrate gradually


# Step 3: Create versioned template
cp templates/data_access/crud_repository.py.template \
   templates/data_access/crud_repository_v2.py.template

# Edit crud_repository_v2.py.template with new security features

# Step 4: Migrate features gradually
python migrate_template.py \
  --feature FEATURE-001-02 \
  --from crud_repository \
  --to crud_repository_v2 \
  --dry-run  # Test migration first

# Output:
# 🔍 Analyzing FEATURE-001-02...
# 
# Changes required:
# ├─ LAYER-001-02-01: Add security_context parameter
# ├─ LAYER-001-02-02: Add security_context parameter
# └─ LAYER-001-02-03: Update tests for security
# 
# Estimated cost: $0 (template adaptation)
# Estimated time: 15 seconds
# 
# Run without --dry-run to apply changes


# Step 5: Apply migration
python migrate_template.py \
  --feature FEATURE-001-02 \
  --from crud_repository \
  --to crud_repository_v2

# Output:
# ✅ Migrated LAYER-001-02-01
# ✅ Migrated LAYER-001-02-02
# ✅ Updated tests
# ✅ Validation passed
# 
# Migration complete: FEATURE-001-02
# Cost: $0
# Time: 18 seconds
```

---

## 🎯 SEGMENTATION: Template vs AI

### Decision Matrix

```text
┌──────────────────────────────────────────────────────────────────┐
│ WHEN TO USE TEMPLATES (70% of layers)                           │
├──────────────────────────────────────────────────────────────────┤
│ ✅ CRUD operations (data access)                                 │
│ ✅ Standard REST endpoints (integration)                         │
│ ✅ Simple validators (business logic)                            │
│ ✅ DTOs / Models (feature)                                       │
│ ✅ Known domain patterns (custom)                                │
│ ✅ Repetitive structures                                         │
│ ✅ Low complexity (< 3/10)                                       │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ WHEN TO ADAPT TEMPLATES (20% of layers)                         │
├──────────────────────────────────────────────────────────────────┤
│ 🔧 Standard pattern + custom methods                             │
│ 🔧 Similar to known pattern (70-90% match)                       │
│ 🔧 Template exists but needs 2-3 modifications                   │
│ 🔧 Medium complexity (3-6/10)                                    │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ WHEN TO USE FULL AI (10% of layers)                             │
├──────────────────────────────────────────────────────────────────┤
│ 🤖 Complex algorithms                                             │
│ 🤖 Novel business logic                                           │
│ 🤖 No similar template exists                                     │
│ 🤖 Integration with uncommon APIs                                 │
│ 🤖 Advanced state machines                                        │
│ 🤖 Complex validation rules                                       │
│ 🤖 High complexity (7-10/10)                                     │
└──────────────────────────────────────────────────────────────────┘
```

---

### Real Example: ZnNi Industrialization Project

```text
PROJECT-002 INDUSTRIALIZATION ANALYSIS:

FEATURE-002-001: File Monitor System
├─ LAYER-002-001-001: File Detector
│  Decision: 🤖 AI (no template for file monitoring)
│  Cost: $2.80
│  Reason: Novel pattern, complex regex parsing
│
├─ LAYER-002-001-002: File Parser
│  Decision: 🔧 Adapt Template (parser_pattern)
│  Cost: $0.50
│  Reason: Standard parser + custom filename format
│
└─ LAYER-002-001-003: File Validator
   Decision: ✅ Template (validator_pattern)
   Cost: $0
   Reason: Standard validation pattern

FEATURE-002-002: Excel Data Manager
├─ LAYER-002-002-001: Excel Reader
│  Decision: ✅ Template (excel_reader_pattern)
│  Cost: $0
│  Reason: Standard openpyxl operations
│
├─ LAYER-002-002-002: Data Transformer
│  Decision: 🔧 Adapt Template (data_transformer_pattern)
│  Cost: $0.50
│  Reason: Standard ETL + custom mapping rules
│
└─ LAYER-002-002-003: Excel Writer
   Decision: ✅ Template (excel_writer_pattern)
   Cost: $0
   Reason: Standard openpyxl operations

FEATURE-002-003: Status Tracker
├─ LAYER-002-003-001: Status Calculator
│  Decision: 🤖 AI (complex business rules)
│  Cost: $2.80
│  Reason: 23 stages, complex state transitions
│
├─ LAYER-002-003-002: Status Repository
│  Decision: ✅ Template (crud_repository)
│  Cost: $0
│  Reason: Standard database CRUD
│
└─ LAYER-002-003-003: Status Validator
   Decision: ✅ Template (validator_pattern)
   Cost: $0
   Reason: Standard validation checks

TOTAL COST:
- AI layers: 2 × $2.80 = $5.60
- Adapted: 2 × $0.50 = $1.00
- Templates: 5 × $0 = $0.00
- TOTAL: $6.60

OLD COST (All AI): 9 × $2.80 = $25.20
SAVINGS: $18.60 (74% reduction!)
```

---

## 🔄 COMPLETE WORKFLOW DIAGRAM

```text
┌──────────────────────────────────────────────────────────────────┐
│ START: python build_feature.py --feature FEATURE-001-02         │
└────────────────────────┬─────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────────────┐
│ STEP 1: Load Feature Specification                              │
│ ├─ Read FEATURE-001-02.yaml                                     │
│ ├─ Discover child LAYER YAMLs                                   │
│ ├─ Check build cache for existing layers                        │
│ └─ Create build plan                                            │
└────────────────────────┬─────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────────────┐
│ STEP 2: For Each Layer (Independent Build)                      │
└────────────────────────┬─────────────────────────────────────────┘
                         ↓
        ┌────────────────┴────────────────┐
        │ 2a. Check Cache                  │
        │ - Is layer already built?        │
        │ - Is cache valid?                │
        └────────┬────────────────┬────────┘
                 ↓                ↓
            CACHE HIT        CACHE MISS
                 │                │
                 │                ↓
                 │   ┌────────────────────────┐
                 │   │ 2b. Pattern Matching   │
                 │   │ - Analyze YAML         │
                 │   │ - Check template lib   │
                 │   │ - Calculate confidence │
                 │   └──────┬─────────────────┘
                 │          ↓
                 │   ┌──────┴───────┬──────────────┬─────────────┐
                 │   │              │              │             │
                 │ EXACT       SIMILAR        NONE            
                 │ MATCH       (>80%)         FOUND
                 │   │              │              │
                 │   ↓              ↓              ↓
                 │ ┌──────┐    ┌──────────┐   ┌────────────┐
                 │ │TEMPL │    │ADAPT AI  │   │ FULL AI    │
                 │ │$0    │    │$0.50     │   │ $2.80      │
                 │ │5 sec │    │25 sec    │   │ 90 sec     │
                 │ └──┬───┘    └────┬─────┘   └──────┬─────┘
                 │    │             │                 │
                 └────┴─────────────┴─────────────────┘
                                    ↓
                        ┌───────────────────────┐
                        │ 2c. Generate Code     │
                        │ - Apply template OR   │
                        │ - Call AI provider    │
                        │ - Generate files      │
                        └───────────┬───────────┘
                                    ↓
                        ┌───────────────────────┐
                        │ 2d. TDD Validation    │
                        │ ✓ Tests exist?        │
                        │ ✓ Coverage > 80%?     │
                        │ ✓ Requirements met?   │
                        │ ✓ Naming correct?     │
                        └─────┬────────┬────────┘
                              ↓        ↓
                          PASS      FAIL
                              │        │
                              │        ↓
                              │ ┌──────────────────┐
                              │ │ 2e. Auto-Fix?    │
                              │ │ - Can fix?       │
                              │ └─────┬──────┬─────┘
                              │       ↓      ↓
                              │     YES    NO
                              │       │      │
                              │       ↓      ↓
                              │  ┌────────┐ ┌──────────────┐
                              │  │Fix     │ │Manual Fix    │
                              │  │$0.30   │ │Required      │
                              │  └───┬────┘ │Save state    │
                              │      │      │Exit with code│
                              │      ↓      └──────────────┘
                              └──────┴──────────┐
                                                 ↓
                                    ┌────────────────────────┐
                                    │ 2f. Cache Layer        │
                                    │ - Store generated code │
                                    │ - Store metadata       │
                                    │ - Store validation     │
                                    └────────────┬───────────┘
                                                 ↓
                        ┌────────────────────────────────────────┐
                        │ STEP 3: Repeat for All Layers         │
                        │ (Layers build independently)           │
                        └────────────────────┬───────────────────┘
                                             ↓
                                ┌────────────────────────┐
                                │ STEP 4: Integration    │
                                │ - Generate feature_    │
                                │   integration.py       │
                                │ - Wire all layers      │
                                │ - Create tests         │
                                └───────────┬────────────┘
                                            ↓
                                ┌────────────────────────┐
                                │ STEP 5: Final Report   │
                                │ - Cost breakdown       │
                                │ - Time breakdown       │
                                │ - Validation summary   │
                                │ - Next steps           │
                                └────────────────────────┘
```

---

## 📊 COST & TIME COMPARISON

### Scenario: 20-Layer Enterprise Feature

```text
┌──────────────────────────────────────────────────────────────────┐
│ CURRENT APPROACH (PROJECT-004 AI Only)                          │
├──────────────────────────────────────────────────────────────────┤
│ Method: AI generates every layer                                │
│                                                                  │
│ Build 1 (Initial):                                              │
│   20 layers × $2.80 = $56.00                                    │
│   Time: 20 × 90sec = 30 minutes                                 │
│                                                                  │
│ Build 2 (Fix Layer 15):                                         │
│   20 layers × $2.80 = $56.00  ← Everything regenerated          │
│   Time: 30 minutes            ← Everything rebuilt              │
│                                                                  │
│ Build 3 (Fix Layer 8):                                          │
│   20 layers × $2.80 = $56.00  ← Everything regenerated          │
│   Time: 30 minutes            ← Everything rebuilt              │
│                                                                  │
│ TOTAL: $168.00                                                   │
│ TOTAL TIME: 90 minutes                                           │
│ WASTE: $112.00 (67%)                                            │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ HYBRID APPROACH (Templates + Selective AI)                      │
├──────────────────────────────────────────────────────────────────┤
│ Method: Templates for standard, AI for complex                  │
│                                                                  │
│ Build 1 (Initial):                                              │
│   14 template layers × $0 = $0                                  │
│   4 adapted layers × $0.50 = $2.00                              │
│   2 AI layers × $2.80 = $5.60                                   │
│   Total: $7.60                                                   │
│   Time: (14×5s) + (4×25s) + (2×90s) = 350s = 6 minutes         │
│                                                                  │
│ Build 2 (Fix Layer 15 - template layer):                        │
│   19 cached layers × $0 = $0                                    │
│   1 auto-fix × $0.30 = $0.30                                    │
│   Total: $0.30                                                   │
│   Time: 25 seconds                                               │
│                                                                  │
│ Build 3 (Fix Layer 8 - AI layer):                               │
│   19 cached layers × $0 = $0                                    │
│   1 AI regenerate × $2.80 = $2.80                               │
│   Total: $2.80                                                   │
│   Time: 95 seconds                                               │
│                                                                  │
│ TOTAL: $10.70                                                    │
│ TOTAL TIME: 8 minutes                                            │
│ SAVINGS: $157.30 (94% cost reduction!)                          │
│ TIME SAVINGS: 82 minutes (91% faster!)                          │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🚀 IMPLEMENTATION ROADMAP

### Week 1-2: Core Infrastructure

```bash
# Task 1: Layer state management
touch build_feature_v2.py
# Add:
# - Layer cache system
# - Independent layer builds
# - Failure recovery
# - Build state persistence

# Task 2: Pattern matcher
touch pattern_library/meta/pattern_matcher.py
# Add:
# - YAML analysis
# - Template similarity scoring
# - Confidence calculation
# - Decision logic

# Task 3: Template adapter
touch pattern_library/meta/template_adapter.py
# Add:
# - Variable substitution
# - Jinja2 template rendering
# - Custom method injection
# - Validation

# Test
python build_feature_v2.py \
  --feature FEATURE-TEST-001 \
  --mode template-only  # Test template generation
```

### Week 3-4: Template Library

```bash
# Build 10 core templates
mkdir -p pattern_library/{data_access,business_logic,integration,feature}

# Data access
touch pattern_library/data_access/crud_repository.py.template
touch pattern_library/data_access/read_only_repository.py.template

# Business logic
touch pattern_library/business_logic/service_pattern.py.template
touch pattern_library/business_logic/validator_pattern.py.template

# Integration
touch pattern_library/integration/rest_controller.py.template
touch pattern_library/integration/api_client.py.template

# Test each template
python test_template.py --template data_access/crud_repository --test-cases 10
```

### Week 5-6: Integration & Testing

```bash
# Integrate with existing build_feature.py
# Add backward compatibility
# Test on existing features
python build_feature_v2.py --feature FEATURE-003-03-03 --validate
```

### Week 7-8: Domain Templates

```bash
# Create domain-specific templates for your use cases
mkdir -p pattern_library/custom/{aerospace,health_fitness,financial}

# Aerospace templates (for ZnNi project)
touch pattern_library/custom/aerospace/part_tracker.py.template
touch pattern_library/custom/aerospace/quality_checker.py.template
touch pattern_library/custom/aerospace/compliance_validator.py.template

# Test on PROJECT-002
python build_feature_v2.py \
  --feature FEATURE-002-001 \
  --prefer-templates custom/aerospace
```

---

## 📋 SUMMARY: Key Benefits

### 1. **Granular Control**
- ✅ Build/rebuild individual layers
- ✅ Resume from failure point
- ✅ No unnecessary regeneration

### 2. **Cost Optimization**
- ✅ 70-90% cost reduction
- ✅ Templates free ($0)
- ✅ AI only when needed

### 3. **Failure Recovery**
- ✅ Auto-fix minor issues ($0.30)
- ✅ Targeted regeneration
- ✅ Cache working layers

### 4. **Template Management**
- ✅ Learn from AI patterns
- ✅ Domain-specific templates
- ✅ Version control templates

### 5. **Speed**
- ✅ 5 seconds (template)
- ✅ 25 seconds (adapt)
- ✅ 90 seconds (AI when needed)

---

**Next Step**: Start with pattern library foundation?
