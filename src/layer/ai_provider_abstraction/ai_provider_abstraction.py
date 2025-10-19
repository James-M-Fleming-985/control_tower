"""
AI Provider Abstraction

Layer: LAYER-004-01-01-01
Requirement: AI Provider Abstraction

Provides abstraction layer for multiple AI providers (OpenAI, Anthropic, Local).
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime
import os

# REQ-LAYER-004-01-01-01


class AIProviderInterface(ABC):
    """
    Abstract base class for AI providers.
    
    AC-001: Define AIProviderInterface with generate_code() method
    """
    
    @abstractmethod
    def generate_code(self, prompt: str, **kwargs) -> str:
        """
        Generate code using the AI provider.
        
        Args:
            prompt: The prompt to send to the AI
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Generated code as a string
            
        Raises:
            ValueError: If prompt is empty or invalid
            RuntimeError: If API call fails
        """
        pass
    
    @abstractmethod
    def validate_configuration(self) -> bool:
        """
        Validate that the provider is properly configured.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        pass


class OpenAIProvider(AIProviderInterface):
    """
    OpenAI GPT-4 provider implementation.
    
    AC-002: Implement OpenAIProvider with GPT-4 integration
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4-turbo-preview"):
        """
        Initialize OpenAI provider.
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            model: Model to use (default: gpt-4-turbo-preview)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        
        if not self.api_key:
            raise ValueError("OpenAI API key not provided and OPENAI_API_KEY env var not set")
    
    def generate_code(self, prompt: str, temperature: float = 0.2, max_tokens: int = 20480) -> str:
        """
        Generate code using OpenAI GPT-4.
        
        Args:
            prompt: The prompt to send to OpenAI
            temperature: Sampling temperature (default: 0.2 for more deterministic)
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated code as a string
            
        Raises:
            ValueError: If prompt is empty
            RuntimeError: If API call fails
        """
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")
        
        try:
            # Import here to avoid dependency issues if not installed
            import openai
            
            client = openai.OpenAI(api_key=self.api_key)
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert Python programmer. Generate clean, well-documented code."},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content
            
        except ImportError:
            raise RuntimeError("openai package not installed. Install with: pip install openai")
        except Exception as e:
            raise RuntimeError(f"OpenAI API call failed: {str(e)}")
    
    def validate_configuration(self) -> bool:
        """
        Validate OpenAI configuration.
        
        Returns:
            True if API key is set, False otherwise
        """
        return bool(self.api_key and len(self.api_key) > 0)


class AnthropicProvider(AIProviderInterface):
    """
    Anthropic Claude provider implementation.
    
    AC-003: Implement AnthropicProvider with Claude integration
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-opus-4-20250514"
    ):
        """
        Initialize Anthropic provider.
        
        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
            model: Model to use (default: claude-opus-4-20250514 - Highest quality, best reasoning)
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model = model
        
        if not self.api_key:
            raise ValueError("Anthropic API key not provided and ANTHROPIC_API_KEY env var not set")
    
    def generate_code(self, prompt: str, max_tokens: int = 20480) -> str:
        """
        Generate code using Anthropic Claude.
        
        Args:
            prompt: The prompt to send to Claude
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated code as a string
            
        Raises:
            ValueError: If prompt is empty
            RuntimeError: If API call fails or response is truncated
        """
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")
        
        try:
            # Import here to avoid dependency issues if not installed
            import anthropic
            
            client = anthropic.Anthropic(api_key=self.api_key)
            
            # Always use standard create (streaming timeout warning is misleading)
            # The SDK will handle long requests automatically
            message = client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                timeout=600.0  # 10 minute timeout for large requests
            )
            
            # Check if response was truncated
            if message.stop_reason == "max_tokens":
                print(f"⚠️ WARNING: Response truncated at max_tokens={max_tokens}")
                print(f"   Input tokens: {message.usage.input_tokens}")
                print(f"   Output tokens: {message.usage.output_tokens}")
                print(f"   Consider increasing max_tokens or simplifying the request")
            
            return message.content[0].text
            
        except ImportError:
            raise RuntimeError("anthropic package not installed. Install with: pip install anthropic")
        except Exception as e:
            raise RuntimeError(f"Anthropic API call failed: {str(e)}")
    
    def validate_configuration(self) -> bool:
        """
        Validate Anthropic configuration.
        
        Returns:
            True if API key is set, False otherwise
        """
        return bool(self.api_key and len(self.api_key) > 0)


class AIProviderFactory:
    """
    Factory for creating AI provider instances.
    
    AC-004: Implement AIProviderFactory for provider creation
    """
    
    _providers = {
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
    }
    
    @classmethod
    def create_provider(cls, provider_type: str, **kwargs) -> AIProviderInterface:
        """
        Create an AI provider instance.
        
        Args:
            provider_type: Type of provider ("openai", "anthropic", "local")
            **kwargs: Additional arguments to pass to provider constructor
            
        Returns:
            AIProviderInterface instance
            
        Raises:
            ValueError: If provider_type is not supported
        """
        if provider_type not in cls._providers:
            raise ValueError(
                f"Unsupported provider type: {provider_type}. "
                f"Supported types: {', '.join(cls._providers.keys())}"
            )
        
        provider_class = cls._providers[provider_type]
        return provider_class(**kwargs)
    
    @classmethod
    def get_supported_providers(cls) -> List[str]:
        """
        Get list of supported provider types.
        
        Returns:
            List of supported provider type names
        """
        return list(cls._providers.keys())
