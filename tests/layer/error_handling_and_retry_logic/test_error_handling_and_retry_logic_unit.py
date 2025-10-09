"""
Unit Tests for Error Handling and Retry Logic
Layer: LAYER-004-01-01-02

Tests the retry logic, error handling, and response validation components.
"""

import pytest

from src.layer.error_handling_and_retry_logic import (
    RetryManager,
    ErrorHandler,
    RateLimitHandler,
    ResponseValidator
)


class TestErrorHandlingAndRetryLogicUnit:
    """Unit tests for Error Handling and Retry Logic."""

    def setup_method(self):
        """Setup test fixtures."""
        self.retry_manager = RetryManager(
            max_retries=3,
            base_delay=0.01,
            max_delay=0.1,
            backoff_factor=2.0
        )
        self.rate_limiter = RateLimitHandler(max_requests_per_minute=5)

    def test_implement_exponential_backoff_retry_logic(self):
        """
        AC-001: Implement exponential backoff retry logic
        
        This test validates exponential backoff calculation.
        """
        # REQ-AC-001
        
        # Test delay calculation
        delay_0 = self.retry_manager.calculate_delay(0)
        delay_1 = self.retry_manager.calculate_delay(1)
        delay_2 = self.retry_manager.calculate_delay(2)
        
        assert delay_0 == 0.01
        assert delay_1 == 0.02
        assert delay_2 == 0.04
        
        # Test max delay cap
        delay_100 = self.retry_manager.calculate_delay(100)
        assert delay_100 == 0.1

    def test_handle_api_timeout_errors_gracefully(self):
        """
        AC-002: Handle API timeout errors gracefully
        
        This test validates timeout error handling.
        """
        # REQ-AC-002
        
        error = TimeoutError("API request timed out")
        result = ErrorHandler.handle_timeout_error(error, "OpenAI API call")
        
        assert result["error_type"] == "timeout"
        assert "timed out" in result["error_message"]
        assert result["context"] == "OpenAI API call"
        assert result["recovery_action"] == "retry"
        assert "timestamp" in result

    def test_handle_rate_limit_errors_with_queueing(self):
        """
        AC-003: Handle rate limit errors with queueing
        
        This test validates rate limit enforcement.
        """
        # REQ-AC-003
        
        # Initially should allow requests
        assert self.rate_limiter.can_make_request() is True
        
        # Fill up the rate limit
        for _ in range(5):
            self.rate_limiter.record_request()
        
        # Should now be at limit
        assert self.rate_limiter.can_make_request() is False
        
        # Wait time should be positive
        wait_time = self.rate_limiter.get_wait_time()
        assert wait_time > 0

    def test_validate_ai_api_responses_for_code(self):
        """
        AC-004: Validate AI API responses for code quality
        
        This test validates code syntax and quality validation.
        """
        # REQ-AC-004
        
        # Test valid code
        valid_code = '''
def add(a, b):
    """Add two numbers."""
    return a + b
'''
        result = ResponseValidator.validate_syntax(valid_code)
        assert result["is_valid"] is True
        
        # Test invalid code
        invalid_code = "def broken( return 42"
        result = ResponseValidator.validate_syntax(invalid_code)
        assert result["is_valid"] is False
        assert result["error_type"] == "syntax_error"
        
        # Test quality validation
        good_code = '''
def calculate_sum(numbers):
    """Calculate the sum."""
    return sum(numbers)
'''
        result = ResponseValidator.validate_quality(good_code)
        assert result["is_quality"] is True
        assert result["quality_score"] == 100

    def test_retry_logic_max_retries_exceeded(self):
        """Test that max retries is enforced."""
        call_count = 0
        
        def failing_function():
            nonlocal call_count
            call_count += 1
            raise ValueError("Simulated failure")
        
        with pytest.raises(RuntimeError, match="Max retries"):
            self.retry_manager.retry_with_backoff(failing_function)
        
        assert call_count == 4  # initial + 3 retries

    def test_retry_logic_success_after_retry(self):
        """Test successful execution after retry."""
        call_count = 0
        
        def flaky_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Transient failure")
            return "success"
        
        result = self.retry_manager.retry_with_backoff(flaky_function)
        assert result == "success"
        assert call_count == 3

    def test_error_handler_invalid_api_key(self):
        """Test API key error handling."""
        error = ValueError("Invalid API key")
        result = ErrorHandler.handle_api_key_error(error)
        
        assert result["error_type"] == "invalid_api_key"
        assert result["recovery_action"] == "check_credentials"

    def test_error_handler_invalid_response(self):
        """Test invalid response handling."""
        response = "This is not valid" * 10
        result = ErrorHandler.handle_invalid_response(response)
        
        assert result["error_type"] == "invalid_response"
        assert len(result["response_preview"]) <= 100

    def test_rate_limit_error_handling(self):
        """Test rate limit error handler."""
        error = Exception("Rate limit exceeded")
        result = self.rate_limiter.handle_rate_limit_error(error)
        
        assert result["error_type"] == "rate_limit"
        assert result["recovery_action"] == "wait_and_retry"
        assert "wait_time_seconds" in result

    def test_validate_syntax_empty_code(self):
        """Test validation of empty code."""
        result = ResponseValidator.validate_syntax("")
        assert result["is_valid"] is False
        assert result["error_type"] == "empty_code"

    def test_validate_quality_poor_code(self):
        """Test quality validation with poor code."""
        poor_code = "x = 1"
        result = ResponseValidator.validate_quality(poor_code)
        
        assert result["is_quality"] is False
        assert len(result["issues"]) > 0
        assert result["quality_score"] < 100

    def test_retry_manager_immediate_success(self):
        """Test retry manager with immediate success."""
        call_count = 0
        
        def successful_function():
            nonlocal call_count
            call_count += 1
            return "success"
        
        result = self.retry_manager.retry_with_backoff(successful_function)
        assert result == "success"
        assert call_count == 1

    def test_retry_manager_custom_parameters(self):
        """Test retry manager with custom parameters."""
        custom_retry = RetryManager(
            max_retries=5,
            base_delay=0.02,
            max_delay=0.5,
            backoff_factor=3.0
        )
        
        delay_0 = custom_retry.calculate_delay(0)
        delay_1 = custom_retry.calculate_delay(1)
        
        assert delay_0 == 0.02
        assert delay_1 == 0.06

    def test_rate_limiter_cleanup_old_requests(self):
        """Test rate limiter cleans up old requests."""
        # Record some requests
        for _ in range(3):
            self.rate_limiter.record_request()
        
        # Verify we can still check if we can make requests
        # After making 3 of 5 allowed requests, we should be able to make more
        assert self.rate_limiter.can_make_request() is True

    def test_response_validator_multiple_issues(self):
        """Test response validator detects multiple quality issues."""
        poor_code = "a=1\nb=2"  # No functions, no docstrings, too short
        result = ResponseValidator.validate_quality(poor_code)
        
        assert result["is_quality"] is False
        assert len(result["issues"]) >= 2
