"""
Integration Tests for Error Handling and Retry Logic
Layer: LAYER-004-01-01-02

Tests the integrated behavior of retry logic, error handling, and rate limiting.
"""

import pytest
import time
from unittest.mock import Mock, patch

from src.layer.error_handling_and_retry_logic import (
    RetryManager,
    ErrorHandler,
    RateLimitHandler,
    ResponseValidator
)


class TestErrorHandlingAndRetryLogicIntegration:
    """Integration tests for Error Handling and Retry Logic."""

    def setup_method(self):
        """Setup test fixtures."""
        self.retry_manager = RetryManager(max_retries=3, base_delay=0.01)
        self.rate_limiter = RateLimitHandler(max_requests_per_minute=10)

    def test_retry_with_simulated_api_timeout(self):
        """
        Integration Test: Retry logic with simulated API timeout
        
        Tests retry manager with timeout errors.
        """
        call_count = 0
        
        def api_call_with_timeout():
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                raise TimeoutError("API timed out")
            return {"status": "success", "data": "result"}
        
        result = self.retry_manager.retry_with_backoff(api_call_with_timeout)
        
        assert result["status"] == "success"
        assert call_count == 3

    def test_rate_limit_handling_with_queue(self):
        """
        Integration Test: Rate limit handling with request queue
        
        Tests rate limiter with multiple requests.
        """
        successful_requests = 0
        
        # Make requests up to the limit
        for i in range(10):
            if self.rate_limiter.can_make_request():
                self.rate_limiter.record_request()
                successful_requests += 1
        
        assert successful_requests == 10
        
        # Next request should be blocked
        assert self.rate_limiter.can_make_request() is False

    def test_error_recovery_full_workflow(self):
        """
        Integration Test: Full error recovery workflow
        
        Tests complete error handling and recovery flow.
        """
        call_count = 0
        
        def flaky_api_call():
            nonlocal call_count
            call_count += 1
            
            if call_count == 1:
                raise TimeoutError("Timeout")
            elif call_count == 2:
                raise ValueError("Rate limit")
            else:
                return {
                    "code": "def add(a, b):\n    return a + b\n"
                }
        
        # Retry the call
        result = self.retry_manager.retry_with_backoff(flaky_api_call)
        
        # Validate the response
        validation = ResponseValidator.validate_syntax(result["code"])
        
        assert validation["is_valid"] is True
        assert call_count == 3

    def test_multi_provider_error_handling(self):
        """
        Integration Test: Multi-provider error handling
        
        Tests error handling across different provider errors.
        """
        # Simulate different provider errors
        errors = [
            (TimeoutError("OpenAI timeout"), "timeout"),
            (ValueError("Invalid API key"), "invalid_api_key"),
            (Exception("Rate limit"), "rate_limit")
        ]
        
        for error, expected_type in errors:
            if isinstance(error, TimeoutError):
                result = ErrorHandler.handle_timeout_error(error, "OpenAI")
            elif "key" in str(error):
                result = ErrorHandler.handle_api_key_error(error)
            else:
                result = self.rate_limiter.handle_rate_limit_error(error)
            
            assert result["error_type"] == expected_type

    def test_response_validation_integration(self):
        """
        Integration Test: Response validation with syntax and quality checks
        
        Tests complete response validation workflow.
        """
        # Test valid code
        valid_code = '''
def fibonacci(n):
    """Calculate fibonacci number."""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
'''
        
        syntax_result = ResponseValidator.validate_syntax(valid_code)
        quality_result = ResponseValidator.validate_quality(valid_code)
        
        assert syntax_result["is_valid"] is True
        assert quality_result["is_quality"] is True
        assert quality_result["quality_score"] == 100

    def test_end_to_end_retry_workflow(self):
        """
        Integration Test: End-to-end retry workflow with validation
        
        Tests complete retry → validate workflow.
        """
        call_count = 0
        
        def api_with_retry_and_validation():
            nonlocal call_count
            call_count += 1
            
            if call_count < 2:
                raise TimeoutError("Transient error")
            
            return '''
def greet(name):
    """Greet the user."""
    return f"Hello, {name}!"
'''
        
        # Retry the API call
        code = self.retry_manager.retry_with_backoff(api_with_retry_and_validation)
        
        # Validate syntax
        syntax_result = ResponseValidator.validate_syntax(code)
        assert syntax_result["is_valid"] is True
        
        # Validate quality
        quality_result = ResponseValidator.validate_quality(code)
        assert quality_result["is_quality"] is True

    def test_concurrent_error_handling(self):
        """
        Integration Test: Concurrent error handling scenarios
        
        Tests handling multiple errors in sequence.
        """
        scenarios = []
        
        # Scenario 1: Timeout then success
        def scenario_1():
            if not hasattr(scenario_1, 'called'):
                scenario_1.called = True
                raise TimeoutError("Timeout")
            return "success"
        
        result1 = self.retry_manager.retry_with_backoff(scenario_1)
        scenarios.append(result1 == "success")
        
        # Scenario 2: Rate limit handling
        for _ in range(10):
            if self.rate_limiter.can_make_request():
                self.rate_limiter.record_request()
        
        scenarios.append(not self.rate_limiter.can_make_request())
        
        # All scenarios should pass
        assert all(scenarios)
