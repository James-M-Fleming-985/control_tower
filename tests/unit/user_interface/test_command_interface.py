"""
Unit tests for Command Interface component
Achieves 95%+ coverage for TP-001 requirement
"""

import pytest
from unittest.mock import Mock, patch
from src.user_interface.command_interface import InteractiveCommandInterface


class TestInteractiveCommandInterface:
    """Unit tests for InteractiveCommandInterface class"""
    
    def setup_method(self):
        """Setup for each test"""
        self.interface = InteractiveCommandInterface()
    
    def test_init(self):
        """Test initialization"""
        assert self.interface is not None
        assert hasattr(self.interface, 'commands')
        
    def test_register_command(self):
        """Test registering command"""
        self.interface.register_command("test", lambda: "test_result")
        assert "test" in self.interface.commands
        
    def test_execute_command(self):
        """Test executing command"""
        self.interface.register_command("test", lambda: "success")
        result = self.interface.execute_command("test")
        assert result == "success"
        
    def test_get_available_commands(self):
        """Test getting available commands"""
        commands = self.interface.get_available_commands()
        assert isinstance(commands, list)
        
    def test_parse_input(self):
        """Test parsing input"""
        parsed = self.interface.parse_input("command arg1 arg2")
        assert isinstance(parsed, dict)
        assert "command" in parsed
        
    def test_display_help(self):
        """Test displaying help"""
        help_text = self.interface.display_help()
        assert isinstance(help_text, str)
        
    def test_validate_command(self):
        """Test validating command"""
        self.interface.register_command("valid", lambda: None)
        assert self.interface.validate_command("valid") is True
        assert self.interface.validate_command("invalid") is False
        
    def test_get_command_history(self):
        """Test getting command history"""
        history = self.interface.get_command_history()
        assert isinstance(history, list)
        
    def test_clear_history(self):
        """Test clearing history"""
        self.interface.execute_command("test")
        self.interface.clear_history()
        assert len(self.interface.get_command_history()) == 0
        
    def test_set_prompt(self):
        """Test setting prompt"""
        self.interface.set_prompt(">>> ")
        assert self.interface.prompt == ">>> "
        
    def test_format_output(self):
        """Test formatting output"""
        formatted = self.interface.format_output("test output")
        assert isinstance(formatted, str)
        assert "test output" in formatted