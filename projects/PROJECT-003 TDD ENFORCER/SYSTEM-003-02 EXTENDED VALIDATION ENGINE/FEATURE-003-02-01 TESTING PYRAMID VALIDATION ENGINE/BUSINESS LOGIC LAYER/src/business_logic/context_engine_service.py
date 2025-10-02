"""
Context Engine Service - Business Logic Layer
Layer: LAY-003-02-01-002 (Business Logic)
Requirement: REQ-DATA-007 Context Engine Integration
TDD Phase: REFACTOR (Code quality improvements)
"""

import logging
from datetime import datetime

# Configure logger
logger = logging.getLogger(__name__)

# Dictionary key constants
KEY_PROCESSED = 'processed'
KEY_USER_ID = 'user_id'
KEY_CHANGES_APPLIED = 'changes_applied'
KEY_TIMESTAMP = 'timestamp'
KEY_CONTEXT_STATE = 'context_state'
KEY_MERGED_STATE = 'merged_state'
KEY_VERSION = 'version'
KEY_CONFLICTS_RESOLVED = 'conflicts_resolved'
KEY_MERGE_STRATEGY_USED = 'merge_strategy_used'


class ContextEngineService:
    """
    Business logic service for context engine state management.
    
    This service handles:
    - Context change processing
    - Context consistency validation
    - Context state merging
    """
    
    def __init__(self):
        """Initialize the context engine service."""
        self.context_store = {}

    def _initialize_user_context(self, user_id: str) -> None:
        """Initialize empty context for new user.

        Args:
            user_id: User identifier

        Returns:
            None
        """
        if user_id not in self.context_store:
            self.context_store[user_id] = {'changes': []}
    
    def process_context_changes(self, context_changes: dict) -> dict:
        """Process and store user context changes.

        Validates input, initializes user context if needed, and stores
        all provided changes in the context store.

        Args:
            context_changes: Dictionary containing:
                - user_id (str): Unique user identifier
                - changes (List[dict]): List of context changes to apply

        Returns:
            dict: Processing result containing:
                - processed (bool): Always True if successful
                - user_id (str): User identifier from input
                - changes_applied (int): Number of changes processed
                - timestamp (str): ISO format timestamp of processing
                - context_state (dict): Current user context state

        Raises:
            TypeError: If context_changes is not a dict or changes is not list
            ValueError: If user_id is missing or invalid
            RuntimeError: If processing fails during change application
        """
        # Input validation
        if not isinstance(context_changes, dict):
            raise TypeError("context_changes must be a dictionary")
        
        user_id = context_changes.get('user_id')
        if not user_id:
            raise ValueError("context_changes must include 'user_id'")
        
        changes = context_changes.get('changes', [])
        if not isinstance(changes, list):
            raise TypeError("'changes' must be a list")

        logger.info("Processing %d context changes for user %s",
                    len(changes), user_id)
        
        self._initialize_user_context(user_id)
        
        try:
            for change in changes:
                self.context_store[user_id]['changes'].append(change)
        except Exception as e:
            raise RuntimeError(f"Failed to process changes: {e}") from e
        
        logger.debug("Context state after processing: %s",
                     self.context_store[user_id])
        
        return {
            KEY_PROCESSED: True,
            KEY_USER_ID: user_id,
            KEY_CHANGES_APPLIED: len(changes),
            KEY_TIMESTAMP: datetime.now().isoformat(),
            KEY_CONTEXT_STATE: self.context_store[user_id]
        }
    
    def validate_context_consistency(self, user_id: str) -> bool:
        """Validate context consistency for a user.

        Checks if the user's context store has the required structure
        and valid data types. Returns True for users without context.

        Args:
            user_id: User identifier (must be non-empty string)

        Returns:
            bool: True if context is consistent or doesn't exist,
                  False if context structure is invalid

        Raises:
            ValueError: If user_id is missing or not a string
        """
        # Input validation
        if not user_id or not isinstance(user_id, str):
            raise ValueError("user_id must be a non-empty string")
        
        logger.debug("Validating context consistency for user %s", user_id)
        
        if user_id not in self.context_store:
            return True
        
        context = self.context_store[user_id]
        
        # Validate required structure
        if ('changes' not in context or
                not isinstance(context['changes'], list)):
            return False
        
        return True

    def _auto_resolve_merge(self, base: dict, incoming: dict) -> tuple:
        """Smart merge with conflict detection.

        Args:
            base: Base context state dictionary
            incoming: Incoming context state dictionary

        Returns:
            tuple: (merged_state dict, conflicts_resolved int)
        """
        merged = base.copy()
        conflicts = 0

        for key, value in incoming.items():
            if key in base and base[key] != value:
                conflicts += 1
            merged[key] = value

        return merged, conflicts
    
    def merge_context_states(self, merge_request: dict) -> dict:
        """Merge context states using specified strategy.

        Supports three merge strategies:
        - auto_resolve: Smart merge with conflict detection
        - last_write_wins: Simple merge where incoming wins
        - manual: Returns both states for manual resolution

        Args:
            merge_request: Dictionary containing:
                - base_context (dict): Base context with 'state' and 'version'
                - incoming_context (dict): Incoming context with 'state'
                                           and 'version'
                - merge_strategy (str): Strategy to use (default:
                                        'auto_resolve')

        Returns:
            dict: Merge result containing:
                - merged_state (dict): Merged context state
                - version (int): New version number (max + 1)
                - conflicts_resolved (int): Number of conflicts detected
                - merge_strategy_used (str): Strategy that was applied
                - timestamp (str): ISO format timestamp of merge

        Raises:
            TypeError: If merge_request is not a dictionary
            ValueError: If merge_strategy is not recognized
        """
        # Input validation
        if not isinstance(merge_request, dict):
            raise TypeError("merge_request must be a dictionary")
        
        base_context = merge_request.get('base_context', {})
        incoming_context = merge_request.get('incoming_context', {})
        merge_strategy = merge_request.get('merge_strategy', 'auto_resolve')
        
        base_state = base_context.get('state', {})
        incoming_state = incoming_context.get('state', {})
        base_version = base_context.get('version', 0)
        incoming_version = incoming_context.get('version', 0)
        
        logger.info("Merging context states using '%s' strategy "
                    "(base v%d, incoming v%d)",
                    merge_strategy, base_version, incoming_version)
        
        # Implement actual merge strategy logic
        if merge_strategy == 'auto_resolve':
            # Smart merge: detect conflicts, prefer newer values
            merged_state, conflicts_resolved = self._auto_resolve_merge(
                base_state, incoming_state)
        elif merge_strategy == 'last_write_wins':
            # Simple merge: incoming always wins
            merged_state = {**base_state, **incoming_state}
            conflicts_resolved = 0
        elif merge_strategy == 'manual':
            # Return both states for manual resolution
            merged_state = {
                'base': base_state,
                'incoming': incoming_state,
                'requires_manual_merge': True
            }
            conflicts_resolved = len(
                set(base_state.keys()) & set(incoming_state.keys()))
        else:
            raise ValueError(
                f"Unknown merge strategy: {merge_strategy}")
        
        new_version = max(base_version, incoming_version) + 1
        
        return {
            KEY_MERGED_STATE: merged_state,
            KEY_VERSION: new_version,
            KEY_CONFLICTS_RESOLVED: conflicts_resolved,
            KEY_MERGE_STRATEGY_USED: merge_strategy,
            KEY_TIMESTAMP: datetime.now().isoformat()
        }
