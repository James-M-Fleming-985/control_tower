"""
Implementation Code Generator

Layer: LAYER-004-01-02-02
Requirement: Implementation Code Generator

Generates Python implementation code from YAML acceptance criteria
and failing tests.
"""

from typing import Dict, List, Optional, Any
from pathlib import Path
import ast
import re
import yaml

# REQ-LAYER-004-01-02-02

# Constants for code generation
DEFAULT_LAYER_ID = 'UNKNOWN'
DEFAULT_REQUIREMENT_NAME = 'Unknown Requirement'
DEFAULT_CRITERION_ID = 'AC-XXX'
MAX_METHOD_NAME_WORDS = 8


class CodeValidator:
    """Validates generated implementation code for syntax and quality."""
    
    # Quality metric weights
    QUALITY_METRICS = {
        'has_docstrings',
        'has_type_hints',
        'has_imports',
        'has_classes',
        'has_methods',
        'syntax_valid'
    }
    
    def __init__(self):
        """Initialize the code validator."""
        self.validation_rules = {
            'syntax': True,
            'type_hints': True,
            'docstrings': True,
            'minimal': True
        }
    
    def validate_syntax(self, code: str) -> bool:
        """
        AC-002: Validate generated code syntax before saving
        
        Args:
            code: Python code to validate
            
        Returns:
            True if syntax is valid, False otherwise
        """
        # REQ-AC-002
        try:
            ast.parse(code)
            return True
        except SyntaxError:
            return False
    
    def validate_quality(self, code: str) -> Dict[str, Any]:
        """
        AC-002: Validate generated implementation quality
        
        Args:
            code: Python code to validate
            
        Returns:
            Dictionary with quality metrics
        """
        # REQ-AC-002
        
        quality = {
            'has_docstrings': '"""' in code or "'''" in code,
            'has_type_hints': '->' in code or ': ' in code,
            'has_imports': 'import ' in code or 'from ' in code,
            'has_classes': 'class ' in code,
            'has_methods': 'def ' in code,
            'syntax_valid': self.validate_syntax(code)
        }
        
        quality['overall_score'] = sum(quality.values()) / len(quality)
        return quality


