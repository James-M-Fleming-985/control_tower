"""
Execute Layer Integration Module

Integrates AI-powered code generation with PROJECT-003's
execute_layer.py infrastructure. Provides backward-compatible
extension that enables AI generation while preserving existing
manual generation workflows.

Layer: LAYER-004-01-03-03
Feature: FEATURE-004-01-03 TDD Cycle Orchestration

Acceptance Criteria:
- AC-001: Integrate with PROJECT-003 execute_layer.py infrastructure
- AC-002: Preserve backward compatibility
"""

import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Callable
import yaml


class ExecuteLayerIntegration:
    """
    Integrates AI code generation with existing execute_layer
    infrastructure.

    Provides a bridge between PROJECT-003's manual TDD workflow and
    PROJECT-004's AI-powered code generation, maintaining full
    backward compatibility.
    """

    def __init__(self):
        """Initialize with backward-compatible defaults."""
        self.default_ai_enabled = False  # Backward compatible default
        self.integration_version = "1.0.0"
    
    def add_ai_generate_flag(self, parser: argparse.ArgumentParser) -> None:
        """
        Add --ai-generate flag to CLI argument parser.
        
        AC-001: Integrate with PROJECT-003 execute_layer.py infrastructure
        
        Args:
            parser: ArgumentParser to extend with AI flag
        """
        parser.add_argument(
            '--ai-generate',
            action='store_true',
            help='Enable AI-powered code generation'
        )
    
    def inject_ai_code_generator(
        self,
        executor: Any,
        ai_enabled: bool = False
    ) -> Any:
        """
        Inject AI code generator into execute_layer workflow.
        
        AC-001: Integrate with PROJECT-003 execute_layer.py infrastructure
        AC-002: Preserve backward compatibility
        
        Args:
            executor: LayerExecutor instance to enhance
            ai_enabled: Whether to enable AI generation
            
        Returns:
            Enhanced executor (or original if ai_enabled=False)
        """
        if not ai_enabled:
            # Backward compatibility: return unmodified executor
            return executor
        
        # Inject AI generator
        from src.layer.orchestrator.ai_code_generator_orchestrator import (
            AICodeGeneratorOrchestrator
        )
        
        config = {
            'test_generator_path': 'src/layer/test_code_generator',
            'impl_generator_path': 'src/layer/implementation_code_generator',
            'output_base_path': 'Testing Outputs'
        }
        
        executor.ai_generator = AICodeGeneratorOrchestrator(config=config)
        
        return executor
    
    def execute_with_fallback(
        self,
        ai_generator: Any,
        manual_generator: Callable,
        yaml_spec: Dict[str, Any]
    ) -> Any:
        """
        Execute with AI generator, falling back to manual on failure.
        
        AC-002: Preserve backward compatibility
        
        Args:
            ai_generator: AI code generator instance
            manual_generator: Manual generation fallback function
            yaml_spec: YAML specification for generation
            
        Returns:
            Generated code (from AI or manual)
        """
        try:
            return ai_generator.generate_code(yaml_spec)
        except Exception:
            # Graceful degradation to manual generation
            return manual_generator(yaml_spec)
    
    def create_cli_parser(self) -> argparse.ArgumentParser:
        """
        Create CLI parser with AI generation support.
        
        AC-001: Integrate with PROJECT-003 execute_layer.py infrastructure
        
        Returns:
            Configured ArgumentParser
        """
        parser = argparse.ArgumentParser(
            description='Execute layer requirements with optional AI generation'
        )
        
        parser.add_argument(
            '--yaml-file',
            required=True,
            help='Path to layer requirements YAML file'
        )
        
        parser.add_argument(
            '--ai-generate',
            action='store_true',
            help='Enable AI-powered code generation'
        )
        
        parser.add_argument(
            '--phase',
            choices=['red', 'green', 'refactor', 'full-cycle'],
            default='full-cycle',
            help='TDD phase to execute'
        )
        
        parser.add_argument(
            '--concurrent',
            action='store_true',
            help='Enable concurrent layer execution'
        )
        
        parser.add_argument(
            '--max-workers',
            type=int,
            default=3,
            help='Maximum concurrent workers'
        )
        
        parser.add_argument(
            '--ai-provider',
            choices=['openai', 'anthropic', 'local'],
            default='openai',
            help='AI provider to use for code generation'
        )
        
        return parser
    
    def validate_yaml_path(self, yaml_path: str) -> Path:
        """
        Validate YAML file path exists.
        
        AC-001: Integrate with PROJECT-003 execute_layer.py infrastructure
        
        Args:
            yaml_path: Path to YAML file
            
        Returns:
            Validated Path object
            
        Raises:
            FileNotFoundError: If file doesn't exist
        """
        path = Path(yaml_path)
        if not path.exists():
            raise FileNotFoundError(f"YAML file not found: {yaml_path}")
        return path
    
    def build_execution_config(
        self,
        ai_enabled: bool = False,
        concurrent: bool = False,
        max_workers: int = 3,
        ai_provider: str = 'openai',
        **kwargs
    ) -> Dict[str, Any]:
        """
        Build execution configuration dictionary.
        
        AC-001: Integrate with PROJECT-003 execute_layer.py infrastructure
        
        Args:
            ai_enabled: Enable AI generation
            concurrent: Enable concurrent execution
            max_workers: Maximum concurrent workers
            ai_provider: AI provider to use
            **kwargs: Additional configuration
            
        Returns:
            Configuration dictionary
            
        Raises:
            ValueError: If invalid configuration provided
        """
        if max_workers < 1:
            raise ValueError("max_workers must be >= 1")
        
        config = {
            'ai_enabled': ai_enabled,
            'concurrent': concurrent,
            'max_workers': max_workers,
            'ai_provider': ai_provider,
            **kwargs
        }
        
        return config
    
    def wrap_executor(self, layer_executor: Any) -> Any:
        """
        Wrap LayerExecutor with AI capabilities while preserving interface.
        
        AC-002: Preserve backward compatibility
        
        Args:
            layer_executor: Original LayerExecutor instance
            
        Returns:
            Wrapped executor with preserved interface
        """
        # Ensure original interface is preserved
        if not hasattr(layer_executor, 'execute_red_phase'):
            layer_executor.execute_red_phase = lambda: {
                'status': 'not_implemented'
            }
        
        if not hasattr(layer_executor, 'execute_green_phase'):
            layer_executor.execute_green_phase = lambda: {
                'status': 'not_implemented'
            }
        
        if not hasattr(layer_executor, 'execute_refactor_phase'):
            layer_executor.execute_refactor_phase = lambda: {
                'status': 'not_implemented'
            }
        
        return layer_executor
    
    def generate_metadata(
        self,
        layer_id: str,
        ai_enabled: bool = False
    ) -> Dict[str, Any]:
        """
        Generate integration metadata for tracking.
        
        AC-001: Integrate with PROJECT-003 execute_layer.py infrastructure
        
        Args:
            layer_id: Layer identifier
            ai_enabled: Whether AI is enabled
            
        Returns:
            Metadata dictionary
        """
        return {
            'layer_id': layer_id,
            'ai_enabled': ai_enabled,
            'timestamp': datetime.now().isoformat(),
            'integration_version': self.integration_version,
            'source': 'ExecuteLayerIntegration'
        }
    
    def execute_layer(
        self,
        yaml_file: str,
        ai_generate: bool = False,
        phase: str = 'full-cycle',
        concurrent: bool = False,
        max_concurrent: int = 3,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute layer with optional AI generation.
        
        AC-001: Integrate with PROJECT-003 execute_layer.py infrastructure
        AC-002: Preserve backward compatibility
        
        Args:
            yaml_file: Path to layer YAML file
            ai_generate: Enable AI code generation
            phase: TDD phase to execute
            concurrent: Enable concurrent execution
            max_concurrent: Maximum concurrent workers
            **kwargs: Additional configuration
            
        Returns:
            Execution result dictionary
        """
        # Validate YAML file
        yaml_path = self.validate_yaml_path(yaml_file)
        
        # Load YAML specification
        with open(yaml_path, 'r') as f:
            yaml_spec = yaml.safe_load(f)
        
        result = {
            'yaml_file': str(yaml_path),
            'phase': phase,
            'ai_enabled': ai_generate,
            'timestamp': datetime.now().isoformat()
        }
        
        if ai_generate:
            # Use AI-powered orchestrator
            orchestrator = self._create_orchestrator(
                yaml_spec,
                concurrent=concurrent,
                max_concurrent=max_concurrent
            )
            
            # Execute requested phase
            if phase == 'red':
                phase_result = orchestrator.execute_red_phase(yaml_spec)
            elif phase == 'green':
                phase_result = orchestrator.execute_green_phase(
                    yaml_spec,
                    test_results={}
                )
            elif phase == 'refactor':
                phase_result = orchestrator.execute_refactor_phase(
                    yaml_spec,
                    implementation_code=""
                )
            else:  # full-cycle
                phase_result = orchestrator.execute_full_cycle(
                    yaml_spec
                )
            
            result.update(phase_result)
            
            if concurrent:
                result['concurrent_enabled'] = True
                result['max_concurrent'] = max_concurrent
        else:
            # Backward compatible mode - manual generation
            result['manual_mode'] = True
            result['fallback_mode'] = True
        
        return result
    
    def _create_orchestrator(
        self,
        yaml_spec: Dict[str, Any],
        concurrent: bool = False,
        max_concurrent: int = 3
    ) -> Any:
        """
        Create AI code generator orchestrator.
        
        Args:
            yaml_spec: YAML specification
            concurrent: Enable concurrent execution
            max_concurrent: Maximum concurrent workers
            
        Returns:
            AICodeGeneratorOrchestrator instance
        """
        from src.layer.orchestrator.ai_code_generator_orchestrator import (
            AICodeGeneratorOrchestrator
        )
        
        config = {
            'test_generator_path': 'src/layer/test_code_generator',
            'impl_generator_path': 'src/layer/implementation_code_generator',
            'output_base_path': 'Testing Outputs'
        }
        
        orchestrator = AICodeGeneratorOrchestrator(config=config)
        
        # Configure concurrent execution if enabled
        if concurrent:
            from src.concurrent_layer_executor import ConcurrentLayerExecutor
            orchestrator.concurrent_executor = ConcurrentLayerExecutor(
                max_concurrent=max_concurrent
            )
        
        return orchestrator
    
    def execute_from_cli_args(self, args: argparse.Namespace) -> Dict[str, Any]:
        """
        Execute layer from CLI arguments.
        
        AC-001: Integrate with PROJECT-003 execute_layer.py infrastructure
        
        Args:
            args: Parsed CLI arguments
            
        Returns:
            Execution result dictionary
        """
        return self.execute_layer(
            yaml_file=args.yaml_file,
            ai_generate=args.ai_generate,
            phase=args.phase,
            concurrent=getattr(args, 'concurrent', False),
            max_concurrent=getattr(args, 'max_workers', 3)
        )
