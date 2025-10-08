# Implementation Guide - PROJECT-004 AI Code Generator

## Day-by-Day Implementation Plan

### Day 1: Foundation Layer (8 hours)

#### Morning Session (4 hours): LAYER-004-01-01-01 - AI Provider Abstraction

**Step 1: Set up environment** (30 minutes)
```bash
cd "projects/PROJECT-004 AI CODE GENERATOR/SYSTEM-004-01 AI CODE GENERATION SYSTEM"
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Step 2: Copy execute_layer.py** (15 minutes)
```bash
cp "../../../PROJECT-003 TDD ENFORCER/SYSTEM-003-03 WORKFLOW ORCHESTRATION SYSTEM/scripts/execute_layer.py" scripts/
```

**Step 3: RED Phase - Generate Tests** (45 minutes)
```bash
python scripts/execute_layer.py --layer LAYER-004-01-01-01 --phase red
```

This generates:
- `tests/layer/ai_provider_abstraction/test_ai_provider_abstraction_unit.py`
- `tests/layer/ai_provider_abstraction/test_ai_provider_abstraction_integration.py`

Expected: All tests FAIL (no implementation yet)

**Step 4: GREEN Phase - Implement** (2 hours)

Create these files:

1. `src/ai_provider/__init__.py`
```python
from .interface import AIProviderInterface
from .openai_provider import OpenAIProvider
from .anthropic_provider import AnthropicProvider
from .factory import AIProviderFactory

__all__ = [
    'AIProviderInterface',
    'OpenAIProvider',
    'AnthropicProvider',
    'AIProviderFactory'
]
```

2. `src/ai_provider/interface.py`
```python
from abc import ABC, abstractmethod

class AIProviderInterface(ABC):
    """Abstract interface for AI code generation providers"""
    
    @abstractmethod
    def generate_code(self, prompt: str) -> str:
        """Generate code from prompt
        
        Args:
            prompt: Formatted prompt for code generation
            
        Returns:
            Generated code as string
        """
        pass
```

3. `src/ai_provider/openai_provider.py`
```python
import openai
from typing import Optional
from .interface import AIProviderInterface

class OpenAIProvider(AIProviderInterface):
    """OpenAI GPT-4 provider for code generation"""
    
    def __init__(self, api_key: str, model: str = "gpt-4-turbo-preview"):
        self.api_key = api_key
        self.model = model
        openai.api_key = api_key
    
    def generate_code(self, prompt: str) -> str:
        """Generate code using OpenAI GPT-4"""
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a Python code generator."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=4000
        )
        return response.choices[0].message.content
```

4. `src/ai_provider/anthropic_provider.py` (similar pattern)

5. `src/ai_provider/factory.py`
```python
from .interface import AIProviderInterface
from .openai_provider import OpenAIProvider
from .anthropic_provider import AnthropicProvider

class AIProviderFactory:
    """Factory for creating AI provider instances"""
    
    @staticmethod
    def create(provider: str, api_key: str) -> AIProviderInterface:
        if provider == "openai":
            return OpenAIProvider(api_key)
        elif provider == "anthropic":
            return AnthropicProvider(api_key)
        else:
            raise ValueError(f"Unknown provider: {provider}")
```

**Step 5: Run GREEN Phase** (15 minutes)
```bash
python scripts/execute_layer.py --layer LAYER-004-01-01-01 --phase green
```

Expected: All tests PASS, coverage >= 95%

**Step 6: REFACTOR Phase** (30 minutes)
```bash
python scripts/execute_layer.py --layer LAYER-004-01-01-01 --phase refactor
```

Refactor:
- Add better error messages
- Improve docstrings
- Add type hints
- Run black formatter

#### Afternoon Session (4 hours): LAYER-004-01-01-02 - Error Handling

**Step 1: RED Phase** (30 minutes)
```bash
python scripts/execute_layer.py --layer LAYER-004-01-01-02 --phase red
```

**Step 2: GREEN Phase** (2.5 hours)

Create:

1. `src/ai_provider/error_handling.py`
```python
from tenacity import retry, stop_after_attempt, wait_exponential

class RetryManager:
    """Manages retry logic with exponential backoff"""
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def call_with_retry(self, func, *args, **kwargs):
        """Call function with retry logic"""
        return func(*args, **kwargs)

class ErrorHandler:
    """Handles AI API errors gracefully"""
    
    def handle_timeout(self, error):
        # Implementation
        pass
    
    def handle_rate_limit(self, error):
        # Implementation
        pass
```

**Step 3: GREEN & REFACTOR** (1 hour)
```bash
python scripts/execute_layer.py --layer LAYER-004-01-01-02 --phase green
python scripts/execute_layer.py --layer LAYER-004-01-01-02 --phase refactor
```

---

### Day 2-3: Core Code Generation (16 hours)

#### LAYER-004-01-02-01: Test Code Generator

**Key Implementation:**

`src/code_generation/test_generator.py`
```python
import yaml
from jinja2 import Template
from typing import Dict, List

