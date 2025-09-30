#!/usr/bin/env python3
"""
TDD Iteration 2 - GREEN Phase Context Correlation Tests

This module validates the working context correlation functionality
after successful implementation in mobile_command_history_repository.py

Tests verify:
- Context-aware command storage
- Multi-criteria context querying 
- Hierarchical context management
- Context statistics generation
- Command relationship tracking
- Performance requirements (<200ms per operation)
"""

import unittest
import time
from datetime import datetime
from mobile_command_history_repository import MobileCommandHistoryRepository


class TestMobileCommandContextCorrelationGreen(unittest.TestCase):
    """GREEN Phase tests for context correlation functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.repository = MobileCommandHistoryRepository()
        
    def test_store_command_with_context_works(self):
        """Test context-aware command storage functionality"""
        start_time = time.time()
        
        command_data = {
            "user_id": "user_123",
            "command": "validate_feature",
            "command_type": "validation",
            "context": {
                "project": "PROJECT-003",
                "system": "extended_validation",
                "feature": "validation_engine",
                "layer": "data_access"
            },
            "timestamp": datetime.now().isoformat()
        }
        
        # Store command with context
        command_id = self.repository.store_command_with_context(command_data)
        
        # Validate performance requirement
        duration = time.time() - start_time
        self.assertLess(duration, 0.2, "Context storage should complete in <200ms")
        
        # Validate command was stored
        self.assertIsNotNone(command_id)
        self.assertTrue(isinstance(command_id, str))
        
        # Validate command can be retrieved
        retrieved_command = self.repository.get_command(command_id)
        self.assertIsNotNone(retrieved_command)
        self.assertEqual(retrieved_command["context"], command_data["context"])
        
    def test_query_commands_by_context_works(self):
        """Test context-based command querying functionality"""
        # Store test commands with different contexts
        contexts = [
            {"project": "PROJECT-003", "system": "validation", "feature": "pyramid"},
            {"project": "PROJECT-003", "system": "validation", "feature": "engine"},
            {"project": "PROJECT-002", "system": "testing", "feature": "automation"}
        ]
        
        command_ids = []
        for i, context in enumerate(contexts):
            command_data = {
                "user_id": f"user_{i}",
                "command": f"test_command_{i}",
                "command_type": "test",
                "context": context,
                "timestamp": datetime.now().isoformat()
            }
            command_id = self.repository.store_command_with_context(command_data)
            command_ids.append(command_id)
        
        start_time = time.time()
        
        # Query by single context criterion
        result = self.repository.get_commands_by_context({"project": "PROJECT-003"})
        
        # Validate performance requirement
        duration = time.time() - start_time
        self.assertLess(duration, 0.2, "Context query should complete in <200ms")
        
        # Validate results
        self.assertEqual(len(result), 2)
        for command in result:
            self.assertEqual(command["context"]["project"], "PROJECT-003")
            self.assertIn("query_time_ms", command)
            self.assertIn("context_query", command)
    
    def test_query_commands_by_multiple_context_criteria_works(self):
        """Test multi-criteria context querying functionality"""
        # Store test commands
        command_data = {
            "user_id": "user_multi",
            "command": "multi_context_test",
            "command_type": "validation",
            "context": {
                "project": "PROJECT-003",
                "system": "extended_validation",
                "feature": "validation_engine"
            },
            "timestamp": datetime.now().isoformat()
        }
        
        command_id = self.repository.store_command_with_context(command_data)
        
        start_time = time.time()
        
        # Query by multiple criteria
        multi_filter = {
            "project": "PROJECT-003",
            "system": "extended_validation"
        }
        result = self.repository.get_commands_by_context(multi_filter)
        
        # Validate performance requirement
        duration = time.time() - start_time
        self.assertLess(duration, 0.2, "Multi-criteria query should complete in <200ms")
        
        # Validate results
        self.assertEqual(len(result), 1)
        command = result[0]
        self.assertEqual(command["context"]["project"], "PROJECT-003")
        self.assertEqual(command["context"]["system"], "extended_validation")
    
    def test_get_context_hierarchy_works(self):
        """Test hierarchical context structure generation"""
        user_id = "hierarchy_user"
        
        # Store commands with hierarchical contexts
        contexts = [
            {"project": "PROJECT-003", "system": "validation", "feature": "pyramid"},
            {"project": "PROJECT-003", "system": "validation", "feature": "engine"},
            {"project": "PROJECT-003", "system": "testing", "feature": "automation"}
        ]
        
        for i, context in enumerate(contexts):
            command_data = {
                "user_id": user_id,
                "command": f"hierarchy_test_{i}",
                "command_type": "test",
                "context": context,
                "timestamp": datetime.now().isoformat()
            }
            self.repository.store_command_with_context(command_data)
        
        start_time = time.time()
        
        # Get hierarchy
        hierarchy = self.repository.get_context_hierarchy(user_id)
        
        # Validate performance requirement
        duration = time.time() - start_time
        self.assertLess(duration, 0.2, "Hierarchy generation should complete in <200ms")
        
        # Validate hierarchy structure
        self.assertEqual(hierarchy["user_id"], user_id)
        self.assertEqual(hierarchy["command_count"], 3)
        self.assertIn("hierarchy", hierarchy)
        self.assertIn("query_time_ms", hierarchy)
        self.assertIn("generated_at", hierarchy)
        
        # Validate hierarchical structure
        project_hierarchy = hierarchy["hierarchy"]
        self.assertIn("PROJECT-003", project_hierarchy)
    
    def test_get_commands_by_context_path_works(self):
        """Test hierarchical path querying functionality"""
        # Store command with hierarchical context
        command_data = {
            "user_id": "path_user",
            "command": "path_test",
            "command_type": "validation",
            "context": {
                "project": "PROJECT-003",
                "system": "extended_validation",
                "feature": "validation_engine"
            },
            "timestamp": datetime.now().isoformat()
        }
        
        command_id = self.repository.store_command_with_context(command_data)
        
        start_time = time.time()
        
        # Query by context path
        context_path = "PROJECT-003/extended_validation/validation_engine"
        result = self.repository.get_commands_by_context_path(context_path)
        
        # Validate performance requirement
        duration = time.time() - start_time
        self.assertLess(duration, 0.2, "Path query should complete in <200ms")
        
        # Validate results
        self.assertEqual(len(result), 1)
        command = result[0]
        self.assertEqual(command["context"]["project"], "PROJECT-003")
        self.assertEqual(command["context"]["system"], "extended_validation")
        self.assertEqual(command["context"]["feature"], "validation_engine")
        self.assertIn("context_path", command)
        self.assertIn("path_query_time_ms", command)
    
    def test_get_context_statistics_works(self):
        """Test context statistics generation functionality"""
        # Store multiple commands for statistics
        contexts = [
            {"project": "PROJECT-003", "status": "completed"},
            {"project": "PROJECT-003", "status": "pending"},  
            {"project": "PROJECT-003", "status": "completed"}
        ]
        
        for i, context in enumerate(contexts):
            command_data = {
                "user_id": f"stats_user_{i}",
                "command": f"stats_test_{i}",
                "command_type": "validation",
                "context": context,
                "status": context["status"],
                "timestamp": datetime.now().isoformat()
            }
            self.repository.store_command_with_context(command_data)
        
        start_time = time.time()
        
        # Get statistics
        context_filter = {"project": "PROJECT-003"}
        stats = self.repository.get_context_statistics(context_filter)
        
        # Validate performance requirement
        duration = time.time() - start_time
        self.assertLess(duration, 0.2, "Statistics generation should complete in <200ms")
        
        # Validate statistics structure
        self.assertEqual(stats["total_commands"], 3)
        self.assertEqual(stats["unique_users"], 3)
        self.assertIn("command_types", stats)
        self.assertIn("status_distribution", stats)
        self.assertIn("time_range", stats)
        self.assertIn("query_time_ms", stats)
        self.assertIn("generated_at", stats)
        
        # Validate status distribution
        self.assertEqual(stats["status_distribution"]["completed"], 2)
        self.assertEqual(stats["status_distribution"]["pending"], 1)
    
    def test_command_relationships_work(self):
        """Test command relationship tracking functionality"""
        # Store command with relationships
        command_data = {
            "user_id": "relationship_user",
            "command": "parent_command",
            "command_type": "validation",
            "context": {"project": "PROJECT-003"},
            "relationships": {
                "parent_command": None,
                "child_commands": ["child_001", "child_002"],
                "dependency_commands": ["dep_001"]
            },
            "timestamp": datetime.now().isoformat()
        }
        
        command_id = self.repository.store_command_with_context(command_data)
        
        start_time = time.time()
        
        # Get relationships
        relationships = self.repository.get_command_relationships(command_id)
        
        # Validate performance requirement
        duration = time.time() - start_time
        self.assertLess(duration, 0.2, "Relationship query should complete in <200ms")
        
        # Validate relationships structure
        self.assertEqual(relationships["command_id"], command_id)
        self.assertIsNone(relationships["parent_command"])
        self.assertEqual(len(relationships["child_commands"]), 2)
        self.assertEqual(len(relationships["dependency_commands"]), 1)
        self.assertIn("query_time_ms", relationships)
        self.assertIn("generated_at", relationships)
    
    def test_hierarchical_context_query_works(self):
        """Test hierarchical context querying functionality"""
        # Store command with hierarchical context
        command_data = {
            "user_id": "hierarchical_user",
            "command": "hierarchical_test",
            "command_type": "validation",
            "context": {
                "project": "PROJECT-003",
                "system": "extended_validation"
            },
            "timestamp": datetime.now().isoformat()
        }
        
        command_id = self.repository.store_command_with_context(command_data)
        
        start_time = time.time()
        
        # Query by hierarchy
        hierarchy_filter = {
            "project": "PROJECT-003",
            "system": "extended_validation"
        }
        result = self.repository.get_commands_by_hierarchy(hierarchy_filter)
        
        # Validate performance requirement
        duration = time.time() - start_time
        self.assertLess(duration, 0.2, "Hierarchical query should complete in <200ms")
        
        # Validate results
        self.assertEqual(len(result), 1)
        command = result[0]
        self.assertEqual(command["context"]["project"], "PROJECT-003")
        self.assertEqual(command["context"]["system"], "extended_validation")
        self.assertIn("hierarchy_filter", command)
        self.assertIn("hierarchy_query_time_ms", command)
    
    def test_context_correlation_integration(self):
        """Test complete context correlation integration"""
        start_time = time.time()
        
        # Store multiple related commands
        base_context = {
            "project": "PROJECT-003",
            "system": "extended_validation",
            "feature": "validation_engine",
            "layer": "data_access"
        }
        
        command_ids = []
        for i in range(5):
            command_data = {
                "user_id": f"integration_user_{i}",
                "command": f"integration_test_{i}",
                "command_type": "validation",
                "context": base_context.copy(),
                "status": "completed" if i % 2 == 0 else "pending",
                "timestamp": datetime.now().isoformat()
            }
            command_id = self.repository.store_command_with_context(command_data)
            command_ids.append(command_id)
        
        # Test all context correlation methods work together
        
        # 1. Context querying
        context_results = self.repository.get_commands_by_context(base_context)
        self.assertEqual(len(context_results), 5)
        
        # 2. Path querying  
        path_results = self.repository.get_commands_by_context_path(
            "PROJECT-003/extended_validation/validation_engine/data_access"
        )
        self.assertEqual(len(path_results), 5)
        
        # 3. Statistics generation
        stats = self.repository.get_context_statistics(base_context)
        self.assertEqual(stats["total_commands"], 5)
        self.assertEqual(stats["unique_users"], 5)
        
        # 4. Hierarchy generation
        hierarchy = self.repository.get_context_hierarchy("integration_user_0")
        self.assertEqual(hierarchy["command_count"], 1)
        
        # Validate overall performance
        total_duration = time.time() - start_time
        self.assertLess(total_duration, 1.0, "Complete integration should complete in <1s")


if __name__ == "__main__":
    unittest.main()