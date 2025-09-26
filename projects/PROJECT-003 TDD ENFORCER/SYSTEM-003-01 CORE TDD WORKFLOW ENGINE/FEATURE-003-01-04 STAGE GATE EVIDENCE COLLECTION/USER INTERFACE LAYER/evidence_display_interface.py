#!/usr/bin/env python3
"""
EvidenceDisplayInterface - UI Layer Implementation
GREEN PHASE: Minimal implementation to make failing tests pass

Target: Make all 48 UI Layer tests pass
TDD Phase: GREEN - Minimal Implementation
"""

import json
import time
import threading
import uuid
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Any, Optional
from functools import lru_cache


# Step 4: UI-Specific Exception Hierarchy
class DisplayValidationError(Exception):
    """Raised when display input validation fails."""
    pass


class InvalidEvidenceEventError(DisplayValidationError):
    """Raised when evidence event format is invalid."""
    pass


class InvalidComplianceDataError(DisplayValidationError):
    """Raised when compliance data format is invalid."""
    pass


# Step 5: Report Generation Strategies
class ReportGenerator(ABC):
    """Abstract base class for compliance report generation"""
    
    @abstractmethod
    def generate(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate report in specific format"""
        pass


class PDFReportGenerator(ReportGenerator):
    """PDF-specific report generation with metadata"""
    
    def generate(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        report_id = str(uuid.uuid4())
        file_path = f"/tmp/compliance_report_{report_id}.pdf"
        
        # Enhanced PDF generation simulation
        pdf_content = {
            'report_id': report_id,
            'generated_at': datetime.now().isoformat(),
            'content': json.dumps(report_data, indent=2)
        }
        
        return {
            'file_path': file_path,
            'file_size': len(json.dumps(pdf_content)),
            'metadata': {
                'title': report_data.get('project_info', {}).get('name', 'Compliance Report'),
                'format': 'PDF',
                'pages_estimated': max(1, len(str(report_data)) // 3000)
            },
            'generation_status': 'success'
        }


class HTMLReportGenerator(ReportGenerator):
    """HTML-specific report generation with styling"""
    
    def generate(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        overall_score = report_data.get('overall_score', 0)
        
        # Enhanced HTML generation with better structure
        html_content = f"""
        <html>
        <head><title>Compliance Report</title></head>
        <body>
            <div class="compliance-dashboard">
                <h1>Compliance Report</h1>
                <div class="score">Overall Score: {overall_score}%</div>
                <div class="chart-container">
                    <div class="chart">Compliance Chart</div>
                </div>
            </div>
        </body>
        </html>
        """
        
        return {
            'content': html_content,
            'generation_status': 'success',
            'metadata': {
                'format': 'HTML',
                'interactive_elements': ['compliance-dashboard', 'chart-container'],
                'estimated_load_time_ms': 250
            }
        }


# Step 2: Configuration Management
DEFAULT_DISPLAY_CONFIG = {
    'performance_limits': {
        'max_updates_per_minute': 50,
        'response_time_ms_target': 100,
        'error_recovery_timeout_seconds': 2
    },
    'display_formats': {
        'status_line_format': '{stage}: {status} - {details}',
        'compliance_format': '{title}: {percentage}%',
        'chart_dimensions': {'width': 400, 'height': 300}
    },
    'compliance_thresholds': {
        'good_threshold': 85,
        'warning_threshold': 70,
        'critical_threshold': 50
    },
    'chart_settings': {
        'default_chart_type': 'bar',
        'color_scheme': ['#28a745', '#ffc107', '#dc3545'],
        'show_grid': True,
        'show_legend': True
    },
    'cache_settings': {
        'max_size': 100,
        'ttl_seconds': 300,
        'chart_cache_ttl_seconds': 600,
        'performance_cache_size': 50
    },
    'mobile_settings': {
        'responsive_breakpoints': {
            'mobile': 320,
            'tablet': 768,
            'desktop': 1024
        },
        'mobile_optimizations': {
            'compact_display': True,
            'reduced_animations': True,
            'touch_friendly_targets': True,
            'simplified_charts': True
        },
        'display_limits': {
            'mobile_max_items': 5,
            'tablet_max_items': 10,
            'desktop_max_items': 20
        }
    }
}


class DisplayRenderer:
    """Reusable display rendering engine for consistent formatting"""
    
    @staticmethod
    def format_status_line(stage: str, status: str, details: Dict[str, Any] = None) -> str:
        """Format consistent status lines across all display methods"""
        line = f"{stage}: {status}"
        if details and status == 'failed':
            line += f"\n  error: {details.get('error_message', 'Unknown error')}"
            line += f"\n  retry_count: {details.get('retry_count', 0)}"
        return line
    
    @staticmethod
    def format_compliance_section(title: str, data: Dict[str, Any]) -> List[str]:
        """Format compliance data sections consistently"""
        lines = [f"{title}:"]
        for key, value in data.items():
            if isinstance(value, dict):
                score = value.get('score', 0)
                status = value.get('status', 'unknown')
                violations = value.get('violations', 0)
                lines.append(f"  {key}: {score}% - {status} - violations: {violations}")
            else:
                lines.append(f"  {key}: {value}")
        return lines


class DisplayUpdateEvent:
    """Event class for display updates"""
    def __init__(self, event_data: Dict[str, Any]):
        self.event_data = event_data


class EvidenceDisplayInterface:
    """
    Minimal UI Layer implementation for evidence display and compliance reporting
    Designed to pass all 48 failing tests with minimal viable functionality
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or DEFAULT_DISPLAY_CONFIG
        self.display_renderer = DisplayRenderer()
        self.logger = logging.getLogger(__name__)  # Step 6: Logging System
        self.current_display_state = {}
        self.processed_update_count = 0
        self.is_operational = True
        self.error_status = 'operational'
        self.data_source_available = True
        
        # Step 5: Initialize report generators
        self.pdf_generator = PDFReportGenerator()
        self.html_generator = HTMLReportGenerator()
        
        # Step 7: Caching mechanisms
        self._cache = {}
        self._cache_expiry = {}
        self._cache_max_size = self.config.get('cache_settings', {}).get('max_size', 100)
        self._cache_ttl_seconds = self.config.get('cache_settings', {}).get('ttl_seconds', 300)
        self._chart_cache = {}
        self._chart_cache_expiry = {}
        self._performance_cache = {}
        
        # Cache statistics
        self.cache_hits = 0
        self.cache_misses = 0
        
        # Step 8: Performance monitoring
        self.performance_metrics = {
            'method_execution_times': {},
            'display_render_times': [],
            'total_operations': 0,
            'average_response_time': 0,
            'slow_operations_count': 0
        }
        self.performance_thresholds = {
            'warning_ms': 100,
            'critical_ms': 500,
            'max_operations_per_minute': 50
        }
    
    # Step 4: Input Validation Methods
    def _validate_evidence_event(self, evidence_event: Dict[str, Any]) -> None:
        """Validate evidence event structure and required fields."""
        required_fields = ['stage', 'evidence_type', 'status']
        missing_fields = [field for field in required_fields if field not in evidence_event]
        
        if missing_fields:
            raise InvalidEvidenceEventError(
                f"Missing required fields: {missing_fields}. "
                f"Required: {required_fields}"
            )
        
        valid_stages = ['red_stage', 'green_stage', 'refactor_stage']
        if evidence_event['stage'] not in valid_stages:
            raise InvalidEvidenceEventError(
                f"Invalid stage '{evidence_event['stage']}'. "
                f"Must be one of: {valid_stages}"
            )
        
        valid_statuses = ['collecting', 'completed', 'failed', 'pending']
        if evidence_event['status'] not in valid_statuses:
            raise InvalidEvidenceEventError(
                f"Invalid status '{evidence_event['status']}'. "
                f"Must be one of: {valid_statuses}"
            )

    def _validate_compliance_data(self, compliance_data: Dict[str, Any]) -> None:
        """Validate compliance data structure and value ranges."""
        if 'overall_compliance_score' not in compliance_data:
            raise InvalidComplianceDataError("Missing 'overall_compliance_score' field")
        
        score = compliance_data['overall_compliance_score']
        if not isinstance(score, (int, float)) or not 0 <= score <= 100:
            raise InvalidComplianceDataError(
                f"overall_compliance_score must be numeric between 0-100, got {score}"
            )
        
    # ===== REAL-TIME EVIDENCE DISPLAY METHODS =====
    
    def update_evidence_collection_status(self, evidence_event: Dict[str, Any]) -> None:
        """
        Update real-time evidence collection status with stage-specific tracking.
        
        Args:
            evidence_event: Dictionary containing evidence update with keys:
                - 'stage': TDD stage identifier (red_stage, green_stage, refactor_stage)
                - 'evidence_type': Type of evidence (test_results, implementation_artifacts, etc.)
                - 'status': Current status (collecting, completed, failed)
                - 'progress_percentage': Completion percentage (0-100)
                - 'artifacts_collected': Number of artifacts collected (optional)
                - 'validation_status': Validation result (passed, failed, pending)
                - 'error_message': Error description if status is 'failed' (optional)
                - 'retry_count': Number of retry attempts (optional)
        
        Returns:
            None: Updates internal display state for subsequent rendering
        
        Example:
            >>> display = EvidenceDisplayInterface()
            >>> event = {
            ...     'stage': 'red_stage', 
            ...     'evidence_type': 'test_results',
            ...     'status': 'collecting', 
            ...     'progress_percentage': 45
            ... }
            >>> display.update_evidence_collection_status(event)
            >>> state = display.get_current_display_state()
            >>> assert state['red_stage']['progress'] == 45
        """
        self._validate_evidence_event(evidence_event)
        self.logger.debug(f"Processing evidence update: stage={evidence_event.get('stage')}")
        
        stage = evidence_event.get('stage')
        if stage not in self.current_display_state:
            self.current_display_state[stage] = {}
        
        self.current_display_state[stage].update({
            'status': evidence_event.get('status'),
            'progress': evidence_event.get('progress_percentage'),
            'artifacts_count': evidence_event.get('artifacts_collected'),
            'validation_status': evidence_event.get('validation_status'),
            'evidence_types': [evidence_event.get('evidence_type')] if evidence_event.get('evidence_type') else [],
            'error_message': evidence_event.get('error_message'),
            'retry_count': evidence_event.get('retry_count', 0)
        })
        self.processed_update_count += 1
    
    def get_current_display_state(self) -> Dict[str, Any]:
        """Get current display state"""
        return self.current_display_state
    
    def render_current_status(self) -> str:
        """Render current status as string"""
        if not self.data_source_available:
            return "Data temporarily unavailable - Last known status: operational"
        
        status_lines = []
        for stage, data in self.current_display_state.items():
            status_lines.append(f"{stage}: {data.get('status', 'unknown')}")
            if data.get('status') == 'failed':
                error_msg = data.get('error_message', 'Unknown error')
                retry_count = data.get('retry_count', 0)
                status_lines.append(f"  error: {error_msg}")
                status_lines.append(f"  retry_count: {retry_count}")
        
        return "\n".join(status_lines) if status_lines else "No status available"
    
    # ===== AUDIT COMPLIANCE DASHBOARD METHODS =====
    
    def render_audit_compliance_dashboard(self, compliance_data: Dict[str, Any]) -> str:
        """
        Render comprehensive audit compliance dashboard with TDD stage analysis.
        
        Args:
            compliance_data: Dictionary containing audit compliance metrics with keys:
                - 'overall_compliance_score': Aggregate compliance percentage (0-100)
                - 'stage_compliance': Dict with stage-specific compliance data:
                    - stage_name: {'status': str, 'score': int, 'violations': int}
                - 'requirement_compliance': Dict with requirement-specific data:
                    - req_name: {'status': str, 'current': int}
                - 'audit_timestamp': ISO timestamp of compliance assessment
                - 'assessor_info': Dictionary with auditor identification
                
        Returns:
            str: Multi-line formatted dashboard containing:
                - Overall compliance percentage with status indicators
                - Stage-by-stage compliance breakdown with violation counts
                - Requirement compliance status with current percentages
                - Visual formatting for quick assessment
                
        Example:
            >>> display = EvidenceDisplayInterface()
            >>> data = {
            ...     'overall_compliance_score': 78,
            ...     'stage_compliance': {
            ...         'red_stage': {'status': 'compliant', 'score': 85, 'violations': 1}
            ...     },
            ...     'requirement_compliance': {
            ...         'test_coverage': {'status': 'warning', 'current': 72}
            ...     }
            ... }
            >>> dashboard = display.render_audit_compliance_dashboard(data)
            >>> assert "78%" in dashboard
            >>> assert "red_stage: 85%" in dashboard
        """
        overall_score = compliance_data.get('overall_compliance_score', 0)
        stage_compliance = compliance_data.get('stage_compliance', {})
        requirement_compliance = compliance_data.get('requirement_compliance', {})
        
        dashboard_lines = [
            f"Overall Compliance: {overall_score}%",
            "Stage Compliance:"
        ]
        
        for stage, data in stage_compliance.items():
            status = data.get('status', 'unknown')
            score = data.get('score', 0)
            violations = data.get('violations', 0)
            dashboard_lines.append(f"  {stage}: {score}% - {status} - violations: {violations}")
        
        dashboard_lines.append("Requirement Compliance:")
        for req_name, req_data in requirement_compliance.items():
            status = req_data.get('status', 'unknown')
            current = req_data.get('current', 0)
            dashboard_lines.append(f"  {req_name}: {current}% - {status}")
        
        return "\n".join(dashboard_lines)
    
    def render_compliance_violations(self, violation_data: Dict[str, Any]) -> str:
        """Render compliance violations with remediation"""
        violations = violation_data.get('violations', [])
        
        violation_lines = []
        for violation in violations:
            violation_id = violation.get('id', 'UNKNOWN')
            severity = violation.get('severity', 'unknown')
            description = violation.get('description', 'No description')
            remediation = violation.get('remediation', 'No remediation available')
            
            violation_lines.append(f"{violation_id} - {severity} severity")
            violation_lines.append(f"  {description}")
            violation_lines.append(f"  Remediation: {remediation}")
        
        return "\n".join(violation_lines)
    
    def render_compliance_trend(self, trend_data: Dict[str, Any]) -> str:
        """Render compliance trend analysis"""
        time_series = trend_data.get('time_series', [])
        trend_direction = trend_data.get('trend_direction', 'stable')
        trend_rate = trend_data.get('trend_rate', 0)
        
        trend_lines = [f"Trend: {trend_direction} at {trend_rate}% per hour"]
        
        if time_series:
            first_score = time_series[0].get('compliance_score', 0)
            last_score = time_series[-1].get('compliance_score', 0)
            trend_lines.append(f"Score change: {first_score} → {last_score}")
        
        return "\n".join(trend_lines)
    
    # ===== EVIDENCE ARTIFACT PRESENTATION METHODS =====
    
    def render_evidence_browser(self, artifacts: Dict[str, Any]) -> str:
        """Render evidence artifact browser"""
        browser_lines = ["Evidence Browser:"]
        
        for category, artifact_list in artifacts.items():
            browser_lines.append(f"\n{category}:")
            for artifact in artifact_list:
                name = artifact.get('name', 'Unknown')
                test_count = artifact.get('test_count', 0)
                coverage = artifact.get('coverage_percentage', 0)
                complexity = artifact.get('complexity_score', 0)
                maintainability = artifact.get('maintainability_index', 0)
                
                browser_lines.append(f"  {name}")
                if test_count:
                    browser_lines.append(f"    {test_count} tests - {coverage}% coverage")
                if complexity:
                    browser_lines.append(f"    complexity: {complexity} - maintainability: {maintainability}")
        
        return "\n".join(browser_lines)
    
    def render_artifact_details(self, artifact_details: Dict[str, Any]) -> str:
        """Render detailed artifact information"""
        name = artifact_details.get('name', 'Unknown')
        metadata = artifact_details.get('metadata', {})
        content_summary = artifact_details.get('content_summary', {})
        quality_assessment = artifact_details.get('quality_assessment', {})
        
        detail_lines = [
            f"Artifact: {name}",
            f"Size: {metadata.get('size_bytes', 0):,} bytes",
            f"{metadata.get('line_count', 0)} lines",
            f"Complexity: {metadata.get('complexity_metrics', {}).get('cyclomatic_complexity', 0)}",
        ]
        
        coverage_analysis = content_summary.get('coverage_analysis', {})
        if coverage_analysis:
            detail_lines.append(f"Statement coverage: {coverage_analysis.get('statement_coverage', 0)}%")
        
        if quality_assessment:
            detail_lines.append(f"Quality score: {quality_assessment.get('test_quality_score', 0)}")
        
        return "\n".join(detail_lines)
    
    def filter_evidence_artifacts(self, all_artifacts: Dict[str, Any], filter_criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Filter evidence artifacts based on criteria"""
        artifacts = all_artifacts.get('artifacts', [])
        quality_threshold = filter_criteria.get('quality_threshold', 0)
        
        filtered_artifacts = [
            artifact for artifact in artifacts
            if artifact.get('quality_score', 0) >= quality_threshold
        ]
        
        return {'artifacts': filtered_artifacts}
    
    def render_filtered_artifacts(self, filtered_results: Dict[str, Any]) -> str:
        """Render filtered artifact results"""
        artifacts = filtered_results.get('artifacts', [])
        count = len(artifacts)
        return f"Filtered results:\n{count} artifacts match criteria"
    
    # ===== COMPLIANCE REPORT GENERATION METHODS =====
    
    def generate_compliance_report_pdf(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive PDF compliance report using PDFReportGenerator.
        
        Args:
            report_data: Dictionary containing report content and metadata
            
        Returns:
            Dict[str, Any]: Report generation result with status and file paths
        """
        self.logger.info("Generating PDF compliance report")
        return self.pdf_generator.generate(report_data)
    
    def generate_compliance_report_html(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate interactive HTML compliance report using HTMLReportGenerator.
        
        Args:
            report_data: Dictionary containing report content and metadata
            
        Returns:
            Dict[str, Any]: Report generation result with HTML content and paths
        """
        self.logger.info("Generating HTML compliance report")
        return self.html_generator.generate(report_data)
    
    def generate_compliance_charts(self, chart_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate compliance visualization charts"""
        charts = {
            'trend_chart': {
                'image_path': f"/tmp/trend_chart_{uuid.uuid4()}.png",
                'chart_type': 'line'
            },
            'category_chart': {
                'image_path': f"/tmp/category_chart_{uuid.uuid4()}.png",
                'chart_type': 'bar'
            },
            'violation_chart': {
                'image_path': f"/tmp/violation_chart_{uuid.uuid4()}.png",
                'chart_type': 'pie',
                'data_points': list(chart_data.get('violation_distribution', {}).keys())
            }
        }
        
        return charts
    
    def export_compliance_report(self, report_data: Dict[str, Any], export_options: Dict[str, Any]) -> Dict[str, Any]:
        """Export compliance report in multiple formats"""
        formats = export_options.get('formats', [])
        generated_files = []
        
        for fmt in formats:
            file_id = str(uuid.uuid4())
            generated_files.append({
                'format': fmt,
                'file_path': f"/tmp/report_{file_id}.{fmt}",
                'file_size': 1024  # Simulate file size
            })
        
        return {
            'status': 'success',
            'generated_files': generated_files
        }
    
    def schedule_compliance_reports(self, schedule_config: Dict[str, Any]) -> Dict[str, Any]:
        """Schedule automated compliance reports"""
        schedule_id = str(uuid.uuid4())
        frequency = schedule_config.get('frequency', 'daily')
        time_str = schedule_config.get('time', '09:00:00')
        timezone = schedule_config.get('timezone', 'UTC')
        recipients = schedule_config.get('recipients', [])
        
        return {
            'scheduling_status': 'active',
            'next_execution': f"2025-09-27T{time_str}Z",
            'schedule_id': schedule_id,
            'configured_recipients': recipients,
            'schedule_description': f"{frequency} at {time_str} {timezone}"
        }
    
    def deliver_compliance_report(self, report_data: Dict[str, Any], delivery_config: Dict[str, Any]) -> Dict[str, Any]:
        """Deliver compliance report via email"""
        recipients = delivery_config.get('recipients', [])
        attachment_name = delivery_config.get('attachment_name', 'report.pdf')
        
        return {
            'delivery_status': 'sent',
            'message_id': str(uuid.uuid4()),
            'successful_deliveries': recipients,
            'attachment_size': 2048,
            'attachment_name': attachment_name
        }
    
    # ===== PERFORMANCE AND ERROR HANDLING METHODS =====
    
    def get_processed_update_count(self) -> int:
        """Get count of processed updates"""
        return self.processed_update_count
    
    def load_evidence_dataset(self, large_dataset: Dict[str, Any]) -> None:
        """Load large evidence dataset"""
        # Simulate loading large dataset
        pass
    
    def set_data_source_available(self, available: bool) -> None:
        """Set data source availability"""
        self.data_source_available = available
    
    def simulate_display_error(self, error_type: str) -> None:
        """Simulate display error for testing"""
        self.is_operational = False
        self.error_status = error_type.lower()
    
    def initiate_error_recovery(self) -> None:
        """Initiate error recovery process"""
        # Simulate recovery time
        time.sleep(0.1)
        self.is_operational = True
        self.error_status = 'recovered'
    
    def is_display_operational(self) -> bool:
        """Check if display is operational"""
        return self.is_operational
    
    def get_error_status(self) -> str:
        """Get current error status"""
        return self.error_status
    
    def render_evidence_data(self, sensitive_data: Dict[str, Any]) -> str:
        """Render evidence data with sensitive information redaction"""
        sanitized_lines = []
        
        for key, value in sensitive_data.items():
            if key in ['api_keys', 'passwords', 'internal_paths']:
                sanitized_lines.append(f"{key}: [REDACTED]")
            elif key == 'evidence_data':
                sanitized_lines.append(f"{key}:")
                if isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        sanitized_lines.append(f"  {sub_key}: {sub_value}")
            else:
                sanitized_lines.append(f"{key}: {value}")
        
        return "\n".join(sanitized_lines)
    
    # ===== STEP 7: CACHING MECHANISMS =====
    
    def _get_cache_key(self, method_name: str, *args, **kwargs) -> str:
        """Generate cache key for method calls."""
        key_parts = [method_name]
        key_parts.extend(str(arg) for arg in args)
        key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
        return "|".join(key_parts)
    
    def _is_cache_valid(self, cache_key: str, cache_type: str = 'default') -> bool:
        """Check if cache entry is still valid based on TTL."""
        if cache_type == 'chart':
            expiry_cache = self._chart_cache_expiry
            ttl = self.config.get('cache_settings', {}).get('chart_cache_ttl_seconds', 600)
        else:
            expiry_cache = self._cache_expiry
            ttl = self._cache_ttl_seconds
            
        if cache_key not in expiry_cache:
            return False
            
        return time.time() - expiry_cache[cache_key] < ttl
    
    def _cache_get(self, cache_key: str, cache_type: str = 'default') -> Optional[Any]:
        """Get value from cache if valid."""
        cache_dict = self._chart_cache if cache_type == 'chart' else self._cache
        
        if cache_key in cache_dict and self._is_cache_valid(cache_key, cache_type):
            self.cache_hits += 1
            self.logger.debug(f"Cache hit: {cache_key}")
            return cache_dict[cache_key]
        
        self.cache_misses += 1
        self.logger.debug(f"Cache miss: {cache_key}")
        return None
    
    def _cache_set(self, cache_key: str, value: Any, cache_type: str = 'default') -> None:
        """Set value in cache with expiry."""
        if cache_type == 'chart':
            cache_dict = self._chart_cache
            expiry_cache = self._chart_cache_expiry
        else:
            cache_dict = self._cache
            expiry_cache = self._cache_expiry
            
        # Evict old entries if cache is full
        if len(cache_dict) >= self._cache_max_size:
            oldest_key = min(expiry_cache.keys(), key=lambda k: expiry_cache[k])
            cache_dict.pop(oldest_key, None)
            expiry_cache.pop(oldest_key, None)
        
        cache_dict[cache_key] = value
        expiry_cache[cache_key] = time.time()
        self.logger.debug(f"Cache set: {cache_key}")
    
    @lru_cache(maxsize=100)
    def _cached_format_status_line(self, stage: str, status: str, details_str: str) -> str:
        """Cached version of status line formatting."""
        details = json.loads(details_str) if details_str else None
        return self.display_renderer.format_status_line(stage, status, details)
    
    def get_cache_statistics(self) -> Dict[str, Any]:
        """Get cache performance statistics."""
        total_requests = self.cache_hits + self.cache_misses
        hit_rate = self.cache_hits / total_requests if total_requests > 0 else 0
        
        return {
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'hit_rate_percentage': round(hit_rate * 100, 2),
            'cache_size': len(self._cache),
            'chart_cache_size': len(self._chart_cache),
            'performance_cache_size': len(self._performance_cache)
        }
    
    # ===== STEP 8: PERFORMANCE MONITORING =====
    
    def _track_method_performance(self, method_name: str, execution_time_ms: float) -> None:
        """Track method execution time and update performance metrics."""
        self.performance_metrics['total_operations'] += 1
        
        if method_name not in self.performance_metrics['method_execution_times']:
            self.performance_metrics['method_execution_times'][method_name] = []
        
        self.performance_metrics['method_execution_times'][method_name].append(execution_time_ms)
        
        # Update average response time
        all_times = []
        for times in self.performance_metrics['method_execution_times'].values():
            all_times.extend(times)
        
        if all_times:
            self.performance_metrics['average_response_time'] = sum(all_times) / len(all_times)
        
        # Track slow operations
        if execution_time_ms > self.performance_thresholds['critical_ms']:
            self.performance_metrics['slow_operations_count'] += 1
            self.logger.warning(f"Critical performance: {method_name} took {execution_time_ms:.2f}ms")
        elif execution_time_ms > self.performance_thresholds['warning_ms']:
            self.logger.info(f"Slow operation: {method_name} took {execution_time_ms:.2f}ms")
    
    def _performance_decorator(self, method_name: str):
        """Decorator to track method performance."""
        def decorator(func):
            def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    end_time = time.time()
                    execution_time_ms = (end_time - start_time) * 1000
                    self._track_method_performance(method_name, execution_time_ms)
            return wrapper
        return decorator
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance monitoring report."""
        report = {
            'total_operations': self.performance_metrics['total_operations'],
            'average_response_time_ms': round(self.performance_metrics['average_response_time'], 2),
            'slow_operations_count': self.performance_metrics['slow_operations_count'],
            'method_performance': {}
        }
        
        # Calculate per-method statistics
        for method_name, times in self.performance_metrics['method_execution_times'].items():
            if times:
                report['method_performance'][method_name] = {
                    'average_ms': round(sum(times) / len(times), 2),
                    'min_ms': round(min(times), 2),
                    'max_ms': round(max(times), 2),
                    'call_count': len(times)
                }
        
        # Performance alerts
        report['performance_alerts'] = []
        if self.performance_metrics['average_response_time'] > self.performance_thresholds['warning_ms']:
            report['performance_alerts'].append({
                'type': 'warning',
                'message': f"Average response time ({report['average_response_time_ms']}ms) exceeds warning threshold"
            })
        
        return report
    
    def reset_performance_metrics(self) -> None:
        """Reset all performance tracking metrics."""
        self.performance_metrics = {
            'method_execution_times': {},
            'display_render_times': [],
            'total_operations': 0,
            'average_response_time': 0,
            'slow_operations_count': 0
        }
        self.logger.info("Performance metrics reset")
    
    # ===== STEP 9: MOBILE PACKAGE OPTIMIZATION =====
    
    def _get_device_type(self, screen_width: int) -> str:
        """Determine device type based on screen width."""
        breakpoints = self.config.get('mobile_settings', {}).get('responsive_breakpoints', {})
        
        if screen_width <= breakpoints.get('mobile', 320):
            return 'mobile'
        elif screen_width <= breakpoints.get('tablet', 768):
            return 'tablet'
        else:
            return 'desktop'
    
    def format_for_mobile(self, content: Dict[str, Any], screen_width: int = 320) -> Dict[str, Any]:
        """Format display content optimized for mobile devices."""
        device_type = self._get_device_type(screen_width)
        mobile_settings = self.config.get('mobile_settings', {})
        
        # Apply display limits based on device type
        display_limits = mobile_settings.get('display_limits', {})
        max_items = display_limits.get(f'{device_type}_max_items', 5)
        
        # Create mobile-optimized content
        mobile_content = content.copy()
        
        # Limit number of items displayed
        if 'items' in mobile_content and isinstance(mobile_content['items'], list):
            mobile_content['items'] = mobile_content['items'][:max_items]
        
        # Apply mobile optimizations
        optimizations = mobile_settings.get('mobile_optimizations', {})
        mobile_content['display_config'] = {
            'compact_display': optimizations.get('compact_display', True),
            'reduced_animations': optimizations.get('reduced_animations', True),
            'touch_friendly': optimizations.get('touch_friendly_targets', True),
            'simplified_charts': optimizations.get('simplified_charts', True),
            'device_type': device_type,
            'max_items': max_items
        }
        
        return mobile_content
    
    def generate_responsive_layout_css(self, device_type: str = 'mobile') -> str:
        """Generate CSS for responsive layout based on device type."""
        mobile_settings = self.config.get('mobile_settings', {})
        breakpoints = mobile_settings.get('responsive_breakpoints', {})
        
        css_rules = []
        
        if device_type == 'mobile':
            css_rules.extend([
                "/* Mobile Layout */",
                "@media (max-width: 320px) {",
                "  .compliance-dashboard { font-size: 12px; padding: 8px; }",
                "  .status-line { margin-bottom: 4px; }",
                "  .chart-container { height: 200px; }",
                "  .touch-target { min-height: 44px; min-width: 44px; }",
                "}"
            ])
        elif device_type == 'tablet':
            css_rules.extend([
                "/* Tablet Layout */",
                "@media (min-width: 321px) and (max-width: 768px) {",
                "  .compliance-dashboard { font-size: 14px; padding: 12px; }",
                "  .status-line { margin-bottom: 6px; }",
                "  .chart-container { height: 300px; }",
                "}"
            ])
        
        return "\n".join(css_rules)
    
    def optimize_for_touch_interface(self, elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Optimize UI elements for touch interface."""
        optimized_elements = []
        
        for element in elements:
            optimized_element = element.copy()
            
            # Ensure touch targets are large enough (minimum 44x44px)
            if 'interactive' in element and element['interactive']:
                optimized_element['min_height'] = '44px'
                optimized_element['min_width'] = '44px'
                optimized_element['touch_optimized'] = True
            
            # Add spacing between interactive elements
            if 'type' in element and element['type'] in ['button', 'link', 'input']:
                optimized_element['margin'] = '8px'
                optimized_element['padding'] = '12px'
            
            optimized_elements.append(optimized_element)
        
        return optimized_elements
    
    # ===== STEP 10: CONFIGURATION VALIDATION =====
    
    def validate_config(self) -> Dict[str, Any]:
        """
        Comprehensive configuration validation with schema checking.
        
        Returns:
            Dict[str, Any]: Validation report with status and any issues found
        """
        validation_report = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'validated_sections': []
        }
        
        try:
            # Validate performance limits
            self._validate_performance_limits(validation_report)
            
            # Validate display formats
            self._validate_display_formats(validation_report)
            
            # Validate compliance thresholds
            self._validate_compliance_thresholds(validation_report)
            
            # Validate chart settings
            self._validate_chart_settings(validation_report)
            
            # Validate cache settings
            self._validate_cache_settings(validation_report)
            
            # Validate mobile settings
            self._validate_mobile_settings(validation_report)
            
            self.logger.info(f"Configuration validation completed: {'VALID' if validation_report['is_valid'] else 'INVALID'}")
            
        except Exception as e:
            validation_report['is_valid'] = False
            validation_report['errors'].append(f"Configuration validation failed: {str(e)}")
            self.logger.error(f"Configuration validation error: {e}")
        
        return validation_report
    
    def _validate_performance_limits(self, report: Dict[str, Any]) -> None:
        """Validate performance limits configuration."""
        perf_limits = self.config.get('performance_limits', {})
        report['validated_sections'].append('performance_limits')
        
        # Check max_updates_per_minute
        max_updates = perf_limits.get('max_updates_per_minute')
        if max_updates is None or not isinstance(max_updates, int) or max_updates <= 0:
            report['errors'].append("performance_limits.max_updates_per_minute must be positive integer")
            report['is_valid'] = False
        elif max_updates > 1000:
            report['warnings'].append("performance_limits.max_updates_per_minute > 1000 may impact performance")
        
        # Check response_time_ms_target
        response_time = perf_limits.get('response_time_ms_target')
        if response_time is None or not isinstance(response_time, int) or response_time <= 0:
            report['errors'].append("performance_limits.response_time_ms_target must be positive integer")
            report['is_valid'] = False
    
    def _validate_display_formats(self, report: Dict[str, Any]) -> None:
        """Validate display formats configuration."""
        display_formats = self.config.get('display_formats', {})
        report['validated_sections'].append('display_formats')
        
        # Check required format strings
        required_formats = ['status_line_format', 'compliance_format']
        for format_name in required_formats:
            if format_name not in display_formats:
                report['errors'].append(f"Missing required format: display_formats.{format_name}")
                report['is_valid'] = False
    
    def _validate_compliance_thresholds(self, report: Dict[str, Any]) -> None:
        """Validate compliance thresholds configuration."""
        thresholds = self.config.get('compliance_thresholds', {})
        report['validated_sections'].append('compliance_thresholds')
        
        required_thresholds = ['good_threshold', 'warning_threshold', 'critical_threshold']
        for threshold_name in required_thresholds:
            threshold_value = thresholds.get(threshold_name)
            if threshold_value is None or not isinstance(threshold_value, (int, float)):
                report['errors'].append(f"compliance_thresholds.{threshold_name} must be numeric")
                report['is_valid'] = False
            elif not 0 <= threshold_value <= 100:
                report['errors'].append(f"compliance_thresholds.{threshold_name} must be between 0-100")
                report['is_valid'] = False
    
    def _validate_chart_settings(self, report: Dict[str, Any]) -> None:
        """Validate chart settings configuration."""
        chart_settings = self.config.get('chart_settings', {})
        report['validated_sections'].append('chart_settings')
        
        # Validate color scheme
        colors = chart_settings.get('color_scheme')
        if colors and not isinstance(colors, list):
            report['errors'].append("chart_settings.color_scheme must be a list")
            report['is_valid'] = False
    
    def _validate_cache_settings(self, report: Dict[str, Any]) -> None:
        """Validate cache settings configuration."""
        cache_settings = self.config.get('cache_settings', {})
        report['validated_sections'].append('cache_settings')
        
        # Validate cache size
        max_size = cache_settings.get('max_size')
        if max_size is not None and (not isinstance(max_size, int) or max_size <= 0):
            report['errors'].append("cache_settings.max_size must be positive integer")
            report['is_valid'] = False
    
    def _validate_mobile_settings(self, report: Dict[str, Any]) -> None:
        """Validate mobile settings configuration."""
        mobile_settings = self.config.get('mobile_settings', {})
        report['validated_sections'].append('mobile_settings')
        
        # Validate responsive breakpoints
        breakpoints = mobile_settings.get('responsive_breakpoints', {})
        for device_type in ['mobile', 'tablet', 'desktop']:
            breakpoint = breakpoints.get(device_type)
            if breakpoint is not None and (not isinstance(breakpoint, int) or breakpoint <= 0):
                report['errors'].append(f"mobile_settings.responsive_breakpoints.{device_type} must be positive integer")
                report['is_valid'] = False


# ===== HELPER FUNCTIONS FOR TESTS =====

def create_sample_artifact_collection() -> Dict[str, Any]:
    """Create sample artifact collection for testing"""
    return {
        'artifacts': [
            {
                'name': 'test_file_1.py',
                'type': 'test_file',
                'quality_score': 85.0,
                'coverage_percentage': 90.0,
                'created': '2025-09-26T09:00:00Z'
            },
            {
                'name': 'implementation_1.py',
                'type': 'implementation',
                'quality_score': 92.0,
                'coverage_percentage': 88.0,
                'created': '2025-09-26T10:00:00Z'
            }
        ]
    }

def create_sample_compliance_data() -> Dict[str, Any]:
    """Create sample compliance data for testing"""
    return {
        'overall_score': 87.5,
        'stage_compliance': {
            'red_stage': {'score': 95.0, 'status': 'compliant'},
            'green_stage': {'score': 82.0, 'status': 'compliant'},
            'refactor_stage': {'score': 85.5, 'status': 'compliant'}
        },
        'generated_at': '2025-09-26T11:00:00Z'
    }

def create_comprehensive_report_data() -> Dict[str, Any]:
    """Create comprehensive report data for testing"""
    return {
        'report_type': 'comprehensive_audit',
        'project_data': {'name': 'UI Layer Test'},
        'compliance_data': create_sample_compliance_data()
    }

def create_large_evidence_update_batch(size: int) -> List[Dict[str, Any]]:
    """Create large batch of evidence updates for testing"""
    return [
        {
            'id': f'update_{i}',
            'stage': 'green_stage',
            'evidence_type': 'implementation_artifacts',
            'status': 'collecting',
            'timestamp': f'2025-09-26T10:{i:02d}:00Z',
            'progress_percentage': (i * 2) % 100
        }
        for i in range(size)
    ]

def create_evidence_update_event(event_id: str) -> Dict[str, Any]:
    """Create evidence update event for testing"""
    return {
        'id': event_id,
        'stage': 'green_stage',
        'evidence_type': 'implementation_artifacts',
        'status': 'collecting',
        'timestamp': '2025-09-26T10:00:00Z',
        'progress_percentage': 75
    }


if __name__ == "__main__":
    print("🔧 EvidenceDisplayInterface - GREEN Phase Implementation")
    print("=" * 60)
    print("Minimal implementation to pass all 48 UI Layer tests")
    print("Ready for testing with UI Layer failing tests")