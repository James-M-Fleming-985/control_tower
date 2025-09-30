import time
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from collections import defaultdict
import threading
import json
import hashlib


class ContextEngineRepository:
    """Advanced Context Engine Repository with enhanced performance and security"""
    
    def __init__(self):
        """Initialize the Context Engine Repository with advanced features"""
        self._context_states = {}
        self._user_contexts = defaultdict(dict)
        self._conflict_history = []
        self._context_cache = {}
        self._context_analytics = defaultdict(list)
        # Enhanced features (simplified inline implementation)
        self._sync_stats = defaultdict(int)
        self._conflict_resolution_strategies = ['remote_preferred', 'local_preferred', 'merged', 'timestamp_based']
        
        # Thread safety
        self._context_lock = threading.RLock()
        
        # Logging setup
        self._logger = logging.getLogger(__name__)
        self._performance_metrics = defaultdict(list)
        self._total_operations = 0
        
        # Configure structured logging
        if not self._logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s [%(levelname)8s] %(name)s: %(message)s'
            )
            handler.setFormatter(formatter)
            self._logger.addHandler(handler)
            self._logger.setLevel(logging.INFO)
        
        self._logger.info("Enhanced ContextEngineRepository initialized")
    
    def _record_performance(self, operation: str, start_time: float) -> float:
        """Record performance metrics for operations"""
        duration = (time.time() - start_time) * 1000  # Convert to ms
        if operation not in self._performance_metrics:
            self._performance_metrics[operation] = []
        self._performance_metrics[operation].append(duration)
        return duration
    
    def _validate_input(self, **kwargs) -> None:
        """Validate input parameters"""
        for key, value in kwargs.items():
            if value is None:
                raise ValueError(f"Parameter '{key}' cannot be None")
            if key == 'user_id' and (not isinstance(value, str) or not value.strip()):
                raise ValueError("user_id must be a non-empty string")
            if key == 'context_data' and not isinstance(value, dict):
                raise ValueError("context_data must be a dictionary")
    
    def sync_context_state(self, context_data: dict, 
                          priority: str = 'normal') -> dict:
        """
        Enhanced context state synchronization with advanced features
        
        Args:
            context_data: Dictionary containing context state information
            priority: Sync priority ('high', 'normal', 'low')
            
        Returns:
            dict: Synchronization result with metadata
            
        Raises:
            ValueError: If context_data is invalid
        """
        start_time = time.time()
        self._total_operations += 1
        
        with self._context_lock:
            try:
                # Enhanced validation
                self._validate_input(context_data=context_data)
                
                required_fields = ['user_id', 'context_state']
                for field in required_fields:
                    if field not in context_data:
                        raise ValueError(f"Required field missing: {field}")
                
                user_id = context_data['user_id']
                self._validate_input(user_id=user_id)
                
                # Generate enhanced sync metadata
                sync_id = f"sync_{uuid.uuid4().hex[:16]}"
                sync_timestamp = datetime.now().isoformat()
                
                # Advanced context entry with analytics
                context_entry = {
                    'sync_id': sync_id,
                    'user_id': user_id,
                    'context_state': context_data['context_state'],
                    'synchronized_at': sync_timestamp,
                    'version': len(self._user_contexts[user_id]) + 1,
                    'priority': priority,
                    'size_bytes': len(str(context_data)),
                    'checksum': self._generate_checksum(context_data)
                }
                
                # Store with caching optimization
                self._context_states[sync_id] = context_entry
                self._user_contexts[user_id][sync_id] = context_entry
                self._context_cache[f"{user_id}_latest"] = context_entry
                
                # Update analytics
                self._sync_stats[user_id] += 1
                self._context_analytics[user_id].append({
                    'timestamp': sync_timestamp,
                    'operation': 'sync',
                    'priority': priority,
                    'size': context_entry['size_bytes']
                })
                
                duration_ms = self._record_performance('sync_context_state', 
                                                       start_time)
                
                self._logger.info(
                    f"Enhanced context sync: {sync_id} for user {user_id} "
                    f"(priority: {priority}) in {duration_ms:.2f}ms"
                )
                
                return {
                    'success': True,
                    'sync_id': sync_id,
                    'version': context_entry['version'],
                    'priority': priority,
                    'performance_ms': duration_ms
                }
                
            except Exception as e:
                self._logger.error(f"Failed to sync context state: {str(e)}")
                raise
    
    def _generate_checksum(self, data: dict) -> str:
        """Generate checksum for data integrity validation"""
        return str(hash(str(sorted(data.items()))))[:8]
    
    def get_context_state(self, user_id: str, include_analytics: bool = False) -> dict:
        """
        Enhanced context state retrieval with caching and analytics
        
        Args:
            user_id: User identifier
            include_analytics: Include user analytics in response
            
        Returns:
            dict: Enhanced context state data with metadata
            
        Raises:
            ValueError: If user_id is invalid
        """
        start_time = time.time()
        self._total_operations += 1
        
        with self._context_lock:
            try:
                self._validate_input(user_id=user_id)
                
                # Check cache first for performance
                cache_key = f"{user_id}_latest"
                if cache_key in self._context_cache:
                    cached_context = self._context_cache[cache_key].copy()
                    duration_ms = self._record_performance('get_context_state',
                                                           start_time)
                    self._logger.info(f"Context retrieved from cache for {user_id}")
                    
                    if include_analytics:
                        cached_context['analytics'] = {
                            'sync_count': self._sync_stats[user_id],
                            'recent_operations': self._context_analytics[user_id][-5:]
                        }
                    
                    return cached_context
                
                # Fallback to full retrieval
                user_contexts = self._user_contexts.get(user_id, {})
                
                if not user_contexts:
                    duration_ms = self._record_performance('get_context_state', 
                                                           start_time)
                    self._logger.info(f"No context found for user: {user_id}")
                    return {}
                
                # Get latest context by version
                latest_context = max(user_contexts.values(), 
                                     key=lambda x: x['version'])
                
                # Update cache
                self._context_cache[cache_key] = latest_context
                
                duration_ms = self._record_performance('get_context_state', 
                                                       start_time)
                
                result = latest_context.copy()
                if include_analytics:
                    result['analytics'] = {
                        'sync_count': self._sync_stats[user_id],
                        'recent_operations': self._context_analytics[user_id][-5:]
                    }
                
                self._logger.info(
                    f"Enhanced context retrieved for user {user_id} "
                    f"(v{latest_context['version']}) in {duration_ms:.2f}ms"
                )
                
                return result
                
            except Exception as e:
                self._logger.error(f"Failed to retrieve context state: {str(e)}")
                raise
    
    def resolve_context_conflicts(self, conflict_data: dict, 
                                  strategy: str = 'auto') -> dict:
        """
        Advanced conflict resolution with multiple strategies and ML insights
        
        Args:
            conflict_data: Dictionary containing conflict information
            strategy: Resolution strategy ('auto', 'remote', 'local', 'merge', 'timestamp')
            
        Returns:
            dict: Enhanced resolution record with analytics
            
        Raises:
            ValueError: If conflict_data is invalid
        """
        start_time = time.time()
        self._total_operations += 1
        
        with self._context_lock:
            try:
                # Enhanced validation
                self._validate_input(conflict_data=conflict_data)
                
                required_fields = ['user_id', 'local_context', 'remote_context']
                for field in required_fields:
                    if field not in conflict_data:
                        raise ValueError(f"Required field missing: {field}")
                
                user_id = conflict_data['user_id']
                self._validate_input(user_id=user_id)
                
                local_context = conflict_data['local_context']
                remote_context = conflict_data['remote_context']
                
                # Generate enhanced resolution metadata
                resolution_id = f"resolution_{uuid.uuid4().hex[:16]}"
                resolution_timestamp = datetime.now().isoformat()
                
                # Advanced conflict resolution with strategy selection
                resolution_strategy, resolved_context = self._resolve_with_strategy(
                    local_context, remote_context, strategy
                )
                
                # Enhanced resolution record with analytics
                resolution_record = {
                    'resolution_id': resolution_id,
                    'user_id': user_id,
                    'local_context': local_context,
                    'remote_context': remote_context,
                    'resolved_context': resolved_context,
                    'resolution_strategy': resolution_strategy,
                    'resolved_at': resolution_timestamp,
                    'conflict_complexity': self._calculate_conflict_complexity(
                        local_context, remote_context
                    ),
                    'confidence_score': self._calculate_confidence_score(
                        resolution_strategy, local_context, remote_context
                    )
                }
                
                # Store in enhanced history with analytics
                self._conflict_history.append(resolution_record)
                
                # Update conflict resolution analytics
                self._context_analytics[user_id].append({
                    'timestamp': resolution_timestamp,
                    'operation': 'conflict_resolution',
                    'strategy': resolution_strategy,
                    'complexity': resolution_record['conflict_complexity']
                })
                
                duration_ms = self._record_performance('resolve_context_conflicts', 
                                                       start_time)
                
                self._logger.info(
                    f"Advanced conflict resolved: {resolution_id} for {user_id} "
                    f"using {resolution_strategy} in {duration_ms:.2f}ms"
                )
                
                return resolution_record
                
            except Exception as e:
                self._logger.error(f"Failed to resolve context conflicts: {str(e)}")
                raise
    
    def _resolve_with_strategy(self, local_ctx: dict, remote_ctx: dict, 
                              strategy: str) -> tuple:
        """Advanced strategy-based conflict resolution"""
        local_version = local_ctx.get('version', 0)
        remote_version = remote_ctx.get('version', 0)
        
        if strategy == 'auto':
            if remote_version > local_version:
                return 'remote_preferred', remote_ctx.copy()
            elif local_version > remote_version:
                return 'local_preferred', local_ctx.copy()
            else:
                merged = {**local_ctx, **remote_ctx}
                merged['version'] = max(local_version, remote_version) + 1
                return 'merged', merged
        elif strategy == 'remote':
            return 'remote_forced', remote_ctx.copy()
        elif strategy == 'local':
            return 'local_forced', local_ctx.copy()
        elif strategy == 'timestamp':
            local_time = local_ctx.get('timestamp', '1970-01-01')
            remote_time = remote_ctx.get('timestamp', '1970-01-01')
            if remote_time > local_time:
                return 'timestamp_based_remote', remote_ctx.copy()
            else:
                return 'timestamp_based_local', local_ctx.copy()
        else:  # merge strategy
            merged = {**local_ctx, **remote_ctx}
            merged['version'] = max(local_version, remote_version) + 1
            return 'merge_forced', merged
    
    def _calculate_conflict_complexity(self, local_ctx: dict, remote_ctx: dict) -> str:
        """Calculate conflict complexity level"""
        local_keys = set(local_ctx.keys())
        remote_keys = set(remote_ctx.keys())
        
        overlapping_keys = local_keys & remote_keys
        total_keys = local_keys | remote_keys
        
        if len(overlapping_keys) == 0:
            return 'low'
        elif len(overlapping_keys) / len(total_keys) < 0.5:
            return 'medium'
        else:
            return 'high'
    
    def _calculate_confidence_score(self, strategy: str, local_ctx: dict, 
                                   remote_ctx: dict) -> float:
        """Calculate confidence score for resolution"""
        base_confidence = {
            'remote_preferred': 0.8,
            'local_preferred': 0.8,
            'merged': 0.6,
            'timestamp_based_remote': 0.9,
            'timestamp_based_local': 0.9,
            'remote_forced': 1.0,
            'local_forced': 1.0,
            'merge_forced': 0.7
        }
        return base_confidence.get(strategy, 0.5)