class TestCodeGenerator:
    """Generates pytest tests from YAML acceptance criteria"""
    
    def __init__(self, ai_provider):
        self.ai_provider = ai_provider
    
    def generate_from_yaml(self, yaml_file: str) -> List[str]:
        """Generate test files from YAML"""
        with open(yaml_file) as f:
            data = yaml.safe_load(f)
        
        # Build prompt
        prompt = self._build_prompt(data)
        
        # Generate via AI
        code = self.ai_provider.generate_code(prompt)
        
        # Validate and save
        self._validate_syntax(code)
        return self._save_files(code)
    
    def _build_prompt(self, data: Dict) -> str:
        """Build prompt from YAML data"""
        template = """
        Generate pytest tests for:
        
        Acceptance Criteria:
        {% for ac in acceptance_criteria %}
        - {{ ac.criterion }}
        {% endfor %}
        
        Expected Test Methods:
        {% for method in expected_methods %}
        - {{ method }}
        {% endfor %}
        
        Output: Complete pytest file with no placeholders.
        """
        return Template(template).render(**data)
```

#### LAYER-004-01-02-02: Implementation Code Generator

Similar pattern but generates implementation from tests.

---

### Day 3-4: Orchestration (16 hours)

#### LAYER-004-01-03-01: Orchestrator

**Key Implementation:**

`src/orchestration/orchestrator.py`
```python
class AICodeGeneratorOrchestrator:
    """Orchestrates complete TDD cycle"""
    
    def __init__(self, yaml_file, ai_provider):
        self.yaml_file = yaml_file
        self.ai_provider = ai_provider
        self.test_generator = TestCodeGenerator(ai_provider)
        self.impl_generator = ImplementationCodeGenerator(ai_provider)
    
    def execute_full_cycle(self):
        """Execute RED -> GREEN -> REFACTOR"""
        
        # RED: Generate tests
        test_files = self.test_generator.generate_from_yaml(self.yaml_file)
        self._run_tests(expect_fail=True)
        
        # GREEN: Generate implementation
        impl_files = self.impl_generator.generate_from_yaml(self.yaml_file)
        self._run_tests(expect_pass=True)
        
        # REFACTOR: Improve code
        self._refactor_code()
        self._run_tests(expect_pass=True)
        
        # VERIFY: Generate reports
        self._generate_reports()
```

#### LAYER-004-01-03-02: Concurrent Executor

**Key Implementation:**

`src/orchestration/concurrent_executor.py`
```python
import asyncio
from typing import List

class ConcurrentLayerExecutor:
    """Execute multiple layers concurrently"""
    
    def __init__(self, max_concurrent=5):
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
    
    async def execute_layers(self, yaml_files: List[str]):
        """Execute layers concurrently with limit"""
        tasks = [self._execute_one(f) for f in yaml_files]
        return await asyncio.gather(*tasks)
    
    async def _execute_one(self, yaml_file):
        async with self.semaphore:
            orchestrator = AICodeGeneratorOrchestrator(yaml_file)
            return await orchestrator.execute_full_cycle()
```

---

### Day 5: Polish & Testing (8 hours)

1. **End-to-end testing** (3 hours)
2. **Documentation completion** (2 hours)
3. **Bug fixes** (2 hours)
4. **Performance optimization** (1 hour)

---

## Testing Strategy

### Unit Tests
- Test each class method independently
- Mock AI API calls (expensive/slow)
- Focus on logic, not integration

### Integration Tests
- Test real AI API calls (with test keys)
- Test file I/O
- Test component integration

### E2E Tests
- Test complete layer generation
- Test concurrent execution
- Verify all outputs

---

## Common Patterns

### Pattern 1: AI Provider Usage
```python
from src.ai_provider import AIProviderFactory

provider = AIProviderFactory.create("openai", api_key)
code = provider.generate_code(prompt)
```

### Pattern 2: Prompt Building
```python
from jinja2 import Template

template = Template("""...""")
prompt = template.render(acceptance_criteria=ac, expected_methods=methods)
```

### Pattern 3: Validation
```python
import ast

def validate_syntax(code: str):
    try:
        ast.parse(code)
        return True
    except SyntaxError as e:
        raise ValueError(f"Invalid syntax: {e}")
```

---

## Troubleshooting

### Issue: API timeouts
**Solution:** Increase timeout in config, add retry logic

### Issue: Generated code has syntax errors
**Solution:** Add validation step, retry with refined prompt

### Issue: Tests don't pass after implementation
**Solution:** Check traceability mapping, refine prompt

---

## Next Steps After Completion

1. Test on PROJECT-003 layers
2. Optimize prompts for better quality
3. Add more AI providers
4. Scale to 10+ concurrent layers
5. CI/CD integration
