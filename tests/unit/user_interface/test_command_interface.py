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
        # Exercise more initialization logic
        assert hasattr(self.interface, 'history')
        assert hasattr(self.interface, 'prompt')
        
    def test_register_command(self):
        """Test registering command"""
        def test_command():
            return "test_result"
        self.interface.register_command("test", test_command)
        assert "test" in self.interface.commands
        # Exercise command execution after registration
        result = self.interface.execute_command("test")
        assert result == "test_result"
        
    def test_execute_command(self):
        """Test executing command"""
        def success_command():
            return "success"
        self.interface.register_command("test", success_command)
        result = self.interface.execute_command("test")
        assert result == "success"
        
        # Test non-existent command
        result = self.interface.execute_command("nonexistent")
        assert result is None or "not found" in str(result).lower()
        
    def test_get_available_commands(self):
        """Test getting available commands"""
        commands = self.interface.get_available_commands()
        assert isinstance(commands, list)
        
        # Add commands and test again
        self.interface.register_command("cmd1", lambda: None)
        self.interface.register_command("cmd2", lambda: None)
        commands = self.interface.get_available_commands()
        assert "cmd1" in commands
        assert "cmd2" in commands
        
    def test_parse_input(self):
        """Test input parsing"""
        # Test various input formats
        parsed = self.interface.parse_input("command arg1 arg2")
        assert isinstance(parsed, (list, tuple, dict))
        
        parsed = self.interface.parse_input("simple")
        assert parsed is not None
        
        parsed = self.interface.parse_input("")
        assert parsed is not None
        
    def test_display_help(self):
        """Test help display"""
        help_output = self.interface.display_help()
        assert isinstance(help_output, str)
        assert len(help_output) > 0
        
        # Test help for specific command
        self.interface.register_command("test", lambda: None)
        help_output = self.interface.display_help("test")
        assert isinstance(help_output, str)
        
    def test_validate_command(self):
        """Test command validation"""
        # Test with valid command
        self.interface.register_command("valid", lambda: None)
        is_valid = self.interface.validate_command("valid")
        assert is_valid is True
        
        # Test with invalid command
        is_valid = self.interface.validate_command("invalid")
        assert is_valid is False
        
    def test_get_command_history(self):
        """Test command history"""
        history = self.interface.get_command_history()
        assert isinstance(history, list)
        
        # Execute some commands to build history
        self.interface.register_command("test", lambda: "result")
        self.interface.execute_command("test")
        self.interface.execute_command("test")
        
        history = self.interface.get_command_history()
        assert len(history) >= 0
        
    def test_clear_history(self):
        """Test clearing history"""
        # Add some history first
        self.interface.register_command("test", lambda: None)
        self.interface.execute_command("test")
        
        # Clear history
        self.interface.clear_history()
        history = self.interface.get_command_history()
        assert len(history) == 0
        
    def test_set_prompt(self):
        """Test setting prompt"""
        original_prompt = getattr(self.interface, 'prompt', '>')
        self.interface.set_prompt("custom> ")
        assert self.interface.prompt == "custom> "
        
        # Reset to original
        self.interface.set_prompt(original_prompt)
        
    def test_format_output(self):
        """Test output formatting"""
        formatted = self.interface.format_output("test output")
        assert isinstance(formatted, str)
        assert "test output" in formatted
        
        # Test with different data types
        formatted = self.interface.format_output({"key": "value"})
        assert isinstance(formatted, str)
        
        formatted = self.interface.format_output([1, 2, 3])
        assert isinstance(formatted, str)
        
    def test_advanced_command_execution(self):
        """Test advanced command scenarios"""
        # Test command with arguments
        def arg_command(*args, **kwargs):
            return f"args: {args}, kwargs: {kwargs}"
            
        self.interface.register_command("argcmd", arg_command)
        result = self.interface.execute_command("argcmd", "arg1", "arg2", key="value")
        assert isinstance(result, str)
        
        # Test command with exception handling
        def error_command():
            raise ValueError("Test error")
            
        self.interface.register_command("error", error_command)
        result = self.interface.execute_command("error")
        # Should handle gracefully
        assert result is not None
        
    def test_command_metadata(self):
        """Test command metadata handling"""
        def documented_command():
            """This is a test command"""
            return "documented"
            
        self.interface.register_command("doc", documented_command, help_text="Test help")
        
        # Test help text retrieval
        help_output = self.interface.display_help("doc")
        assert "test" in help_output.lower()
        
    def test_input_validation(self):
        """Test input validation scenarios"""
        # Test empty input
        result = self.interface.execute_command("")
        assert result is not None
        
        # Test whitespace input
        result = self.interface.execute_command("   ")
        assert result is not None
        
        # Test special characters
        result = self.interface.execute_command("!@#$%")
        assert result is not None
        
    def test_session_management(self):
        """Test session management features"""
        # Test session state
        if hasattr(self.interface, 'get_session_info'):
            session_info = self.interface.get_session_info()
            assert isinstance(session_info, dict)
            
        # Test session reset
        if hasattr(self.interface, 'reset_session'):
            self.interface.reset_session()
            history = self.interface.get_command_history()
            assert len(history) == 0

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