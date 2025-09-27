"""
Evidence Display Interface for FEATURE-003-01-04 Stage Gate Evidence Collection
Implements mobile display configuration, CSS generation, responsive grid, and data pagination.
Enhanced with logging, type safety, and performance monitoring.
"""
import logging
import time
from typing import Dict, Any, List, Optional
from datetime import datetime


class MobileWorkflowPackage:
    """Mobile workflow package object with proper to_dict() method
    
    Enhanced with type safety and validation
    """
    
    def __init__(self, data: Dict[str, Any]):
        """Initialize mobile workflow package with validation
        
        Args:
            data: Dictionary containing workflow data
        """
        self.stage = data.get('stage', '')
        self.progress = data.get('progress', 0)
        self.mobile_optimized = data.get('mobile_optimized', True)
        self.metrics = data.get('metrics', {})
        self._original_data = data
        self._created_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert mobile workflow package to dictionary
        
        Returns:
            Dictionary representation of the workflow package
        """
        return {
            'stage': self.stage,
            'progress': self.progress,
            'mobile_optimized': self.mobile_optimized,
            'metrics': self.metrics,
            'timestamp': self._created_at.isoformat(),
            'created_at': self._created_at.isoformat()
        }


class EvidenceDisplayInterface:
    """Evidence display interface with mobile optimization capabilities
    
    Enhanced with:
    - Structured logging
    - Performance monitoring
    - Type safety
    - Configuration management
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize evidence display interface
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or self._get_default_config()
        self.operation_count = 0
        self.start_time = time.time()
        
        # Setup logging
        self._setup_logging()
        
        self.logger.info("EvidenceDisplayInterface initialized")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration settings
        
        Returns:
            Default configuration dictionary
        """
        return {
            'mobile': {
                'max_items': 10,
                'font_size': '16px',
                'grid_columns': '1fr',
                'screen_width': 320
            },
            'performance': {
                'enable_monitoring': True,
                'log_operations': True
            }
        }
    
    def _setup_logging(self) -> None:
        """Setup structured logging"""
        self.logger = logging.getLogger(__name__)
        
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    def _track_operation(self, operation_name: str) -> None:
        """Track operation for performance monitoring
        
        Args:
            operation_name: Name of the operation being tracked
        """
        if self.config.get('performance', {}).get('log_operations', True):
            self.operation_count += 1
            self.logger.debug(f"Operation {self.operation_count}: {operation_name}")
    
    def create_mobile_optimized_display(self, evidence_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create mobile-optimized display with screen_width property
        
        Args:
            evidence_data: Evidence data to display
            
        Returns:
            Mobile-optimized display configuration
        """
        start_time = time.time()
        self._track_operation("create_mobile_optimized_display")
        
        mobile_config = self.config.get('mobile', {})
        
        display_config = {
            'screen_width': mobile_config.get('screen_width', 320),  # iOS/Android standard
            'compact_display': True,
            'reduced_animations': True,  
            'touch_friendly': True,
            'simplified_charts': True,
            'device_type': 'mobile',
            'max_items': mobile_config.get('max_items', 10)  # Mobile pagination limit
        }
        
        # Apply mobile pagination
        max_items = display_config['max_items']
        
        result = {
            'display_config': display_config,
            'compliance_data': evidence_data.get('compliance_data', [])[:max_items],
            'test_results': evidence_data.get('test_results', [])[:max_items],
            'metrics': evidence_data.get('metrics', {}),
            'timestamp': datetime.now().isoformat(),
            'generation_time_ms': round((time.time() - start_time) * 1000, 2)
        }
        
        self.logger.info(f"Mobile display created in {result['generation_time_ms']}ms")
        return result
    
    def generate_mobile_css(self) -> str:
        """Generate mobile CSS with iOS-compliant font sizes"""
        
        mobile_css = """
/* Mobile Layout - iOS Accessibility Compliant */
@media (max-width: 320px) {
  .compliance-dashboard { 
    font-size: 16px;  /* CHANGED FROM 12px - iOS zoom prevention */
    padding: 8px; 
  }
  .status-line { 
    margin-bottom: 4px;
    font-size: 16px;  /* Consistent sizing */ 
  }
  .chart-container { height: 200px; }
  .touch-target { 
    min-height: 44px; 
    min-width: 44px; 
    font-size: 16px;  /* Touch target readability */
  }
  
  /* Responsive Grid Layout */
  .compliance-grid {
    grid-template-columns: 1fr;  /* Single column for mobile */
    display: grid;
    gap: 8px;
  }
}"""
        return mobile_css
    
    def generate_responsive_css(self) -> str:
        """Generate responsive CSS grid layout"""
        
        responsive_css = """
/* Responsive Grid System */
.compliance-grid {
  display: grid;
  gap: 16px;
}

/* Desktop */
@media (min-width: 1024px) {
  .compliance-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

/* Tablet */
@media (min-width: 768px) and (max-width: 1023px) {
  .compliance-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

/* Mobile */
@media (max-width: 767px) {
  .compliance-grid {
    grid-template-columns: 1fr;  /* Single column for mobile */
  }
}"""
        return responsive_css
    
    def display_audit_compliance_dashboard(self, compliance_data: Dict[str, Any]) -> str:
        """Display compliance dashboard with proper score formatting"""
        
        if compliance_data and compliance_data.get('overall_compliance_score') is not None:
            score = compliance_data['overall_compliance_score']
            
            # Format score properly - never show 0% unless actually 0
            if score == 0:
                score_display = "0%"
            else:
                score_display = f"{score:.1f}%"
            
            dashboard = f"""
=== COMPLIANCE DASHBOARD ===
Overall Compliance: {score_display}
Status: {'COMPLIANT' if score >= 85 else 'NON-COMPLIANT'}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            return dashboard
        else:
            return """
=== COMPLIANCE DASHBOARD ===
Overall Compliance: No data available
Status: PENDING
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    def create_mobile_workflow_package(self, workflow_data: Dict[str, Any]) -> MobileWorkflowPackage:
        """Create mobile workflow package object with to_dict() method"""
        return MobileWorkflowPackage(workflow_data)