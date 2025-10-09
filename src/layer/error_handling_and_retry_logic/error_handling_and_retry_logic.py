"""
Error Handling and Retry Logic

Layer: LAYER-004-01-01-02
Requirement: Error Handling and Retry Logic

Implements retry logic, error handling, and response validation for AI providers.
"""

import time
import ast
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime
from collections import deque

# REQ-LAYER-004-01-01-02


class RetryManager:
    """
    AC-001: Implement exponential backoff retry logic
    
    Manages retry attempts with exponential backoff for failed API calls.
    """
    
    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        backoff_factor: float = 2.0
    ):
        """
        Initialize retry manager.
        
        Args:
            max_retries: Maximum number of retry attempts
            base_delay: Initial delay in seconds
            max_delay: Maximum delay between retries
            backoff_factor: Multiplier for exponential backoff
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
    
    def calculate_delay(self, attempt: int) -> float:
        """
        Calculate exponential backoff delay.
        
        Args:
            attempt: Current attempt number (0-indexed)
        
        Returns:
            Delay in seconds
        """
        delay = self.base_delay * (self.backoff_factor ** attempt)
        return min(delay, self.max_delay)
    
    def retry_with_backoff(
        self,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """
        Execute function with exponential backoff retry logic.
        
        Args:
            func: Function to execute
            *args: Positional arguments for func
            **kwargs: Keyword arguments for func
        
        Returns:
            Result from successful function call
        
        Raises:
            RuntimeError: If max retries exceeded
        """
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                
                if attempt < self.max_retries:
                    delay = self.calculate_delay(attempt)
                    time.sleep(delay)
                else:
                    raise RuntimeError(
                        f"Max retries ({self.max_retries}) exceeded"
                    ) from last_exception


class ErrorHandler:
    """
    AC-002: Handle API timeout errors gracefully
    
    Handles various API errors with appropriate recovery strategies.
    """
    
    @staticmethod
    def handle_timeout_error(error: Exception, context: str = "") -> Dict:
        """
        Handle API timeout errors.
        
        Args:
            error: The timeout exception
            context: Additional context about the error
        
        Returns:
            Dict with error details and recovery suggestion
        """
        return {
            "error_type": "timeout",
            "error_message": str(error),
            "context": context,
            "recovery_action": "retry",
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def handle_api_key_error(error: Exception) -> Dict:
        """
        Handle invalid API key errors.
        
        Args:
            error: The API key exception
        
        Returns:
            Dict with error details
        """
        return {
            "error_type": "invalid_api_key",
            "error_message": str(error),
            "recovery_action": "check_credentials",
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def handle_invalid_response(response: str) -> Dict:
        """
        Handle invalid API response errors.
        
        Args:
            response: The invalid response
        
        Returns:
            Dict with error details
        """
        return {
            "error_type": "invalid_response",
            "error_message": "API returned invalid or empty response",
            "response_preview": response[:100] if response else None,
            "recovery_action": "retry",
            "timestamp": datetime.now().isoformat()
        }


class RateLimitHandler:
    """
    AC-003: Handle rate limit errors with queueing
    
    Manages rate-limited API requests using a queue.
    """
    
    def __init__(self, max_requests_per_minute: int = 60):
        """
        Initialize rate limit handler.
        
        Args:
            max_requests_per_minute: Maximum requests allowed per minute
        """
        self.max_requests_per_minute = max_requests_per_minute
        self.request_queue = deque()
        self.request_timestamps = deque()
    
    def can_make_request(self) -> bool:
        """
        Check if a request can be made without exceeding rate limit.
        
        Returns:
            True if request can be made, False otherwise
        """
        now = time.time()
        cutoff = now - 60  # 60 seconds ago
        
        # Remove timestamps older than 1 minute
        while self.request_timestamps and self.request_timestamps[0] < cutoff:
            self.request_timestamps.popleft()
        
        return len(self.request_timestamps) < self.max_requests_per_minute
    
    def record_request(self):
        """Record that a request was made."""
        self.request_timestamps.append(time.time())
    
    def get_wait_time(self) -> float:
        """
        Calculate how long to wait before next request.
        
        Returns:
            Wait time in seconds
        """
        if self.can_make_request():
            return 0.0
        
        # Wait until the oldest request expires
        oldest = self.request_timestamps[0]
        wait_time = (oldest + 60) - time.time()
        return max(0.0, wait_time)
    
    def handle_rate_limit_error(self, error: Exception) -> Dict:
        """
        Handle rate limit error.
        
        Args:
            error: The rate limit exception
        
        Returns:
            Dict with error details and wait time
        """
        wait_time = self.get_wait_time()
        return {
            "error_type": "rate_limit",
            "error_message": str(error),
            "recovery_action": "wait_and_retry",
            "wait_time_seconds": wait_time,
            "timestamp": datetime.now().isoformat()
        }


class ResponseValidator:
    """
    AC-004: Validate AI API responses for code quality
    
    Validates that AI-generated code responses meet quality standards.
    """
    
    @staticmethod
    def validate_syntax(code: str) -> Dict:
        """
        Validate Python syntax of generated code.
        
        Args:
            code: Generated code string
        
        Returns:
            Dict with validation results
        """
        if not code or not code.strip():
            return {
                "is_valid": False,
                "error_type": "empty_code",
                "error_message": "Code is empty or whitespace",
                "timestamp": datetime.now().isoformat()
            }
        
        try:
            ast.parse(code)
            return {
                "is_valid": True,
                "error_type": None,
                "error_message": None,
                "timestamp": datetime.now().isoformat()
            }
        except SyntaxError as e:
            return {
                "is_valid": False,
                "error_type": "syntax_error",
                "error_message": str(e),
                "line_number": e.lineno,
                "timestamp": datetime.now().isoformat()
            }
    
    @staticmethod
    def validate_quality(code: str) -> Dict:
        """
        Validate code quality (basic checks).
        
        Args:
            code: Generated code string
        
        Returns:
            Dict with quality assessment
        """
        issues = []
        
        # Check for minimum length
        if len(code.strip()) < 10:
            issues.append("Code is too short")
        
        # Check for common quality indicators
        if "def " not in code and "class " not in code:
            issues.append("No functions or classes defined")
        
        # Check for docstrings
        if '"""' not in code and "'''" not in code:
            issues.append("No docstrings found")
        
        return {
            "is_quality": len(issues) == 0,
            "issues": issues,
            "quality_score": max(0, 100 - (len(issues) * 20)),
            "timestamp": datetime.now().isoformat()
        }