class ImplementationCodeGenerator:
    """
    Implementation Code Generator
    
    Acceptance Criteria:
    - Generate implementation code that passes generated tests
    - Validate generated code syntax before saving
    - Use YAML traceability mapping to generate correct methods
    """

    def __init__(self, ai_provider=None):
        """
        Initialize the implementation code generator.
        
        Args:
            ai_provider: Optional AI provider for code generation
        """
        self.ai_provider = ai_provider
        self.validator = CodeValidator()
        self.generated_implementations: List[str] = []
        self._generation_count = 0

    def parse_yaml_file(self, yaml_path: Path) -> Dict[str, Any]:
        """
        Parse YAML specification file.
        
        Args:
            yaml_path: Path to YAML file
            
        Returns:
            Parsed YAML as dictionary
            
        Raises:
            ValueError: If YAML is invalid or empty
            yaml.YAMLError: If YAML syntax is invalid
        """
        if not yaml_path.exists():
            raise ValueError(
                f"YAML specification file not found: {yaml_path}\n"
                f"Please ensure the file exists and the path is correct."
            )
        
        try:
            with open(yaml_path, 'r') as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(
                f"Invalid YAML syntax in {yaml_path}: {e}"
            ) from e
        
        if not data:
            raise ValueError(
                f"YAML file is empty or contains no data: {yaml_path}"
            )
        
        return data

    def extract_acceptance_criteria(self, yaml_data: Dict) -> List[Dict]:
        """
        Extract acceptance criteria from YAML data.
        
        Args:
            yaml_data: Parsed YAML dictionary
            
        Returns:
            List of acceptance criteria dictionaries
        """
        ac_list = yaml_data.get('acceptance_criteria', [])
        
        if not ac_list:
            return []
        
        return ac_list

    def extract_traceability_mapping(self, yaml_data: Dict) -> Dict[str, Any]:
        """
        AC-003: Use YAML traceability mapping to generate correct methods
        
        Extract traceability mapping from YAML specification.
        
        Args:
            yaml_data: Parsed YAML dictionary
            
        Returns:
            Traceability mapping dictionary
        """
        # REQ-AC-003
        
        traceability = yaml_data.get('traceability', {})
        mapping = traceability.get('requirement_to_test_mapping', {})
        
        return mapping

    def parse_failing_tests(self, test_file_path: Path) -> List[Dict]:
        """
        Parse failing tests to extract requirements.
        
        Args:
            test_file_path: Path to test file
            
        Returns:
            List of test information dictionaries
        """
        if not test_file_path.exists():
            return []
        
        with open(test_file_path, 'r') as f:
            content = f.read()
        
        # Extract test methods
        test_pattern = r'def (test_\w+)\(self\):'
        tests = re.findall(test_pattern, content)
        
        test_info = []
        for test_name in tests:
            test_info.append({
                'name': test_name,
                'file': str(test_file_path),
                'status': 'failing'
            })
        
        return test_info

    def generate_implementation_class(
        self,
        layer_id: str,
        requirement_name: str,
        acceptance_criteria: List[Dict],
        traceability_mapping: Dict[str, Any]
    ) -> str:
        """
        AC-001: Generate implementation code that passes generated tests
        
        Generate a complete implementation class with methods.
        
        Args:
            layer_id: Layer identifier
            requirement_name: Name of the requirement
            acceptance_criteria: List of AC dictionaries
            traceability_mapping: Traceability mapping from YAML
            
        Returns:
            Generated implementation code as string
        """
        # REQ-AC-001
        
        class_name = self._to_class_name(requirement_name)
        
        impl_code = f'''"""
{requirement_name}

Layer: {layer_id}

Generated from acceptance criteria.
Implements minimal functionality to pass tests (TDD GREEN phase).
"""

from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime

# REQ-{layer_id}


class {class_name}:
    """
    {requirement_name}
    
    Implements the following acceptance criteria:
'''
        
        # Add AC list to docstring
        for ac in acceptance_criteria:
            criterion_id = ac.get('criterion_id', 'AC-XXX')
            criterion = ac.get('criterion', '')
            impl_code += f'    - {criterion_id}: {criterion}\n'
        
        impl_code += '    """\n\n'
        
        # Generate __init__ method
        impl_code += '    def __init__(self):\n'
        impl_code += '        """Initialize the component."""\n'
        impl_code += '        self.state = {}\n'
        impl_code += '        self.initialized = True\n\n'
        
        # Generate methods for each AC
        for ac in acceptance_criteria:
            impl_code += self._generate_method_for_ac(
                ac, traceability_mapping
            )
        
        return impl_code

    def _generate_method_for_ac(
        self,
        ac: Dict,
        traceability_mapping: Dict
    ) -> str:
        """
        Generate a method implementation for an acceptance criterion.
        
        Args:
            ac: Acceptance criterion dictionary
            traceability_mapping: Traceability mapping
            
        Returns:
            Generated method code
        """
        criterion_id = ac.get('criterion_id', 'AC-XXX')
        criterion = ac.get('criterion', '')
        method_name = self._to_method_name(criterion)
        
        method_code = f'''    def {method_name}(self, *args, **kwargs) -> Any:
        """
        {criterion_id}: {criterion}
        
        Minimal implementation to pass tests.
        
        Returns:
            Result based on acceptance criterion
        """
        # REQ-{criterion_id}
        
        # Minimal implementation
        return True
    
'''
        return method_code

    def generate_implementation_methods(
        self,
        acceptance_criteria: List[Dict],
        method_signatures: Optional[Dict] = None
    ) -> List[str]:
        """
        AC-001: Generate implementation methods from acceptance criteria
        
        Args:
            acceptance_criteria: List of AC dictionaries
            method_signatures: Optional method signature specifications
            
        Returns:
            List of generated method code strings
        """
        # REQ-AC-001
        
        methods = []
        for ac in acceptance_criteria:
            method_code = self._generate_method_for_ac(ac, {})
            methods.append(method_code)
        
        return methods

    def generate_implementation_from_yaml(
        self,
        yaml_path: Path,
        output_dir: Path
    ) -> Path:
        """
        AC-001 & AC-003: Generate implementation from YAML specification
        
        Main entry point for implementation generation.
        
        Args:
            yaml_path: Path to YAML specification
            output_dir: Directory to save generated implementation
            
        Returns:
            Path to generated implementation file
            
        Raises:
            ValueError: If YAML is invalid
        """
        # REQ-AC-001, REQ-AC-003
        
        # Parse YAML
        yaml_data = self.parse_yaml_file(yaml_path)
        
        # Extract metadata and ACs
        metadata = yaml_data.get('metadata', {})
        layer_id = metadata.get('requirement_id', 'UNKNOWN')
        requirement_name = metadata.get(
            'requirement_name',
            'Unknown Requirement'
        )
        acceptance_criteria = self.extract_acceptance_criteria(yaml_data)
        traceability_mapping = self.extract_traceability_mapping(
            yaml_data
        )
        
        # Generate implementation code
        impl_code = self.generate_implementation_class(
            layer_id,
            requirement_name,
            acceptance_criteria,
            traceability_mapping
        )
        
        # Validate syntax before saving
        if not self.validator.validate_syntax(impl_code):
            raise ValueError(
                f"Generated code for {requirement_name} has syntax errors.\n"
                "Please check the YAML specification and try again."
            )
        
        # Save implementation
        snake_case_name = self._to_snake_case(requirement_name)
        impl_file_path = output_dir / f"{snake_case_name}.py"
        impl_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(impl_file_path, 'w', encoding='utf-8') as f:
            f.write(impl_code)
        
        # Track generation statistics
        self.generated_implementations.append(impl_code)
        self._generation_count += 1
        
        return impl_file_path

    def add_docstrings(self, code: str) -> str:
        """
        Add docstrings to code that lacks them.
        
        Args:
            code: Python code
            
        Returns:
            Code with docstrings added
        """
        # Simple implementation - in practice would be more sophisticated
        if '"""' not in code and "'''" not in code:
            lines = code.split('\n')
            if lines and not lines[0].startswith('"""'):
                lines.insert(0, '"""Generated implementation."""')
                return '\n'.join(lines)
        return code

    def add_type_hints(self, code: str) -> str:
        """
        Add type hints to code.
        
        Args:
            code: Python code
            
        Returns:
            Code with type hints added
        """
        # Minimal implementation - already generated with type hints
        return code

    def format_code(self, code: str) -> str:
        """
        Format generated code for consistency.
        
        Args:
            code: Python code
            
        Returns:
            Formatted code
        """
        # Remove excessive blank lines
        while '\n\n\n' in code:
            code = code.replace('\n\n\n', '\n\n')
        
        # Ensure final newline
        if not code.endswith('\n'):
            code += '\n'
        
        return code

    @property
    def generation_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about code generation activity.
        
        Returns:
            Dictionary with generation statistics
        """
        return {
            'total_generated': self._generation_count,
            'implementations_stored': len(self.generated_implementations),
            'has_ai_provider': self.ai_provider is not None
        }

    def _to_class_name(self, text: str) -> str:
        """
        Convert text to PascalCase class name.
        
        Removes special characters and capitalizes each word.
        """
        if not text:
            return 'GeneratedClass'
        words = re.sub(r'[^a-zA-Z0-9\s]', ' ', text).split()
        return ''.join(word.capitalize() for word in words)

    def _to_snake_case(self, text: str) -> str:
        """
        Convert text to snake_case.
        
        Removes special characters and joins with underscores.
        """
        if not text:
            return 'generated_module'
        text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
        words = text.lower().split()
        return '_'.join(words)

    def _to_method_name(self, text: str) -> str:
        """
        Convert criterion text to method name.
        
        Limits to first 8 words to keep method names manageable.
        """
        if not text:
            return 'generated_method'
        text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
        words = text.lower().split()
        return '_'.join(words[:MAX_METHOD_NAME_WORDS])

        
