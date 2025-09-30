from datetime import datetime
from typing import Dict, List, Optional
import time
import logging
import uuid
from dataclasses import dataclass
from enum import Enum


class CommandStatus(Enum):
    """Command execution status enumeration"""
    PENDING = "pending"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class PerformanceMetrics:
    """Performance tracking data structure"""
    operation_type: str
    start_time: float
    end_time: float
    duration_ms: float
    memory_usage_bytes: Optional[int] = None


class SecurityValidator:
    """Security validation for mobile command data"""
    
    @staticmethod
    def validate_user_id(user_id: str) -> bool:
        """Validate user ID format and security"""
        if not user_id or not isinstance(user_id, str):
            return False
        # Basic validation: alphanumeric and underscores only
        return user_id.replace('_', '').replace('-', '').isalnum()
    
    @staticmethod
    def sanitize_command_data(command_data: dict) -> dict:
        """Sanitize command data for security"""
        sanitized = {}
        allowed_keys = {
            'command_id', 'user_id', 'command_type', 'timestamp',
            'execution_context', 'parameters', 'status', 'metadata',
            'context', 'relationships', 'command'  # Added for context correlation
        }
        
        for key, value in command_data.items():
            if key in allowed_keys and isinstance(key, str):
                # Basic sanitization
                if isinstance(value, str):
                    sanitized[key] = value.strip()[:1000]  # Limit length
                else:
                    sanitized[key] = value
        
        return sanitized
    
    @staticmethod
    def generate_secure_command_id() -> str:
        """Generate cryptographically secure command ID"""
        return f"cmd_{uuid.uuid4().hex[:16]}"


class ContextIndex:
    """Advanced context indexing system for optimized queries"""
    
    def __init__(self):
        self._project_index = defaultdict(set)  # project -> command_ids
        self._system_index = defaultdict(set)   # system -> command_ids
        self._feature_index = defaultdict(set)  # feature -> command_ids
        self._layer_index = defaultdict(set)    # layer -> command_ids
        self._component_index = defaultdict(set) # component -> command_ids
        self._composite_index = {}  # context_hash -> command_ids
        self._lock = Lock()
    
    def add_command(self, command_id: str, context: dict) -> None:
        """Add command to context indexes"""
        with self._lock:
            if 'project' in context:
                self._project_index[context['project']].add(command_id)
            if 'system' in context:
                self._system_index[context['system']].add(command_id)
            if 'feature' in context:
                self._feature_index[context['feature']].add(command_id)
            if 'layer' in context:
                self._layer_index[context['layer']].add(command_id)
            if 'component' in context:
                self._component_index[context['component']].add(command_id)
            
            # Create composite index for multi-criteria queries
            context_hash = self._hash_context(context)
            if context_hash not in self._composite_index:
                self._composite_index[context_hash] = set()
            self._composite_index[context_hash].add(command_id)
    
    def remove_command(self, command_id: str, context: dict) -> None:
        """Remove command from context indexes"""
        with self._lock:
            if 'project' in context:
                self._project_index[context['project']].discard(command_id)
            if 'system' in context:
                self._system_index[context['system']].discard(command_id)
            if 'feature' in context:
                self._feature_index[context['feature']].discard(command_id)
            if 'layer' in context:
                self._layer_index[context['layer']].discard(command_id)
            if 'component' in context:
                self._component_index[context['component']].discard(command_id)
            
            context_hash = self._hash_context(context)
            if context_hash in self._composite_index:
                self._composite_index[context_hash].discard(command_id)
    
    def query_by_context(self, context_filter: dict) -> set:
        """Optimized context query using indexes"""
        with self._lock:
            if not context_filter:
                return set()
            
            # Try composite index first for exact matches
            context_hash = self._hash_context(context_filter)
            if context_hash in self._composite_index:
                return self._composite_index[context_hash].copy()
            
            # Fallback to individual index intersection
            result_sets = []
            
            if 'project' in context_filter:
                result_sets.append(self._project_index[context_filter['project']])
            if 'system' in context_filter:
                result_sets.append(self._system_index[context_filter['system']])
            if 'feature' in context_filter:
                result_sets.append(self._feature_index[context_filter['feature']])
            if 'layer' in context_filter:
                result_sets.append(self._layer_index[context_filter['layer']])
            if 'component' in context_filter:
                result_sets.append(self._component_index[context_filter['component']])
            
            if not result_sets:
                return set()
            
            # Intersection of all matching sets
            result = result_sets[0].copy()
            for result_set in result_sets[1:]:
                result.intersection_update(result_set)
            
            return result
    
    def _hash_context(self, context: dict) -> str:
        """Create consistent hash for context dict"""
        sorted_items = sorted(context.items())
        context_str = json.dumps(sorted_items, sort_keys=True)
        return hashlib.md5(context_str.encode()).hexdigest()
    
    def get_stats(self) -> dict:
        """Get indexing statistics"""
        with self._lock:
            return {
                'project_keys': len(self._project_index),
                'system_keys': len(self._system_index),
                'feature_keys': len(self._feature_index),
                'layer_keys': len(self._layer_index),
                'component_keys': len(self._component_index),
                'composite_keys': len(self._composite_index)
            }


