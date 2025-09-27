"""
Compliance Reporter for Evidence Collection System
Generates comprehensive compliance reports and metrics.
Enhanced with logging, configuration management, error handling, and performance monitoring.
"""
import json
import logging
import time
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path


class ComplianceReporterError(Exception):
    """Base exception for ComplianceReporter operations"""
    pass


class ConfigurationError(ComplianceReporterError):
    """Raised when configuration issues occur"""
    pass


class ReportGenerationError(ComplianceReporterError):
    """Raised when report generation fails"""
    pass


class ComplianceReporter:
    """Generate compliance reports for stage gate evidence collection
    
    Enhanced with:
    - External configuration management
    - Structured logging
    - Performance monitoring
    - Error handling
    - Type safety
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize ComplianceReporter with optional external configuration
        
        Args:
            config_path: Path to external configuration file (optional)
        """
        self.reports: List[Dict[str, Any]] = []
        self.operation_count = 0
        
        # Load configuration
        if config_path and Path(config_path).exists():
            self.config = self._load_config(config_path)
        else:
            self.config = self._get_default_config()
        
        # Setup output directory
        self.output_dir = Path(self.config.get('output_directory', './compliance_reports'))
        self.output_dir.mkdir(exist_ok=True, parents=True)
        
        # Setup logging
        self._setup_logging()
        
        # Performance tracking
        self.start_time = time.time()
        
        self.logger.info(f"ComplianceReporter initialized with config from {config_path or 'defaults'}")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from external JSON file
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            Configuration dictionary
            
        Raises:
            ConfigurationError: If configuration loading fails
        """
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            return config
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise ConfigurationError(f"Failed to load configuration from {config_path}: {e}")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration settings
        
        Returns:
            Default configuration dictionary
        """
        return {
            'output_directory': './compliance_reports',
            'thresholds': {
                'excellent': 95.0,
                'good': 85.0,
                'acceptable': 70.0
            },
            'logging': {
                'level': 'INFO',
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            }
        }
    
    def _setup_logging(self) -> None:
        """Setup structured logging for ComplianceReporter"""
        self.logger = logging.getLogger(__name__)
        
        # Only add handler if none exists (prevent duplicate handlers)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                self.config.get('logging', {}).get('format', 
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        
        log_level = self.config.get('logging', {}).get('level', 'INFO')
        self.logger.setLevel(getattr(logging, log_level, logging.INFO))
        
    def generate_compliance_report(self, evidence_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive compliance report from evidence with enhanced monitoring
        
        Args:
            evidence_data: Dictionary containing evidence and compliance information
            
        Returns:
            Dict containing formatted compliance report
            
        Raises:
            ReportGenerationError: If report generation fails
        """
        start_time = time.time()
        
        try:
            # Increment operation counter
            self.operation_count += 1
            
            # Generate unique report ID
            report_id = f"RPT_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{self.operation_count:03d}"
            
            self.logger.info(f"Generating compliance report {report_id}")
            
            # Extract compliance metrics from evidence data
            compliance_score = evidence_data.get('compliance_score', 0.0)
            requirements_passed = evidence_data.get('requirements_passed', 0)
            requirements_total = evidence_data.get('requirements_total', 0)
            stage_gates = evidence_data.get('stage_gates', {})
            
            # Calculate additional metrics
            pass_rate = (requirements_passed / requirements_total * 100) if requirements_total > 0 else 0.0
            
            # Generate report structure
            report = {
                'report_id': report_id,
                'timestamp': datetime.now().isoformat(),
                'overall_compliance_score': compliance_score,
                'pass_rate_percentage': round(pass_rate, 1),
                'requirements_passed': requirements_passed,
                'requirements_total': requirements_total,
                'stage_gates_status': stage_gates,
                'compliance_level': self._determine_compliance_level(compliance_score),
                'recommendations': self._generate_recommendations(evidence_data),
                'summary': f"Compliance Score: {compliance_score}% | {requirements_passed}/{requirements_total} requirements passed",
                'generation_time_ms': round((time.time() - start_time) * 1000, 2),
                'operation_number': self.operation_count
            }
            
            # Store report
            self.reports.append(report)
            
            processing_time = (time.time() - start_time) * 1000
            self.logger.info(f"Report {report_id} generated in {processing_time:.2f}ms")
            
            return report
            
        except Exception as e:
            self.logger.error(f"Failed to generate compliance report: {e}")
            raise ReportGenerationError(f"Report generation failed: {e}")
    
    def export_report(self, report_id: str, file_path: str) -> bool:
        """
        Export report to file with enhanced error handling
        
        Args:
            report_id: ID of the report to export
            file_path: Path where to save the report
            
        Returns:
            True if export successful, False otherwise
        """
        try:
            self.logger.info(f"Exporting report {report_id} to {file_path}")
            
            report = next((r for r in self.reports if r['report_id'] == report_id), None)
            if not report:
                self.logger.error(f"Report {report_id} not found")
                return False
            
            output_path = self.output_dir / file_path
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            self.logger.info(f"Report {report_id} exported successfully to {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export report {report_id}: {e}")
            return False
    
    def _determine_compliance_level(self, score: float) -> str:
        """
        Determine compliance level based on score and thresholds
        
        Args:
            score: Compliance score percentage
            
        Returns:
            Compliance level string
        """
        thresholds = self.config.get('thresholds', {})
        
        if score >= thresholds.get('excellent', 95.0):
            return 'EXCELLENT'
        elif score >= thresholds.get('good', 85.0):
            return 'GOOD'
        elif score >= thresholds.get('acceptable', 70.0):
            return 'ACCEPTABLE'
        else:
            return 'NEEDS_IMPROVEMENT'
    
    def _generate_recommendations(self, evidence_data: Dict[str, Any]) -> List[str]:
        """
        Generate recommendations based on evidence data
        
        Args:
            evidence_data: Evidence data to analyze
            
        Returns:
            List of recommendation strings
        """
        recommendations = []
        compliance_score = evidence_data.get('compliance_score', 0.0)
        
        if compliance_score < 70:
            recommendations.append("CRITICAL: Immediate review required - compliance score below acceptable threshold")
        elif compliance_score < 85:
            recommendations.append("Consider implementing additional quality assurance measures")
        elif compliance_score < 95:
            recommendations.append("Good compliance - consider minor optimizations for excellence")
        else:
            recommendations.append("Excellent compliance - maintain current standards")
        
        # Stage-specific recommendations
        if evidence_data.get('requirements_passed', 0) == 0:
            recommendations.append("No requirements passed - comprehensive review needed")
        
        return recommendations
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get performance metrics for the compliance reporter
        
        Returns:
            Dictionary containing performance metrics
        """
        uptime = time.time() - self.start_time
        
        return {
            'operations_performed': self.operation_count,
            'uptime_seconds': round(uptime, 2),
            'reports_generated': len(self.reports),
            'average_processing_time_ms': round(
                sum(r.get('generation_time_ms', 0) for r in self.reports) / max(len(self.reports), 1), 2
            ),
            'memory_usage_reports': len(self.reports)
        }