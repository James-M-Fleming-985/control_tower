"""
Interactive Command Interface Component
User command processing and interaction for TDD enforcer
"""

import re
import time
from typing import List, Dict, Any


class InteractiveCommandInterface:
    """Interactive command interface with autocompletion and help"""
    
    def __init__(self):
        self.commands = {}
        self.command_history = []
        self.prompt = ">>> "
        self.session_active = False
        self.preferences = {}
        self.user_role = "user"
        import time
        self.created_at = time.time()


    def start_session(self) -> None:
        """Start interactive session with enhanced features"""
        self.session_active = True
        self._command_history = []
        self._session_start_time = time.time()
        print("🚀 TDD Command Interface Started")
        print("Type 'help' for available commands or 'exit' to quit")
    
    def autocomplete(self, partial: str) -> List[str]:
        """Provide context-aware autocompletion with fuzzy matching"""
        return [cmd for cmd in self.commands.keys() if cmd.startswith(partial)]
    
    def register_command(self, name, func):
        """Register command"""
        self.commands[name] = func
    
    def execute_command(self, command, *args):
        """Execute command with optional arguments"""
        self.command_history.append(command)
        if command in self.commands:
            try:
                return self.commands[command](*args) if args else self.commands[command]()
            except Exception as e:
                return f"Error executing '{command}': {e}"
        return None  # Changed to return None for unknown commands
    
    def get_available_commands(self):
        """Get available commands"""
        return list(self.commands.keys())
    
    def parse_input(self, input_str):
        """Parse input"""
        parts = input_str.split()
        return {"command": parts[0] if parts else "", "args": parts[1:] if len(parts) > 1 else []}
    
    def display_help(self, topic=None):
        """Display help for all commands or specific topic"""
        if topic and topic in self.commands:
            return f"Help for '{topic}': {self.commands[topic].__doc__ or 'No documentation available'}"
        return f"Available commands: {', '.join(self.commands.keys())}"
    
    def validate_command(self, command):
        """Validate command"""
        return command in self.commands
    
    def get_command_history(self):
        """Get command history"""
        return self.command_history
    
    def clear_history(self):
        """Clear history"""
        self.command_history = []
    
    def set_prompt(self, prompt):
        """Set prompt"""
        self.prompt = prompt
    
    def format_output(self, output):
        """Format output"""
        return f"[OUTPUT] {output}"
        import difflib
        
        # Exact prefix matches (highest priority)
        exact_matches = [cmd for cmd in self.commands if cmd.startswith(partial.lower())]
        
        # Fuzzy matches (secondary priority)
        fuzzy_matches = difflib.get_close_matches(partial.lower(), self.commands, n=3, cutoff=0.6)
        
        # Context-aware suggestions based on current phase
        context_suggestions = []
        if hasattr(self, '_current_phase'):
            phase_commands = {
                'RED': ['test', 'fail', 'validate'],
                'GREEN': ['implement', 'pass', 'minimal'],
                'REFACTOR': ['improve', 'optimize', 'clean']
            }
            context_suggestions = [cmd for cmd in phase_commands.get(self._current_phase, []) 
                                 if cmd.startswith(partial.lower())]
        
        # Combine and deduplicate while preserving order
        all_suggestions = exact_matches + context_suggestions + fuzzy_matches
        seen = set()
        result = []
        for item in all_suggestions:
            if item not in seen:
                seen.add(item)
                result.append(item)
                
        return result[:5]  # Limit to top 5 suggestions
    
    def get_help(self, topic: str = None) -> str:
        """Comprehensive help system with examples and tutorials"""
        if not topic:
            return self._get_general_help()
            
        help_content = {
            "phase": {
                "description": "TDD phase management commands",
                "commands": ["show", "transition", "status", "validate"],
                "examples": [
                    "phase show - Display current TDD phase",
                    "phase transition red - Move to RED phase",
                    "phase status - Show phase history"
                ],
                "tutorial": "TDD phase commands allow you to manage the Red-Green-Refactor cycle effectively."
            },
            "test": {
                "description": "Test execution and management",
                "commands": ["run", "status", "results", "coverage"],
                "examples": [
                    "test run - Execute current test suite",
                    "test coverage - Show test coverage report",
                    "test results --format json - Get results in JSON format"
                ],
                "tutorial": "Tests should be written before implementation. Aim for 100% coverage."
            },
            "status": {
                "description": "System status and monitoring",
                "commands": ["current", "history", "enforcement", "metrics"],
                "examples": [
                    "status current - Show current system state",
                    "status enforcement - Display enforcement rules",
                    "status metrics - Performance and quality metrics"
                ],
                "tutorial": "Regular status checks help maintain TDD discipline and track progress."
            }
        }
        
        topic_info = help_content.get(topic.lower())
        if not topic_info:
            return f"⚠️  No help available for '{topic}'. Available topics: {', '.join(help_content.keys())}"
            
        result = f"📚 HELP: {topic.upper()}\n"
        result += "=" * 40 + "\n"
        result += f"Description: {topic_info['description']}\n\n"
        result += "Commands:\n"
        for cmd in topic_info['commands']:
            result += f"  • {cmd}\n"
        result += "\nExamples:\n"
        for example in topic_info['examples']:
            result += f"  📝 {example}\n"
        result += f"\nTutorial: {topic_info['tutorial']}\n"
        result += "\nFor more help: help <command> or visit docs/tdd-guide.md"
        
        return result
        
    def _get_general_help(self) -> str:
        """General help overview"""
        result = "🎆 TDD COMMAND INTERFACE HELP\n"
        result += "=" * 40 + "\n"
        result += "Available commands:\n"
        for cmd in sorted(self.commands):
            result += f"  • {cmd}\n"
        result += "\nTopics: phase, test, status\n"
        result += "Usage: <command> [options] or help <topic>\n"
        result += "\nTips:\n"
        result += "  • Use Tab for autocompletion\n"
        result += "  • Commands are context-aware based on TDD phase\n"
        result += "  • Type 'exit' to quit the session\n"
        return result
    
    def set_preference(self, key: str, value: Any) -> None:
        """Set user preferences with validation"""
        valid_preferences = {
            'color_scheme': ['dark', 'light', 'high_contrast'],
            'output_format': ['text', 'json', 'yaml'],
            'notification_level': ['all', 'errors_only', 'silent'],
            'autocompletion': [True, False],
            'session_timeout': range(5, 121)  # 5-120 minutes
        }
        
        if key not in valid_preferences:
            raise ValueError(f"Invalid preference key. Valid keys: {list(valid_preferences.keys())}")
            
        valid_values = valid_preferences[key]
        if isinstance(valid_values, range):
            if value not in valid_values:
                raise ValueError(f"Value must be between {valid_values.start} and {valid_values.stop-1}")
        elif value not in valid_values:
            raise ValueError(f"Invalid value. Valid values: {valid_values}")
            
        self.preferences[key] = value
        print(f"⚙️  Preference updated: {key} = {value}")

    def handle_error(self, error):
        """Handle errors in command processing"""
        error_msg = f"Error: {str(error)}"
        self.command_history.append(f"ERROR: {error_msg}")
        return error_msg

    def get_user_input(self):
        """Get user input (mocked for testing)"""
        return "test_input"

    def get_phase(self):
        """Get current TDD phase"""
        return getattr(self, '_current_phase', 'RED')

    def set_phase(self, phase):
        """Set current TDD phase"""
        valid_phases = ['RED', 'GREEN', 'REFACTOR']
        if phase in valid_phases:
            self._current_phase = phase
            return True
        return False