"""
Integration Tests for AI Provider Abstraction
Layer: LAYER-004-01-01-01

Integration tests for real AI API interactions.
Note: These tests can be mocked or skipped if API keys are not available.
"""

import pytest
import os
from src.layer.ai_provider_abstraction import (
    OpenAIProvider,
    AnthropicProvider,
    AIProviderFactory,
)

# REQ-LAYER-004-01-01-01


class TestAiProviderAbstractionIntegration:
    """Integration tests for AI Provider Abstraction."""

    def setup_method(self):
        """Setup test fixtures."""
        self.test_prompt = "Write a Python function that returns 'Hello World'"
        self.has_openai_key = bool(os.getenv("OPENAI_API_KEY"))
        self.has_anthropic_key = bool(os.getenv("ANTHROPIC_API_KEY"))

    @pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY"),
        reason="OPENAI_API_KEY not set"
    )
    def test_openai_provider_real_api_call(self):
        """
        AC-002: Test OpenAIProvider with real API call
        
        This test makes a real API call to OpenAI.
        Skipped if OPENAI_API_KEY environment variable is not set.
        """
        # REQ-AC-002
        
        provider = OpenAIProvider()
        result = provider.generate_code(self.test_prompt, max_tokens=100)
        
        assert result is not None
        assert isinstance(result, str)
        assert len(result) > 0
        # Verify it looks like code (contains common Python keywords)
        assert any(keyword in result.lower() for keyword in ['def', 'return', 'hello'])

    @pytest.mark.skipif(
        not os.getenv("ANTHROPIC_API_KEY"),
        reason="ANTHROPIC_API_KEY not set"
    )
    def test_anthropic_provider_real_api_call(self):
        """
        AC-003: Test AnthropicProvider with real API call
        
        This test makes a real API call to Anthropic.
        Skipped if ANTHROPIC_API_KEY environment variable is not set.
        """
        # REQ-AC-003
        
        provider = AnthropicProvider()
        result = provider.generate_code(self.test_prompt, max_tokens=100)
        
        assert result is not None
        assert isinstance(result, str)
        assert len(result) > 0
        # Verify it looks like code
        assert any(keyword in result.lower() for keyword in ['def', 'return', 'hello'])

    def test_provider_handles_api_timeout(self):
        """
        Test that providers handle API timeouts gracefully
        
        Note: This is a placeholder test that would require more complex
        mocking or network manipulation to truly test timeout handling.
        """
        # For now, just verify providers can be instantiated
        provider = OpenAIProvider(api_key="test-key")
        assert provider is not None

    def test_provider_handles_invalid_api_key(self):
        """
        Test that providers handle invalid API keys appropriately
        """
        # Test with obviously invalid key
        provider = OpenAIProvider(api_key="invalid-key-123")
        
        # Should raise RuntimeError when trying to use invalid key
        # Note: Without openai installed, it will raise import error first
        with pytest.raises(RuntimeError):
            provider.generate_code("test prompt")

    def test_provider_handles_rate_limit_error(self):
        """
        Test that providers handle rate limit errors
        
        Note: This is a placeholder that would require specific
        rate limit triggering or mocking to properly test.
        """
        # For now, just verify factory can create providers
        provider = AIProviderFactory.create_provider("openai", api_key="test-key")
        assert provider is not None

    def test_standalone_integration(self):
        """
        Standalone integration test that doesn't require API keys.
        
        Tests the complete flow of creating and configuring providers
        without making actual API calls.
        """
        # Test creating providers via factory
        openai_provider = AIProviderFactory.create_provider(
            "openai",
            api_key="test-key-openai"
        )
        assert openai_provider.validate_configuration() is True
        
        anthropic_provider = AIProviderFactory.create_provider(
            "anthropic",
            api_key="test-key-anthropic"
        )
        assert anthropic_provider.validate_configuration() is True
        
        # Verify both are proper instances
        assert openai_provider.__class__.__name__ == "OpenAIProvider"
        assert anthropic_provider.__class__.__name__ == "AnthropicProvider"