class QueryCache:
    """Intelligent caching system for frequently accessed queries"""
    
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 300):
        self._cache = {}
        self._access_times = {}
        self._access_counts = defaultdict(int)
        self._max_size = max_size
        self._ttl_seconds = ttl_seconds
        self._lock = Lock()
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached value with TTL and access tracking"""
        with self._lock:
            if key not in self._cache:
                return None
            
            # Check TTL
            if time.time() - self._access_times[key] > self._ttl_seconds:
                self._evict(key)
                return None
            
            # Update access tracking
            self._access_times[key] = time.time()
            self._access_counts[key] += 1
            
            return self._cache[key]
    
    def set(self, key: str, value: Any) -> None:
        """Set cached value with intelligent eviction"""
        with self._lock:
            current_time = time.time()
            
            # Evict if at capacity
            if len(self._cache) >= self._max_size and key not in self._cache:
                self._evict_lru()
            
            self._cache[key] = value
            self._access_times[key] = current_time
            self._access_counts[key] += 1
    
    def _evict(self, key: str) -> None:
        """Evict specific key"""
        self._cache.pop(key, None)
        self._access_times.pop(key, None)
        self._access_counts.pop(key, None)
    
    def _evict_lru(self) -> None:
        """Evict least recently used item"""
        if not self._access_times:
            return
        
        lru_key = min(self._access_times.keys(), 
                     key=lambda k: self._access_times[k])
        self._evict(lru_key)
    
    def clear(self) -> None:
        """Clear all cached data"""
        with self._lock:
            self._cache.clear()
            self._access_times.clear()
            self._access_counts.clear()
    
    def get_stats(self) -> dict:
        """Get cache statistics"""
        with self._lock:
            return {
                'size': len(self._cache),
                'max_size': self._max_size,
                'hit_rate': sum(self._access_counts.values()) / max(len(self._cache), 1),
                'avg_access_count': sum(self._access_counts.values()) / max(len(self._access_counts), 1)
            }


class MobileCommandHistoryRepository:
    """
    Enhanced repository for mobile command history storage and retrieval
    
    Features:
    - Advanced performance monitoring
    - Security validation and sanitization
    - Comprehensive error handling
    - Logging and audit trails
    - Context Engine integration preparation
    """
    
    def __init__(self, enable_logging: bool = True,
                 max_commands_per_user: int = 10000):
        """
        Initialize repository with enhanced configuration
        
        Args:
            enable_logging: Enable comprehensive logging
            max_commands_per_user: Maximum commands per user (security limit)
        """
        self._commands: Dict[str, dict] = {}
        self._user_commands: Dict[str, List[str]] = {}
        self._performance_metrics: List[PerformanceMetrics] = []
        self._max_commands_per_user = max_commands_per_user
        
        # Initialize logging
        if enable_logging:
            logging.basicConfig(level=logging.INFO)
            self._logger = logging.getLogger(__name__)
        else:
            self._logger = logging.getLogger(__name__)
            self._logger.disabled = True
            
        # Security validator
        self._security = SecurityValidator()
        
        # Performance tracking
        self._total_operations = 0
        self._failed_operations = 0
        
        self._logger.info("MobileCommandHistoryRepository initialized")
    
    def _record_performance(self, operation_type: str,
                            start_time: float) -> float:
        """Record performance metrics for operation"""
        end_time = time.time()
        duration_ms = (end_time - start_time) * 1000
        
        metrics = PerformanceMetrics(
            operation_type=operation_type,
            start_time=start_time,
            end_time=end_time,
            duration_ms=duration_ms
        )
        
        self._performance_metrics.append(metrics)
        
        # Keep only last 1000 metrics to prevent memory issues
        if len(self._performance_metrics) > 1000:
            self._performance_metrics = self._performance_metrics[-1000:]
            
        return duration_ms
    
    def _validate_input(self, **kwargs) -> None:
        """Comprehensive input validation with detailed error messages"""
        for param_name, param_value in kwargs.items():
            if param_value is None:
                raise ValueError(f"Parameter '{param_name}' cannot be None")
            
            if param_name == 'user_id':
                if not self._security.validate_user_id(param_value):
                    raise ValueError(f"Invalid user_id format: {param_value}")
            
            if param_name == 'command_data':
                if not isinstance(param_value, dict):
                    raise TypeError("command_data must be a dictionary")
                if not param_value:
                    raise ValueError("command_data cannot be empty")
    
    def _check_user_limits(self, user_id: str) -> None:
        """Check if user has exceeded command limits"""
        if user_id in self._user_commands:
            current_count = len(self._user_commands[user_id])
            if current_count >= self._max_commands_per_user:
                raise ValueError(
                    f"User {user_id} has exceeded maximum commands limit "
                    f"({current_count}/{self._max_commands_per_user})"
                )
    
    def store_command(self, command_data: dict) -> str:
        """
        Store a mobile command with enhanced security and performance tracking
        
        Args:
            command_data: Dictionary containing command information
            
        Returns:
            str: Unique command identifier
            
        Raises:
            ValueError: If command_data is invalid or user limits exceeded
            TypeError: If command_data is not a dictionary
        """
        start_time = time.time()
        self._total_operations += 1
        
        try:
            # Comprehensive input validation
            self._validate_input(command_data=command_data)
            
            # Security sanitization
            sanitized_data = self._security.sanitize_command_data(command_data)
            
            # Extract or generate secure command_id
            command_id = sanitized_data.get("command_id")
            if not command_id:
                command_id = self._security.generate_secure_command_id()
            
            # Validate user_id and check limits
            user_id = sanitized_data.get("user_id", "unknown")
            if user_id != "unknown":
                self._validate_input(user_id=user_id)
                self._check_user_limits(user_id)
            
            # Enhanced command metadata
            stored_command = {
                **sanitized_data,
                "command_id": command_id,
                "stored_at": datetime.now().isoformat(),
                "status": sanitized_data.get(
                    "status", CommandStatus.PENDING.value),
                "version": "1.0",
                "security_validated": True,
                "context_ready": True,  # For Context Engine integration
                "storage_time_ms": 0  # Will be updated below
            }
            
            # Store in main commands dict
            self._commands[command_id] = stored_command
            
            # Add to user's command list with initialization if needed
            if user_id not in self._user_commands:
                self._user_commands[user_id] = []
            self._user_commands[user_id].append(command_id)
            
            # REFACTOR: Add to context index for optimized queries
            if self._enable_optimizations and 'context' in stored_command:
                try:
                    self._context_index.add_command(command_id, stored_command['context'])
                except Exception as e:
                    self._logger.warning(f"Failed to index context for {command_id}: {e}")
            
            # Record performance metrics
            duration_ms = self._record_performance("store_command", start_time)
            self._commands[command_id]["storage_time_ms"] = duration_ms
            
            # Audit logging
            self._logger.info(
                f"Command stored: {command_id} for user {user_id} "
                f"in {duration_ms:.2f}ms"
            )
            
            return command_id
            
        except Exception as e:
            self._failed_operations += 1
            self._logger.error(f"Failed to store command: {str(e)}")
            raise
    
    def get_command_history(self, user_id: str,
                            limit: Optional[int] = None,
                            status_filter: Optional[CommandStatus] = None
                            ) -> List[dict]:
        """
        Retrieve command history with enhanced filtering and security
        
        Args:
            user_id: User identifier
            limit: Maximum number of commands to return
            status_filter: Filter by command status
            
        Returns:
            List[dict]: List of command records
            
        Raises:
            ValueError: If user_id is invalid
        """
        start_time = time.time()
        self._total_operations += 1
        
        try:
            # Input validation
            self._validate_input(user_id=user_id)
            
            if user_id not in self._user_commands:
                self._logger.info(f"No commands found for user: {user_id}")
                return []
            
            # Get all commands for the user
            user_command_ids = self._user_commands[user_id]
            command_history = []
            
            for command_id in user_command_ids:
                if command_id in self._commands:
                    command = self._commands[command_id].copy()
                    
                    # Apply status filter if specified
                    if status_filter:
                        if command.get("status") != status_filter.value:
                            continue
                    
                    command_history.append(command)
            
            # Sort by timestamp (most recent first)
            command_history.sort(
                key=lambda x: x.get("timestamp", x.get("stored_at", "")),
                reverse=True
            )
            
            # Apply limit if specified
            if limit and limit > 0:
                command_history = command_history[:limit]
            
            # Record performance and add metadata
            duration_ms = self._record_performance("get_command_history",
                                                   start_time)
            
            # Add retrieval performance metadata to each command
            for cmd in command_history:
                cmd["retrieval_time_ms"] = duration_ms
                cmd["retrieved_at"] = datetime.now().isoformat()
            
            self._logger.info(
                f"Retrieved {len(command_history)} commands for {user_id} "
                f"in {duration_ms:.2f}ms"
            )
            
            return command_history
            
        except Exception as e:
            self._failed_operations += 1
            self._logger.error(f"Failed to retrieve command history: {str(e)}")
            raise
    
    def command_exists(self, command_id: str) -> bool:
        """
        Check if a command exists with enhanced validation
        
        Args:
            command_id: Command identifier to check
            
        Returns:
            bool: True if command exists
            
        Raises:
            ValueError: If command_id is invalid
        """
        start_time = time.time()
        self._total_operations += 1
        
        try:
            if not command_id or not isinstance(command_id, str):
                raise ValueError("command_id must be a non-empty string")
            
            exists = command_id in self._commands
            
            # Record performance
            self._record_performance("command_exists", start_time)
            
            return exists
            
        except Exception as e:
            self._failed_operations += 1
            self._logger.error(f"Failed to check command existence: {str(e)}")
            raise
    
    def delete_command(self, command_id: str) -> bool:
        """
        Delete a command with comprehensive cleanup and audit trail
        
        Args:
            command_id: Command identifier to delete
            
        Returns:
            bool: True if command was deleted, False if not found
            
        Raises:
            ValueError: If command_id is invalid
        """
        start_time = time.time()
        self._total_operations += 1
        
        try:
            if not command_id or not isinstance(command_id, str):
                raise ValueError("command_id must be a non-empty string")
            
            if command_id not in self._commands:
                self._logger.info(f"Command not found: {command_id}")
                return False
            
            # Get command info for audit trail
            command = self._commands[command_id]
            user_id = command.get("user_id", "unknown")
            
            # Remove from main storage
            del self._commands[command_id]
            
            # Remove from user's command list with cleanup
            if (user_id in self._user_commands and
                    command_id in self._user_commands[user_id]):
                self._user_commands[user_id].remove(command_id)
                
                # Clean up empty user lists
                if not self._user_commands[user_id]:
                    del self._user_commands[user_id]
            
            # Record performance
            duration_ms = self._record_performance("delete_command",
                                                   start_time)
            
            # Audit logging
            self._logger.info(
                f"Command deleted: {command_id} for user {user_id} "
                f"in {duration_ms:.2f}ms"
            )
            
            return True
            
        except Exception as e:
            self._failed_operations += 1
            self._logger.error(f"Failed to delete command: {str(e)}")
            raise
    
    def get_command(self, command_id: str) -> dict:
        """
        Retrieve a single command by ID
        
        Args:
            command_id: Command identifier
            
        Returns:
            dict: Command data
            
        Raises:
            ValueError: If command_id is invalid or command not found
        """
        start_time = time.time()
        self._total_operations += 1
        
        try:
            if not command_id or not isinstance(command_id, str):
                raise ValueError("Command ID must be a non-empty string")
            
            if command_id not in self._commands:
                raise ValueError(f"Command not found: {command_id}")
            
            command = self._commands[command_id].copy()
            
            duration_ms = self._record_performance("get_command", start_time)
            command["retrieval_time_ms"] = duration_ms
            
            self._logger.info(
                f"Command retrieved: {command_id} in {duration_ms:.2f}ms"
            )
            
            return command
            
        except Exception as e:
            self._failed_operations += 1
            self._logger.error(f"Failed to get command: {str(e)}")
            raise
    
    def get_command_count(self, user_id: str) -> int:
        """
        Get total command count with enhanced validation
        
        Args:
            user_id: User identifier
            
        Returns:
            int: Number of commands for the user
            
        Raises:
            ValueError: If user_id is invalid
        """
        start_time = time.time()
        self._total_operations += 1
        
        try:
            # Input validation
            self._validate_input(user_id=user_id)
            
            count = len(self._user_commands.get(user_id, []))
            
            # Record performance
            self._record_performance("get_command_count", start_time)
            
            return count
            
        except Exception as e:
            self._failed_operations += 1
            self._logger.error(f"Failed to get command count: {str(e)}")
            raise
    
    def get_performance_metrics(self) -> Dict[str, float]:
        """
        Get comprehensive performance statistics
        
        Returns:
            Dict[str, float]: Performance metrics
        """
        if not self._performance_metrics:
            return {}
        
        metrics_by_operation = {}
        for metric in self._performance_metrics:
            op_type = metric.operation_type
            if op_type not in metrics_by_operation:
                metrics_by_operation[op_type] = []
            metrics_by_operation[op_type].append(metric.duration_ms)
        
        summary = {}
        for op_type, durations in metrics_by_operation.items():
            summary[f"{op_type}_avg_ms"] = sum(durations) / len(durations)
            summary[f"{op_type}_max_ms"] = max(durations)
            summary[f"{op_type}_min_ms"] = min(durations)
            summary[f"{op_type}_count"] = len(durations)
        
        summary["total_operations"] = self._total_operations
        summary["failed_operations"] = self._failed_operations
        summary["success_rate"] = (
            (self._total_operations - self._failed_operations) /
            max(self._total_operations, 1) * 100
        )
        
        return summary
    
    def get_repository_stats(self) -> Dict[str, int]:
        """
        Get repository statistics for monitoring
        
        Returns:
            Dict[str, int]: Repository statistics
        """
        return {
            "total_commands": len(self._commands),
            "total_users": len(self._user_commands),
            "total_operations": self._total_operations,
            "failed_operations": self._failed_operations,
            "performance_metrics_count": len(self._performance_metrics)
        }
    
    # Context Correlation Methods - TDD Iteration 2
    
    def store_command_with_context(self, command_data: dict) -> str:
        """
        Store a mobile command with hierarchical context metadata
        
        Args:
            command_data: Dictionary containing command and context information
            
        Returns:
            str: Unique command identifier
            
        Raises:
            ValueError: If command_data or context is invalid
        """
        start_time = time.time()
        self._total_operations += 1
        
        try:
            # Validate input
            self._validate_input(command_data=command_data)
            
            # Validate context structure if provided
            context = command_data.get("context", {})
            if context and not isinstance(context, dict):
                raise ValueError("Context must be a dictionary")
            
            # Store command using existing store_command method
            command_id = self.store_command(command_data)
            
            # If context was provided, it's already stored with the command
            duration_ms = self._record_performance(
                "store_command_with_context", start_time)
            
            self._logger.info(
                f"Command with context stored: {command_id} "
                f"in {duration_ms:.2f}ms"
            )
            
            return command_id
            
        except Exception as e:
            self._failed_operations += 1
            self._logger.error(f"Failed to store command with context: {str(e)}")
            raise
    
    def get_commands_by_context(self, context_filter: dict) -> list:
        """
        Query commands by context criteria with REFACTOR optimizations
        
        Args:
            context_filter: Dictionary with context criteria to filter by
            
        Returns:
            list: List of commands matching context criteria
            
        Raises:
            ValueError: If context_filter is invalid
        """
        start_time = time.time()
        self._total_operations += 1
        
        try:
            if not isinstance(context_filter, dict):
                raise ValueError("Context filter must be a dictionary")
            
            if not context_filter:
                raise ValueError("Context filter cannot be empty")
            
            # REFACTOR: Try cache first
            cache_key = f"context_query_{hash(frozenset(context_filter.items()))}"
            if self._enable_optimizations:
                cached_result = self._query_cache.get(cache_key)
                if cached_result is not None:
                    self._optimization_metrics['cache_hits'] += 1
                    duration_ms = self._record_performance("get_commands_by_context_cached", start_time)
                    
                    # Add cache metadata to results
                    for cmd in cached_result:
                        cmd["query_time_ms"] = duration_ms
                        cmd["context_query"] = context_filter
                        cmd["from_cache"] = True
                    
                    return cached_result
                else:
                    self._optimization_metrics['cache_misses'] += 1
            
            matching_commands = []
            
            # REFACTOR: Use context index for optimized search
            if self._enable_optimizations and self._context_index:
                self._optimization_metrics['index_queries'] += 1
                matching_command_ids = self._context_index.query_by_context(context_filter)
                
                for command_id in matching_command_ids:
                    if command_id in self._commands:
                        command_copy = self._commands[command_id].copy()
                        matching_commands.append(command_copy)
            else:
                # Fallback: Search through all commands (original method)
                for command_id, command in self._commands.items():
                    command_context = command.get("context", {})
                    
                    # Check if command matches all filter criteria
                    matches = True
                    for filter_key, filter_value in context_filter.items():
                        if (filter_key not in command_context or 
                            command_context[filter_key] != filter_value):
                            matches = False
                            break
                    
                    if matches:
                        command_copy = command.copy()
                        matching_commands.append(command_copy)
            
            # Sort by timestamp (most recent first)
            matching_commands.sort(
                key=lambda x: x.get("timestamp", x.get("stored_at", "")),
                reverse=True
            )
            
            duration_ms = self._record_performance(
                "get_commands_by_context", start_time)
            
            # Add query metadata
            for cmd in matching_commands:
                cmd["query_time_ms"] = duration_ms
                cmd["context_query"] = context_filter
            
            self._logger.info(
                f"Found {len(matching_commands)} commands matching context "
                f"in {duration_ms:.2f}ms"
            )
            
            return matching_commands
            
        except Exception as e:
            self._failed_operations += 1
            self._logger.error(f"Failed to query commands by context: {str(e)}")
            raise
    
    def get_context_hierarchy(self, user_id: str) -> dict:
        """
        Get hierarchical context structure for user's commands
        
        Args:
            user_id: User identifier
            
        Returns:
            dict: Hierarchical context structure
            
        Raises:
            ValueError: If user_id is invalid
        """
        start_time = time.time()
        self._total_operations += 1
        
        try:
            self._validate_input(user_id=user_id)
            
            if user_id not in self._user_commands:
                return {"user_id": user_id, "hierarchy": {}, "command_count": 0}
            
            hierarchy = {}
            command_count = 0
            
            # Build hierarchy from user's commands
            for command_id in self._user_commands[user_id]:
                if command_id in self._commands:
                    command = self._commands[command_id]
                    context = command.get("context", {})
                    command_count += 1
                    
                    # Build nested hierarchy structure
                    current_level = hierarchy
                    for level in ["project", "system", "feature", "layer", "component"]:
                        if level in context:
                            level_value = context[level]
                            if level_value not in current_level:
                                current_level[level_value] = {}
                            current_level = current_level[level_value]
            
            duration_ms = self._record_performance(
                "get_context_hierarchy", start_time)
            
            result = {
                "user_id": user_id,
                "hierarchy": hierarchy,
                "command_count": command_count,
                "query_time_ms": duration_ms,
                "generated_at": datetime.now().isoformat()
            }
            
            self._logger.info(
                f"Generated context hierarchy for {user_id} "
                f"in {duration_ms:.2f}ms"
            )
            
            return result
            
        except Exception as e:
            self._failed_operations += 1
            self._logger.error(f"Failed to get context hierarchy: {str(e)}")
            raise
    
    def get_commands_by_context_path(self, context_path: str) -> list:
        """
        Query commands by hierarchical context path
        
        Args:
            context_path: Hierarchical path (e.g., "PROJECT-003/system/feature")
            
        Returns:
            list: List of commands matching the context path
            
        Raises:
            ValueError: If context_path is invalid
        """
        start_time = time.time()
        self._total_operations += 1
        
        try:
            if not context_path or not isinstance(context_path, str):
                raise ValueError("Context path must be a non-empty string")
            
            # Parse the hierarchical path
            path_parts = context_path.split("/")
            if len(path_parts) < 1:
                raise ValueError("Context path must contain at least one level")
            
            # Map path parts to context levels
            context_levels = ["project", "system", "feature", "layer", "component"]
            context_filter = {}
            
            for i, part in enumerate(path_parts):
                if i < len(context_levels):
                    context_filter[context_levels[i]] = part
            
            # Use existing context filtering
            matching_commands = self.get_commands_by_context(context_filter)
            
            duration_ms = self._record_performance(
                "get_commands_by_context_path", start_time)
            
            # Add path query metadata
            for cmd in matching_commands:
                cmd["context_path"] = context_path
                cmd["path_query_time_ms"] = duration_ms
            
            self._logger.info(
                f"Found {len(matching_commands)} commands for path '{context_path}' "
                f"in {duration_ms:.2f}ms"
            )
            
            return matching_commands
            
        except Exception as e:
            self._failed_operations += 1
            self._logger.error(f"Failed to query by context path: {str(e)}")
            raise
    
    def get_context_statistics(self, context_filter: dict) -> dict:
        """
        Get statistics for commands within context
        
        Args:
            context_filter: Dictionary with context criteria
            
        Returns:
            dict: Statistics for matching commands
            
        Raises:
            ValueError: If context_filter is invalid
        """
        start_time = time.time()
        self._total_operations += 1
        
        try:
            if not isinstance(context_filter, dict):
                raise ValueError("Context filter must be a dictionary")
            
            # Get matching commands
            matching_commands = self.get_commands_by_context(context_filter)
            
            # Calculate statistics
            stats = {
                "context_filter": context_filter,
                "total_commands": len(matching_commands),
                "users": set(),
                "command_types": {},
                "status_distribution": {},
                "time_range": {"earliest": None, "latest": None}
            }
            
            for command in matching_commands:
                # Track unique users
                user_id = command.get("user_id", "unknown")
                stats["users"].add(user_id)
                
                # Track command types
                cmd_type = command.get("command_type", "unknown")
                stats["command_types"][cmd_type] = stats["command_types"].get(cmd_type, 0) + 1
                
                # Track status distribution
                status = command.get("status", "unknown")
                stats["status_distribution"][status] = stats["status_distribution"].get(status, 0) + 1
                
                # Track time range
                timestamp = command.get("timestamp", command.get("stored_at"))
                if timestamp:
                    if stats["time_range"]["earliest"] is None or timestamp < stats["time_range"]["earliest"]:
                        stats["time_range"]["earliest"] = timestamp
                    if stats["time_range"]["latest"] is None or timestamp > stats["time_range"]["latest"]:
                        stats["time_range"]["latest"] = timestamp
            
            # Convert set to count
            stats["unique_users"] = len(stats["users"])
            del stats["users"]  # Remove set (not JSON serializable)
            
            duration_ms = self._record_performance(
                "get_context_statistics", start_time)
            
            stats["query_time_ms"] = duration_ms
            stats["generated_at"] = datetime.now().isoformat()
            
            self._logger.info(
                f"Generated context statistics for {stats['total_commands']} commands "
                f"in {duration_ms:.2f}ms"
            )
            
            return stats
            
        except Exception as e:
            self._failed_operations += 1
            self._logger.error(f"Failed to get context statistics: {str(e)}")
            raise
    
    def get_command_relationships(self, command_id: str) -> dict:
        """
        Get command relationships (parent, children, dependencies)
        
        Args:
            command_id: Command identifier
            
        Returns:
            dict: Command relationships information
            
        Raises:
            ValueError: If command_id is invalid or command not found
        """
        start_time = time.time()
        self._total_operations += 1
        
        try:
            if not command_id or not isinstance(command_id, str):
                raise ValueError("Command ID must be a non-empty string")
            
            if command_id not in self._commands:
                raise ValueError(f"Command not found: {command_id}")
            
            command = self._commands[command_id]
            relationships = command.get("relationships", {})
            
            # Build relationships structure
            result = {
                "command_id": command_id,
                "parent_command": relationships.get("parent_command"),
                "child_commands": relationships.get("child_commands", []),
                "dependency_commands": relationships.get("dependency_commands", []),
                "context": command.get("context", {}),
                "command_type": command.get("command_type", "unknown")
            }
            
            duration_ms = self._record_performance(
                "get_command_relationships", start_time)
            
            result["query_time_ms"] = duration_ms
            result["generated_at"] = datetime.now().isoformat()
            
            self._logger.info(
                f"Retrieved relationships for {command_id} "
                f"in {duration_ms:.2f}ms"
            )
            
            return result
            
        except Exception as e:
            self._failed_operations += 1
            self._logger.error(f"Failed to get command relationships: {str(e)}")
            raise
    
    def get_commands_by_hierarchy(self, hierarchy_filter: dict) -> list:
        """
        Query commands by hierarchical context structure
        
        Args:
            hierarchy_filter: Dictionary with hierarchical context criteria
            
        Returns:
            list: List of commands matching hierarchical criteria
            
        Raises:
            ValueError: If hierarchy_filter is invalid
        """
        start_time = time.time()
        self._total_operations += 1
        
        try:
            if not isinstance(hierarchy_filter, dict):
                raise ValueError("Hierarchy filter must be a dictionary")
            
            if not hierarchy_filter:
                raise ValueError("Hierarchy filter cannot be empty")
            
            # Use existing context filtering (hierarchy is part of context)
            matching_commands = self.get_commands_by_context(hierarchy_filter)
            
            duration_ms = self._record_performance(
                "get_commands_by_hierarchy", start_time)
            
            # Add hierarchy query metadata
            for cmd in matching_commands:
                cmd["hierarchy_filter"] = hierarchy_filter
                cmd["hierarchy_query_time_ms"] = duration_ms
            
            self._logger.info(
                f"Found {len(matching_commands)} commands by hierarchy "
                f"in {duration_ms:.2f}ms"
            )
            
            return matching_commands
            
        except Exception as e:
            self._failed_operations += 1
            self._logger.error(f"Failed to query by hierarchy: {str(e)}")
            raise
    
    # REFACTOR Phase: Batch Operations
    def batch_store_commands_with_context(self, commands_data: List[dict]) -> List[str]:
        """
        REFACTOR: Batch store multiple commands with context for improved performance
        
        Args:
            commands_data: List of command data dictionaries
            
        Returns:
            List[str]: List of generated command IDs
            
        Raises:
            ValueError: If commands_data is invalid
        """
        start_time = time.time()
        self._total_operations += 1
        
        if not self._enable_optimizations:
            # Fallback to individual operations
            return [self.store_command_with_context(cmd_data) for cmd_data in commands_data]
        
        try:
            if not isinstance(commands_data, list):
                raise ValueError("Commands data must be a list")
            
            if not commands_data:
                raise ValueError("Commands data cannot be empty")
            
            self._optimization_metrics['batch_operations'] += 1
            command_ids = []
            
            # Batch validation
            for i, command_data in enumerate(commands_data):
                self._validate_input(command_data=command_data)
            
            # Batch processing
            for command_data in commands_data:
                # Security sanitization
                sanitized_data = self._security.sanitize_command_data(command_data)
                
                # Generate command ID
                command_id = sanitized_data.get("command_id")
                if not command_id:
                    command_id = self._security.generate_secure_command_id()
                
                # Validate user limits
                user_id = sanitized_data.get("user_id", "unknown")
                if user_id != "unknown":
                    self._validate_input(user_id=user_id)
                    self._check_user_limits(user_id)
                
                # Create stored command
                stored_command = {
                    **sanitized_data,
                    "command_id": command_id,
                    "stored_at": datetime.now().isoformat(),
                    "status": sanitized_data.get("status", CommandStatus.PENDING.value),
                    "version": "1.0",
                    "security_validated": True,
                    "context_ready": True,
                    "batch_processed": True
                }
                
                # Store command
                self._commands[command_id] = stored_command
                
                # Update user commands
                if user_id not in self._user_commands:
                    self._user_commands[user_id] = []
                self._user_commands[user_id].append(command_id)
                
                # Add to context index
                if 'context' in stored_command:
                    try:
                        self._context_index.add_command(command_id, stored_command['context'])
                    except Exception as e:
                        self._logger.warning(f"Failed to index batch context: {e}")
                
                command_ids.append(command_id)
            
            duration_ms = self._record_performance("batch_store_commands_with_context", start_time)
            
            self._logger.info(
                f"Batch stored {len(command_ids)} commands in {duration_ms:.2f}ms "
                f"({duration_ms/len(command_ids):.2f}ms per command)"
            )
            
            return command_ids
            
        except Exception as e:
            self._failed_operations += 1
            self._logger.error(f"Failed to batch store commands: {str(e)}")
            raise
    
    def batch_get_commands_by_contexts(self, context_filters: List[dict]) -> Dict[str, list]:
        """
        REFACTOR: Batch query multiple context filters efficiently
        
        Args:
            context_filters: List of context filter dictionaries
            
        Returns:
            Dictionary mapping filter hash to matching commands
            
        Raises:
            ValueError: If context_filters is invalid
        """
        start_time = time.time()
        self._total_operations += 1
        
        if not self._enable_optimizations:
            # Fallback to individual operations
            results = {}
            for i, context_filter in enumerate(context_filters):
                results[f"filter_{i}"] = self.get_commands_by_context(context_filter)
            return results
        
        try:
            if not isinstance(context_filters, list):
                raise ValueError("Context filters must be a list")
            
            if not context_filters:
                raise ValueError("Context filters cannot be empty")
            
            self._optimization_metrics['batch_operations'] += 1
            results = {}
            
            for context_filter in context_filters:
                if not isinstance(context_filter, dict):
                    raise ValueError("Each context filter must be a dictionary")
                
                filter_hash = hash(frozenset(context_filter.items()))
                filter_key = f"filter_{filter_hash}"
                
                # Use optimized individual query method
                matching_commands = self.get_commands_by_context(context_filter)
                results[filter_key] = matching_commands
            
            duration_ms = self._record_performance("batch_get_commands_by_contexts", start_time)
            
            self._logger.info(
                f"Batch queried {len(context_filters)} context filters in {duration_ms:.2f}ms"
            )
            
            return results
            
        except Exception as e:
            self._failed_operations += 1
            self._logger.error(f"Failed to batch query contexts: {str(e)}")
            raise
    
    # REFACTOR Phase: Memory Optimization
    def optimize_memory_usage(self) -> dict:
        """
        REFACTOR: Optimize memory usage by cleaning up stale data and compacting structures
        
        Returns:
            dict: Memory optimization results
        """
        start_time = time.time()
        
        if not self._enable_optimizations:
            return {"status": "optimizations_disabled"}
        
        try:
            initial_stats = self.get_optimization_metrics()
            
            # Clean query cache
            old_cache_size = len(self._query_cache._cache) if self._query_cache else 0
            if self._query_cache:
                self._query_cache.clear()
            
            # Clean performance metrics (keep recent)
            for metric_name in self._performance_metrics:
                if len(self._performance_metrics[metric_name]) > 1000:
                    # Keep only recent 100 entries
                    self._performance_metrics[metric_name] = \
                        self._performance_metrics[metric_name][-100:]
            
            duration_ms = self._record_performance("optimize_memory_usage", start_time)
            
            optimization_results = {
                "status": "completed",
                "cache_entries_cleared": old_cache_size,
                "metrics_entries_trimmed": sum(
                    max(0, len(entries) - 100) 
                    for entries in initial_stats.get('performance_metrics', {}).values()
                ),
                "optimization_time_ms": duration_ms,
                "timestamp": datetime.now().isoformat()
            }
            
            self._logger.info(
                f"Memory optimization completed in {duration_ms:.2f}ms"
            )
            
            return optimization_results
            
        except Exception as e:
            self._logger.error(f"Failed to optimize memory: {str(e)}")
            return {"status": "failed", "error": str(e)}
    
    def get_optimization_metrics(self) -> dict:
        """
        REFACTOR: Get comprehensive optimization metrics
        
        Returns:
            dict: Detailed optimization metrics
        """
        if not self._enable_optimizations:
            return {"status": "optimizations_disabled"}
        
        try:
            base_metrics = {
                "optimization_metrics": self._optimization_metrics.copy(),
                "total_operations": self._total_operations,
                "failed_operations": self._failed_operations,
                "success_rate": (
                    (self._total_operations - self._failed_operations) / 
                    max(self._total_operations, 1)
                ) * 100
            }
            
            if self._context_index:
                base_metrics["context_index_stats"] = self._context_index.get_stats()
            
            if self._query_cache:
                base_metrics["query_cache_stats"] = self._query_cache.get_stats()
            
            # Performance metrics summary
            performance_summary = {}
            for metric_name, times in self._performance_metrics.items():
                if times:
                    performance_summary[metric_name] = {
                        "count": len(times),
                        "avg_ms": sum(times) / len(times),
                        "min_ms": min(times),
                        "max_ms": max(times)
                    }
            
            base_metrics["performance_metrics"] = performance_summary
            
            return base_metrics
            
        except Exception as e:
            self._logger.error(f"Failed to get optimization metrics: {str(e)}")
            return {"status": "error", "error": str(e)}
