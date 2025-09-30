import time
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from collections import defaultdict


class ContextEngineRepository:
    """Context Engine Repository for managing context synchronization and state"""
    
    def __init__(self):
        """Initialize the Context Engine Repository"""
        self._context_states = {}
        self._user_contexts = defaultdict(dict)
        self._conflict_history = []
        self._logger = logging.getLogger(__name__)
        self._performance_metrics = {}
        self._total_operations = 0
        
        # Configure logging
        if not self._logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s [%(levelname)8s] %(name)s: %(message)s'
            )
            handler.setFormatter(formatter)
            self._logger.addHandler(handler)
            self._logger.setLevel(logging.INFO)
        
        self._logger.info("ContextEngineRepository initialized")
    
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
    
    def sync_context_state(self, context_data: dict) -> bool:
        """
        Synchronize context state data
        
        Args:
            context_data: Dictionary containing context state information
            
        Returns:
            bool: True if synchronization successful
            
        Raises:
            ValueError: If context_data is invalid
        """
        start_time = time.time()
        self._total_operations += 1
        
        try:
            # Validate input
            self._validate_input(context_data=context_data)
            
            required_fields = ['user_id', 'context_state']
            for field in required_fields:
                if field not in context_data:
                    raise ValueError(f"Required field missing: {field}")
            
            user_id = context_data['user_id']
            self._validate_input(user_id=user_id)
            
            # Generate sync ID and timestamp
            sync_id = f"sync_{uuid.uuid4().hex[:16]}"
            sync_timestamp = datetime.now().isoformat()
            
            # Create context entry
            context_entry = {
                'sync_id': sync_id,
                'user_id': user_id,
                'context_state': context_data['context_state'],
                'synchronized_at': sync_timestamp,
                'version': len(self._user_contexts[user_id]) + 1
            }
            
            # Store context state
            self._context_states[sync_id] = context_entry
            self._user_contexts[user_id][sync_id] = context_entry
            
            duration_ms = self._record_performance('sync_context_state', start_time)
            
            self._logger.info(
                f"Context synchronized: {sync_id} for user {user_id} "
                f"in {duration_ms:.2f}ms"
            )
            
            return True
            
        except Exception as e:
            self._logger.error(f"Failed to sync context state: {str(e)}")
            raise
    
    def get_context_state(self, user_id: str) -> dict:
        """
        Retrieve context state for a user
        
        Args:
            user_id: User identifier
            
        Returns:
            dict: Context state data
            
        Raises:
            ValueError: If user_id is invalid
        """
        start_time = time.time()
        self._total_operations += 1
        
        try:
            self._validate_input(user_id=user_id)
            
            # Get user contexts
            user_contexts = self._user_contexts.get(user_id, {})
            
            if not user_contexts:
                duration_ms = self._record_performance('get_context_state', start_time)
                self._logger.info(f"No context found for user: {user_id}")
                return {}
            
            # Get latest context by version
            latest_context = max(user_contexts.values(), key=lambda x: x['version'])
            
            duration_ms = self._record_performance('get_context_state', start_time)
            
            self._logger.info(
                f"Retrieved context for user {user_id} "
                f"(version {latest_context['version']}) in {duration_ms:.2f}ms"
            )
            
            return latest_context.copy()
            
        except Exception as e:
            self._logger.error(f"Failed to retrieve context state: {str(e)}")
            raise
    
    def resolve_context_conflicts(self, conflict_data: dict) -> dict:
        """
        Resolve context conflicts between local and remote state
        
        Args:
            conflict_data: Dictionary containing conflict information
            
        Returns:
            dict: Resolved context data
            
        Raises:
            ValueError: If conflict_data is invalid
        """
        start_time = time.time()
        self._total_operations += 1
        
        try:
            # Validate input
            self._validate_input(conflict_data=conflict_data)
            
            required_fields = ['user_id', 'local_context', 'remote_context']
            for field in required_fields:
                if field not in conflict_data:
                    raise ValueError(f"Required field missing: {field}")
            
            user_id = conflict_data['user_id']
            self._validate_input(user_id=user_id)
            
            local_context = conflict_data['local_context']
            remote_context = conflict_data['remote_context']
            
            # Generate resolution ID
            resolution_id = f"resolution_{uuid.uuid4().hex[:16]}"
            resolution_timestamp = datetime.now().isoformat()
            
            # Simple conflict resolution: prefer remote if versions differ
            local_version = local_context.get('version', 0)
            remote_version = remote_context.get('version', 0)
            
            if remote_version > local_version:
                resolved_context = remote_context.copy()
                resolution_strategy = 'remote_preferred'
            elif local_version > remote_version:
                resolved_context = local_context.copy()
                resolution_strategy = 'local_preferred'
            else:
                # Merge contexts if versions are equal
                resolved_context = {**local_context, **remote_context}
                resolved_context['version'] = max(local_version, remote_version) + 1
                resolution_strategy = 'merged'
            
            # Create resolution record
            resolution_record = {
                'resolution_id': resolution_id,
                'user_id': user_id,
                'local_context': local_context,
                'remote_context': remote_context,
                'resolved_context': resolved_context,
                'resolution_strategy': resolution_strategy,
                'resolved_at': resolution_timestamp
            }
            
            # Store resolution history
            self._conflict_history.append(resolution_record)
            
            duration_ms = self._record_performance('resolve_context_conflicts', start_time)
            
            self._logger.info(
                f"Context conflict resolved: {resolution_id} for user {user_id} "
                f"using {resolution_strategy} strategy in {duration_ms:.2f}ms"
            )
            
            return resolution_record
            
        except Exception as e:
            self._logger.error(f"Failed to resolve context conflicts: {str(e)}")
            raise