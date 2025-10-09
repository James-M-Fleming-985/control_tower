"""
Unit Tests for AI Provider Abstraction
Layer: LAYER-004-01-01-01

Tests for AIProviderInterface, OpenAIProvider, AnthropicProvider, and AIProviderFactory.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.layer.ai_provider_abstraction import (
    AIProviderInterface,
    OpenAIProvider,
    AnthropicProvider,
    AIProviderFactory,
)

# REQ-LAYER-004-01-01-01


class TestAiProviderAbstractionUnit:
    """Unit tests for AI Provider Abstraction."""

    def setup_method(self):
        """Setup test fixtures."""
        self.test_api_key = "test-api-key-123"
        self.test_prompt = "Generate a Python function to add two numbers"

    # AC-001: AIProviderInterface tests
    def test_ai_provider_interface_contract(self):
        """
        AC-001: Define AIProviderInterface with generate_code() method
        
        Verify that AIProviderInterface is an abstract base class with required methods.
        """
        # REQ-AC-001
        
        # Verify it's an ABC
        assert hasattr(AIProviderInterface, '__abstractmethods__')
        
        # Verify required abstract methods exist
        abstract_methods = AIProviderInterface.__abstractmethods__
        assert 'generate_code' in abstract_methods
        assert 'validate_configuration' in abstract_methods
        
        # Verify we cannot instantiate abstract class directly
        with pytest.raises(TypeError):
            AIProviderInterface()

    # AC-002: OpenAIProvider tests
    def test_openai_provider_initialization(self):
        """
        AC-002: Test OpenAIProvider initialization with API key
        """
        # REQ-AC-002
        
        # Test initialization with explicit API key
        provider = OpenAIProvider(api_key=self.test_api_key)
        assert provider.api_key == self.test_api_key
        assert provider.model == "gpt-4-turbo-preview"
        
        # Test initialization with custom model
        provider = OpenAIProvider(api_key=self.test_api_key, model="gpt-4")
        assert provider.model == "gpt-4"

    def test_openai_provider_api_key_validation(self):
        """
        AC-002: Test OpenAIProvider validates API key requirement
        """
        # REQ-AC-002
        
        # Should raise error if no API key provided and env var not set
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="OpenAI API key not provided"):
                OpenAIProvider()
    
    def test_openai_provider_validate_configuration(self):
        """
        AC-002: Test OpenAIProvider configuration validation
        """
        # REQ-AC-002
        
        provider = OpenAIProvider(api_key=self.test_api_key)
        assert provider.validate_configuration() is True
        
        # Test invalid configuration
        provider.api_key = None
        assert provider.validate_configuration() is False

    def test_openai_provider_generate_code(self):
        """
        AC-002: Test OpenAIProvider generate_code method
        """
        # REQ-AC-002
        
        # Create a mock openai module
        mock_openai = MagicMock()
        mock_client = MagicMock()
        mock_openai.OpenAI.return_value = mock_client
        
        # Setup mock response with proper structure
        mock_message = MagicMock()
        mock_message.content = "def add(a, b): return a + b"
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response
        
        # Patch the import at the point of use
        with patch.dict('sys.modules', {'openai': mock_openai}):
            provider = OpenAIProvider(api_key=self.test_api_key)
            result = provider.generate_code(self.test_prompt)
            
            assert result == "def add(a, b): return a + b"
            mock_client.chat.completions.create.assert_called_once()
    
    def test_openai_provider_empty_prompt_raises_error(self):
        """
        AC-002: Test OpenAIProvider rejects empty prompts
        """
        # REQ-AC-002
        
        provider = OpenAIProvider(api_key=self.test_api_key)
        
        with pytest.raises(ValueError, match="Prompt cannot be empty"):
            provider.generate_code("")
        
        with pytest.raises(ValueError, match="Prompt cannot be empty"):
            provider.generate_code("   ")

    # AC-003: AnthropicProvider tests
    def test_anthropic_provider_initialization(self):
        """
        AC-003: Test AnthropicProvider initialization with API key
        """
        # REQ-AC-003
        
        # Test initialization with explicit API key
        provider = AnthropicProvider(api_key=self.test_api_key)
        assert provider.api_key == self.test_api_key
        assert provider.model == "claude-sonnet-4-5"
        
        # Test initialization with custom model
        provider = AnthropicProvider(api_key=self.test_api_key, model="claude-3-opus-20240229")
        assert provider.model == "claude-3-opus-20240229"

    def test_anthropic_provider_api_key_validation(self):
        """
        AC-003: Test AnthropicProvider validates API key requirement
        """
        # REQ-AC-003
        
        # Should raise error if no API key provided and env var not set
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="Anthropic API key not provided"):
                AnthropicProvider()
    
    def test_anthropic_provider_validate_configuration(self):
        """
        AC-003: Test AnthropicProvider configuration validation
        """
        # REQ-AC-003
        
        provider = AnthropicProvider(api_key=self.test_api_key)
        assert provider.validate_configuration() is True
        
        # Test invalid configuration
        provider.api_key = None
        assert provider.validate_configuration() is False

    def test_anthropic_provider_generate_code(self):
        """
        AC-003: Test AnthropicProvider generate_code method
        """
        # REQ-AC-003
        
        # Create a mock anthropic module
        mock_anthropic = MagicMock()
        mock_client = MagicMock()
        mock_anthropic.Anthropic.return_value = mock_client
        
        # Setup mock response with proper structure
        mock_text = MagicMock()
        mock_text.text = "def add(a, b): return a + b"
        mock_message = MagicMock()
        mock_message.content = [mock_text]
        mock_client.messages.create.return_value = mock_message
        
        # Patch the import at the point of use
        with patch.dict('sys.modules', {'anthropic': mock_anthropic}):
            provider = AnthropicProvider(api_key=self.test_api_key)
            result = provider.generate_code(self.test_prompt)
            
            assert result == "def add(a, b): return a + b"
            mock_client.messages.create.assert_called_once()
    
    def test_anthropic_provider_empty_prompt_raises_error(self):
        """
        AC-003: Test AnthropicProvider rejects empty prompts
        """
        # REQ-AC-003
        
        provider = AnthropicProvider(api_key=self.test_api_key)
        
        with pytest.raises(ValueError, match="Prompt cannot be empty"):
            provider.generate_code("")
        
        with pytest.raises(ValueError, match="Prompt cannot be empty"):
            provider.generate_code("   ")

    # AC-004: AIProviderFactory tests
    def test_provider_factory_creates_openai(self):
        """
        AC-004: Test AIProviderFactory creates OpenAI provider
        """
        # REQ-AC-004
        
        provider = AIProviderFactory.create_provider("openai", api_key=self.test_api_key)
        assert isinstance(provider, OpenAIProvider)
        assert isinstance(provider, AIProviderInterface)
        assert provider.api_key == self.test_api_key

    def test_provider_factory_creates_anthropic(self):
        """
        AC-004: Test AIProviderFactory creates Anthropic provider
        """
        # REQ-AC-004
        
        provider = AIProviderFactory.create_provider("anthropic", api_key=self.test_api_key)
        assert isinstance(provider, AnthropicProvider)
        assert isinstance(provider, AIProviderInterface)
        assert provider.api_key == self.test_api_key

    def test_provider_factory_invalid_provider_raises_error(self):
        """
        AC-004: Test AIProviderFactory rejects invalid provider types
        """
        # REQ-AC-004
        
        with pytest.raises(ValueError, match="Unsupported provider type"):
            AIProviderFactory.create_provider("invalid_provider")
    
    def test_provider_factory_get_supported_providers(self):
        """
        AC-004: Test AIProviderFactory lists supported providers
        """
        # REQ-AC-004
        
        supported = AIProviderFactory.get_supported_providers()
        assert isinstance(supported, list)
        assert "openai" in supported
        assert "anthropic" in supported

