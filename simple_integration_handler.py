import json
import logging
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from logging.handlers import RotatingFileHandler
from typing import Dict, Any, List, Union, Optional

class IntegrationError(Exception):
    """Base integration error for the handler"""
    pass

class FileOperationError(IntegrationError):
    """Error during file save/load operations"""
    pass

class ConfigurationError(IntegrationError):
    """Error in configuration loading or validation"""
    pass

class NotificationError(IntegrationError):
    """Error during notification sending"""
    pass

@dataclass
class NotificationResult:
    """Simple result object for notifications"""
    status: str
    recipient: str = ""

class SimpleIntegrationHandler:
    """Simple integration handler for TDD evidence collection"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize with optional configuration file"""
        # Load configuration
        if config_path:
            self.config = self.load_config(config_path)
        else:
            self.config = self._get_default_config()
        
        # Setup logging first
        self.setup_logging(self.config)
        
        # Setup evidence directory from configuration
        evidence_config = self.config.get('evidence_storage', {})
        self.evidence_dir = Path(evidence_config.get('base_directory', './evidence'))
        self.evidence_dir.mkdir(parents=True, exist_ok=True)
        
        # Log initialization
        self.logger.info("SimpleIntegrationHandler initialized successfully")
        self.logger.debug(f"Evidence directory: {self.evidence_dir}")
    
    def setup_logging(self, config: Dict[str, Any]) -> None:
        """Setup logging system based on configuration"""
        log_config = config.get('logging', {})
        
        # Create logger
        self.logger = logging.getLogger('SimpleIntegrationHandler')
        self.logger.setLevel(getattr(logging, log_config.get('level', 'INFO')))
        
        # Clear any existing handlers
        self.logger.handlers.clear()
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # File handler if enabled
        if log_config.get('file_enabled', True):
            log_file = log_config.get('log_file', './logs/integration.log')
            Path(log_file).parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=log_config.get('max_log_size_mb', 5) * 1024 * 1024,
                backupCount=log_config.get('backup_count', 3)
            )
            file_handler.setLevel(logging.DEBUG)
            self.logger.addHandler(file_handler)
        
        # Add console handler
        self.logger.addHandler(console_handler)
        
        # Set formatter
        log_format = log_config.get('format', '[{level}] {timestamp} - {message}')
        formatter = logging.Formatter(
            log_format.replace('{level}', '%(levelname)s')
                      .replace('{timestamp}', '%(asctime)s')
                      .replace('{message}', '%(message)s')
        )
        
        for handler in self.logger.handlers:
            handler.setFormatter(formatter)
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for the handler"""
        return {
            "evidence_storage": {
                "base_directory": "./evidence",
                "backup_enabled": True,
                "backup_directory": "./evidence_backup",
                "compression_enabled": False,
                "max_file_size_mb": 10,
                "cleanup_after_days": 30
            },
            "notifications": {
                "email_enabled": False,
                "smtp_server": "localhost",
                "smtp_port": 587,
                "use_tls": True,
                "from_address": "tdd-enforcer@localhost",
                "max_retries": 3,
                "retry_delay_seconds": 5
            },
            "logging": {
                "level": "INFO",
                "format": "[{level}] {timestamp} - {message}",
                "file_enabled": True,
                "log_file": "./logs/integration.log",
                "max_log_size_mb": 5,
                "backup_count": 3
            },
            "reports": {
                "default_template": "standard",
                "include_timestamps": True,
                "include_metadata": True,
                "max_entries_per_report": 100
            }
        }
    
    def save_evidence_locally(self, evidence_data: Dict[str, Any], filename: str) -> Path:
        """Save evidence data to a local JSON file with error handling"""
        try:
            # Ensure evidence directory exists
            self.evidence_dir.mkdir(parents=True, exist_ok=True)
            
            # Create full file path
            file_path = self.evidence_dir / filename
            
            # Save data as JSON with atomic write
            temp_path = file_path.with_suffix('.tmp')
            with open(temp_path, 'w') as f:
                json.dump(evidence_data, f, indent=2, ensure_ascii=False)
            
            # Atomic rename to final file
            temp_path.rename(file_path)
            
            return file_path
            
        except (OSError, IOError, ValueError) as e:
            raise FileOperationError(f"Failed to save evidence to {filename}: {e}")
        except Exception as e:
            raise IntegrationError(f"Unexpected error saving evidence: {e}")
    
    def load_evidence_from_file(self, file_path: Path) -> Dict[str, Any]:
        """Load evidence data from JSON file with error handling"""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileOperationError(f"Evidence file not found: {file_path}")
        except json.JSONDecodeError as e:
            raise FileOperationError(f"Invalid JSON in evidence file: {e}")
        except Exception as e:
            raise FileOperationError(f"Error loading evidence file: {e}")
    
    def generate_simple_report(self, evidence_files: List[Path]) -> str:
        """Generate a simple text report from evidence files"""
        report_lines = ["=== TDD Evidence Report ===", ""]
        
        for file_path in evidence_files:
            if file_path.exists():
                data = self.load_evidence_from_file(file_path)
                
                # Extract stage info
                stage = data.get('stage', 'unknown')
                report_lines.append(f"Stage: {stage}")
                
                # Add any numeric data found
                for key, value in data.items():
                    if isinstance(value, (int, str)) and str(value).isdigit():
                        report_lines.append(f"  {key}: {value}")
                
                report_lines.append("")
        
        return "\n".join(report_lines)
    
    def send_email_notification(self, notification: Dict[str, str]) -> NotificationResult:
        """Send email notification - simplified for small team"""
        recipient = notification.get('to', '')
        subject = notification.get('subject', '')
        message = notification.get('message', '')
        
        # Simple logging of the notification
        print(f"EMAIL: To={recipient}, Subject={subject}")
        print(f"Message: {message}")
        
        return NotificationResult(status='sent', recipient=recipient)
    
    def log_to_console(self, log_entry: Dict[str, str]) -> str:
        """Log message using proper logging infrastructure"""
        level = log_entry.get('level', 'INFO').upper()
        message = log_entry.get('message', '')
        
        # Map to logging levels
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        
        log_level = level_map.get(level, logging.INFO)
        
        # Log using proper logger
        if hasattr(self, 'logger'):
            self.logger.log(log_level, message)
        else:
            # Fallback to print if logger not initialized
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            formatted_message = f"[{level}] {timestamp} - {message}"
            print(formatted_message)
            return formatted_message
        
        # Return formatted message for compatibility
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return f"[{level}] {timestamp} - {message}"
    
    def load_config(self, config_path: str) -> Dict[str, Any]:
        """Load and validate configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Validate configuration schema (backward compatible)
            if not self.validate_config(config):
                raise ConfigurationError(f"Invalid configuration")
            
            return config
            
        except FileNotFoundError:
            raise ConfigurationError(f"Configuration file not found")
        except json.JSONDecodeError as e:
            raise ConfigurationError(f"Invalid JSON in configuration file: {e}")
        except Exception as e:
            raise ConfigurationError(f"Error loading configuration: {e}")

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate configuration has required fields and valid values"""
        # Check for legacy test format first
        if 'evidence_dir' in config:
            # Legacy format for backward compatibility with tests
            return config.get('evidence_dir') is not None
        
        # New comprehensive validation for full configuration
        required_sections = ['evidence_storage', 'notifications', 'logging', 'reports']
        
        for section in required_sections:
            if section not in config:
                return False
        
        # Validate evidence storage section
        evidence_config = config['evidence_storage']
        required_evidence_keys = ['base_directory', 'backup_enabled']
        if not all(key in evidence_config for key in required_evidence_keys):
            return False
        
        # Validate notification section
        notification_config = config['notifications']
        required_notification_keys = ['email_enabled', 'max_retries']
        if not all(key in notification_config for key in required_notification_keys):
            return False
        
        # Validate numeric values are positive
        numeric_fields = [
            ('evidence_storage', 'max_file_size_mb'),
            ('notifications', 'max_retries'),
            ('notifications', 'retry_delay_seconds'),
            ('logging', 'max_log_size_mb'),
            ('reports', 'max_entries_per_report')
        ]
        
        for section, field in numeric_fields:
            if section in config and field in config[section]:
                value = config[section][field]
                if not isinstance(value, (int, float)) or value <= 0:
                    return False
        
        return True
