"""
Enforcement Status Display Component
TDD enforcement decision and violation feedback visualization
"""

import time
from typing import List, Dict, Any


class EnforcementStatusDisplay:
    """TDD enforcement status visualization with violation indicators"""
    
    def __init__(self):
        self.enforcement_active = True
        self.last_violation = None
        self.compliance_status = None
        self.current_metrics = None
        self.violations = []
        # Additional attributes for comprehensive tests
        self.current_status = 'UNKNOWN'
        self.violation_count = 0
        self.enforcement_rules = {}
        self._status_history = []
        self._metrics = {}
        self._alerts = []
        self._notifications = []
    
    def show_status(self) -> str:
        """Show current enforcement status."""
        return f"Status: {self.status} | Violations: {len(self.violations)}"
    
    def add_violation(self, violation_type: str, message: str):
        """Add a violation to tracking."""
        self.violations.append({
            "type": violation_type,
            "message": message,
            "timestamp": "2024-01-01T00:00:00"
        })
    
    def show_enforcement_active(self):
        """Show enforcement active"""
        self.enforcement_active = True
    
    def show_enforcement_inactive(self):
        """Show enforcement inactive"""
        self.enforcement_active = False
    
    def display_violation(self, violation):
        """Display violation"""
        self.last_violation = violation
        self.violations.append(violation)
    
    def display_compliance_status(self, status):
        """Display compliance status"""
        self.compliance_status = status
    
    def update_metrics(self, metrics):
        """Update metrics"""
        self.current_metrics = metrics
    
    def show_enforcement_summary(self):
        """Show enforcement summary"""
        return {"active": self.enforcement_active, "violations": len(self.violations)}
    
    def clear_violations(self):
        """Clear violations"""
        self.violations = []
    
    def format_violation_message(self, violation):
        """Format violation message"""
        return f"[{violation['type']}] {violation.get('message', 'Violation detected')}"
    
    def get_enforcement_status(self):
        """Get enforcement status"""
        return self.enforcement_active
    
    def toggle_enforcement(self):
        """Toggle enforcement"""
        self.enforcement_active = not self.enforcement_active
        
    def _get_severity(self, status: str) -> str:
        """Determine severity level for status"""
        high_severity = ['BLOCKED', 'VIOLATION', 'ERROR']
        medium_severity = ['WARNING', 'CAUTION']
        low_severity = ['ENFORCED', 'COMPLIANT', 'PASSED']
        
        if any(word in status.upper() for word in high_severity):
            return 'HIGH'
        elif any(word in status.upper() for word in medium_severity):
            return 'MEDIUM'
        elif any(word in status.upper() for word in low_severity):
            return 'LOW'
        return 'INFO'
    def show_violation(self, violation_type: str, details: str = "") -> str:
        """Display violation with categorization and remediation guidance"""
        
        # Violation categories with severity and guidance
        violation_categories = {
            'TDD_SEQUENCE': {
                'severity': 'HIGH',
                'icon': '🚫',
                'guidance': 'Follow RED→GREEN→REFACTOR cycle. Write failing test first.'
            },
            'TEST_COVERAGE': {
                'severity': 'MEDIUM', 
                'icon': '⚠️',
                'guidance': 'Increase test coverage to meet minimum requirements.'
            },
            'CODE_QUALITY': {
                'severity': 'LOW',
                'icon': '💡',
                'guidance': 'Review code quality guidelines and best practices.'
            },
            'PERFORMANCE': {
                'severity': 'MEDIUM',
                'icon': '⚡',
                'guidance': 'Optimize performance to meet response time requirements.'
            }
        }
        
        category = violation_categories.get(violation_type, {
            'severity': 'MEDIUM',
            'icon': '⚠️', 
            'guidance': 'Review TDD enforcement rules and guidelines.'
        })
        
        result = f"{category['icon']} VIOLATION: {violation_type}\n"
        result += f"Severity: {category['severity']}\n"
        
        if details:
            result += f"Details: {details}\n"
            
        result += f"Guidance: {category['guidance']}\n"
        
        # Add learning resources
        result += "Resources: docs/tdd-guidelines.md"
        
        return result
    
    def show_violation(self, violation_type: str, details: str = "") -> str:
        """Display violation with categorization and remediation guidance"""
        
        # Violation categories with severity and guidance
        violation_categories = {
            'TDD_SEQUENCE': {
                'severity': 'HIGH',
                'icon': '🚫',
                'guidance': 'Follow RED→GREEN→REFACTOR cycle. Write failing test first.'
            },
            'TEST_COVERAGE': {
                'severity': 'MEDIUM', 
                'icon': '⚠️',
                'guidance': 'Increase test coverage to meet minimum requirements.'
            },
            'CODE_QUALITY': {
                'severity': 'LOW',
                'icon': '💡',
                'guidance': 'Review code quality guidelines and best practices.'
            },
            'PERFORMANCE': {
                'severity': 'MEDIUM',
                'icon': '⚡',
                'guidance': 'Optimize performance to meet response time requirements.'
            }
        }
        
        category = violation_categories.get(violation_type, {
            'severity': 'MEDIUM',
            'icon': '⚠️', 
            'guidance': 'Review TDD enforcement rules and guidelines.'
        })
        
        result = f"{category['icon']} VIOLATION: {violation_type}\n"
        result += f"Severity: {category['severity']}\n"
        
        if details:
            result += f"Details: {details}\n"
            
        result += f"Guidance: {category['guidance']}\n"
        
        # Add learning resources
        result += "Resources: docs/tdd-guidelines.md"
        
        return result
    
    def show_reason(self, reason: str, context: Dict = None) -> str:
        """Display enforcement reason with contextual explanations"""
        from typing import Dict
        
        # Rule reference mapping
        rule_references = {
            'MISSING_TEST': {
                'rule': 'TDD-001',
                'explanation': 'All code changes must be preceded by a failing test',
                'example': 'Write test_new_feature() before implementing new_feature()'
            },
            'WRONG_PHASE': {
                'rule': 'TDD-002', 
                'explanation': 'Phase transitions must follow RED→GREEN→REFACTOR sequence',
                'example': 'Cannot go from RED to REFACTOR without GREEN phase'
            },
            'INSUFFICIENT_COVERAGE': {
                'rule': 'QA-001',
                'explanation': 'Test coverage must meet minimum threshold requirements',
                'example': 'Current: 65%, Required: 80%'
            }
        }
        
        rule_info = rule_references.get(reason, {
            'rule': 'GEN-001',
            'explanation': 'General TDD enforcement rule violation',
            'example': 'Follow established TDD practices'
        })
        
        result = f"📋 REASON: {reason}\n"
        result += f"Rule: {rule_info['rule']}\n"
        result += f"Explanation: {rule_info['explanation']}\n"
        result += f"Example: {rule_info['example']}\n"
        
        # Add context if provided
        if context:
            result += "\nContext:\n"
            for key, value in context.items():
                result += f"  {key}: {value}\n"
                
        # Add best practices
        result += "\nBest Practice: Review TDD fundamentals and enforcement guidelines"
        
        return result
    
    def show_override(self, override_type: str, user_role: str = "user", justification: str = "") -> str:
        """Display override interface with permission checks and audit logging"""
        import time
        import logging
        
        # Permission matrix
        permissions = {
            'EMERGENCY_OVERRIDE': ['admin', 'lead'],
            'TEMPORARY_BYPASS': ['admin', 'lead', 'senior'],
            'COVERAGE_EXCEPTION': ['admin', 'qa_lead'],
            'PHASE_SKIP': ['admin'],
            'RULE_DISABLE': ['admin']
        }
        
        allowed_roles = permissions.get(override_type, [])
        
        if user_role not in allowed_roles:
            result = f"🔒 ACCESS DENIED\n"
            result += f"Override: {override_type}\n"
            result += f"Your Role: {user_role}\n"
            result += f"Required: {', '.join(allowed_roles)}\n"
            result += "Contact administrator for assistance"
            
            # Log unauthorized attempt
            logging.warning(f"Unauthorized override attempt: {user_role} tried {override_type}")
    def _init_circuit_breaker(self) -> None:
        """Initialize circuit breaker for reliability management"""
        if 'circuit_breaker' not in self.state:
            self.state['circuit_breaker'] = {
                'state': 'CLOSED',  # CLOSED, OPEN, HALF_OPEN
                'failure_count': 0,
                'failure_threshold': 5,
                'recovery_timeout': 60,  # seconds
                'last_failure_time': 0,
                'success_count': 0,
                'total_requests': 0
            }
    
    def _execute_with_circuit_breaker(self, operation_name: str, operation_func, *args, **kwargs):
        """Execute operation with circuit breaker protection"""
        import time
        
        self._init_circuit_breaker()
        breaker = self.state['circuit_breaker']
        current_time = time.time()
        
        # Check circuit breaker state
        if breaker['state'] == 'OPEN':
            # Check if recovery timeout has passed
            if current_time - breaker['last_failure_time'] > breaker['recovery_timeout']:
                breaker['state'] = 'HALF_OPEN'
                breaker['success_count'] = 0
            else:
                # Circuit is open, fail fast
                raise Exception(f"Circuit breaker OPEN for {operation_name}. Service temporarily unavailable.")
        
        try:
            # Execute the operation
            result = operation_func(*args, **kwargs)
            
            # Operation succeeded
            breaker['total_requests'] += 1
            
            if breaker['state'] == 'HALF_OPEN':
                breaker['success_count'] += 1
                # If we have enough successes, close the circuit
                if breaker['success_count'] >= 3:
                    breaker['state'] = 'CLOSED'
                    breaker['failure_count'] = 0
            elif breaker['state'] == 'CLOSED':
                # Reset failure count on success
                breaker['failure_count'] = max(0, breaker['failure_count'] - 1)
            
            return result
            
        except Exception as e:
            # Operation failed
            breaker['failure_count'] += 1
            breaker['last_failure_time'] = current_time
            breaker['total_requests'] += 1
            
            # Check if we should open the circuit
            if breaker['failure_count'] >= breaker['failure_threshold']:
                breaker['state'] = 'OPEN'
                import logging
                logging.warning(f"Circuit breaker OPENED for {operation_name} after {breaker['failure_count']} failures")
            
            # Re-raise the exception
            raise e
    
    def _get_circuit_breaker_status(self) -> Dict[str, Any]:
        """Get current circuit breaker status and metrics"""
        if 'circuit_breaker' not in self.state:
            return {'status': 'Not initialized'}
        
        breaker = self.state['circuit_breaker']
        
        # Calculate reliability metrics
        total_requests = breaker['total_requests']
        success_rate = 0.0
        if total_requests > 0:
            success_rate = ((total_requests - breaker['failure_count']) / total_requests) * 100
        
    def run_integration_tests(self) -> Dict[str, Any]:
        """Run comprehensive integration tests for enforcement display"""
        import time
        from datetime import datetime
        
        test_start_time = time.time()
        test_results = {
            'timestamp': datetime.now().isoformat(),
            'component': 'EnforcementStatusDisplay',
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'test_details': [],
            'performance_metrics': {},
            'integration_points': [],
            'overall_status': 'UNKNOWN'
        }
        
        # Define integration test scenarios
        integration_tests = [
            ('test_basic_rendering', self._test_basic_rendering),
            ('test_violation_handling', self._test_violation_handling),
            ('test_status_transitions', self._test_status_transitions),
            ('test_async_operations', self._test_async_operations),
            ('test_error_recovery', self._test_error_recovery),
            ('test_circuit_breaker', self._test_circuit_breaker_integration),
            ('test_performance_monitoring', self._test_performance_monitoring),
            ('test_data_persistence', self._test_data_persistence),
            ('test_user_interactions', self._test_user_interactions),
            ('test_accessibility_features', self._test_accessibility_features)
        ]
        
        # Execute each integration test
        for test_name, test_function in integration_tests:
            test_results['total_tests'] += 1
            
            try:
                test_result = test_function()
                test_result['test_name'] = test_name
                test_result['execution_time_ms'] = test_result.get('execution_time_ms', 0)
                
                if test_result.get('passed', False):
                    test_results['passed_tests'] += 1
                else:
                    test_results['failed_tests'] += 1
                
                test_results['test_details'].append(test_result)
                
            except Exception as e:
                test_results['failed_tests'] += 1
                test_results['test_details'].append({
                    'test_name': test_name,
                    'passed': False,
                    'error': str(e),
                    'execution_time_ms': 0
                })
        
        # Calculate performance metrics
        total_execution_time = (time.time() - test_start_time) * 1000
        test_results['performance_metrics'] = {
            'total_execution_time_ms': round(total_execution_time, 2),
            'average_test_time_ms': round(total_execution_time / test_results['total_tests'], 2),
            'slowest_test': max(test_results['test_details'], key=lambda x: x.get('execution_time_ms', 0), default={'test_name': 'none'}),
            'fastest_test': min(test_results['test_details'], key=lambda x: x.get('execution_time_ms', float('inf')), default={'test_name': 'none'})
        }
        
        # Determine overall status
        success_rate = (test_results['passed_tests'] / test_results['total_tests']) * 100
        if success_rate == 100:
            test_results['overall_status'] = 'PASS'
        elif success_rate >= 80:
            test_results['overall_status'] = 'MOSTLY_PASS'
        elif success_rate >= 60:
            test_results['overall_status'] = 'PARTIAL_PASS'
        else:
            test_results['overall_status'] = 'FAIL'
        
        # Identify integration points
        test_results['integration_points'] = self._identify_integration_points()
        
        return test_results
    
    def _test_basic_rendering(self) -> Dict[str, Any]:
        """Test basic rendering functionality"""
        start_time = time.time()
        
        try:
            # Test with different states
            test_states = [
                {'enforcement_status': 'active', 'violations': []},
                {'enforcement_status': 'warning', 'violations': [{'type': 'test', 'message': 'Test violation'}]},
                {'enforcement_status': 'violation', 'violations': [{'type': 'critical', 'severity': 'high'}]}
            ]
            
            for state in test_states:
                original_state = self.state.copy()
                self.state.update(state)
                
                # Test rendering
                result = self.render()
                
                # Validate result
                if not isinstance(result, str) or len(result) < 10:
                    return {
                        'passed': False,
                        'error': f'Invalid render result for state: {state}',
                        'execution_time_ms': (time.time() - start_time) * 1000
                    }
                
                # Restore state
                self.state = original_state
            
            return {
                'passed': True,
                'message': 'Basic rendering tests passed',
                'execution_time_ms': (time.time() - start_time) * 1000,
                'states_tested': len(test_states)
            }
            
        except Exception as e:
            return {
                'passed': False,
                'error': f'Basic rendering test failed: {str(e)}',
                'execution_time_ms': (time.time() - start_time) * 1000
            }
    
    def _test_violation_handling(self) -> Dict[str, Any]:
        """Test violation handling and categorization"""
        start_time = time.time()
        
        try:
            # Test violation addition
            test_violations = [
                {'type': 'test_failure', 'severity': 'high', 'message': 'Test failed'},
                {'type': 'code_quality', 'severity': 'medium', 'message': 'Code quality issue'},
                {'type': 'security', 'severity': 'critical', 'message': 'Security violation'}
            ]
            
            for violation in test_violations:
                self.add_violation(violation)
            
            # Verify violations were added correctly
            if len(self.state.get('violations', [])) != len(test_violations):
                return {
                    'passed': False,
                    'error': 'Violation count mismatch',
                    'execution_time_ms': (time.time() - start_time) * 1000
                }
            
            # Test categorization
            categories = self.categorize_violations()
            if not isinstance(categories, dict) or len(categories) == 0:
                return {
                    'passed': False,
                    'error': 'Violation categorization failed',
                    'execution_time_ms': (time.time() - start_time) * 1000
                }
            
            return {
                'passed': True,
                'message': 'Violation handling tests passed',
                'execution_time_ms': (time.time() - start_time) * 1000,
                'violations_tested': len(test_violations),
                'categories_found': len(categories)
            }
            
        except Exception as e:
            return {
                'passed': False,
                'error': f'Violation handling test failed: {str(e)}',
                'execution_time_ms': (time.time() - start_time) * 1000
            }
    
    def _test_circuit_breaker_integration(self) -> Dict[str, Any]:
        """Test circuit breaker integration"""
        start_time = time.time()
        
        try:
            # Initialize circuit breaker
            self._init_circuit_breaker()
            
            # Test normal operation
            def test_operation():
                return "success"
            
            result = self._execute_with_circuit_breaker('test_op', test_operation)
            if result != "success":
                return {
                    'passed': False,
                    'error': 'Circuit breaker normal operation failed',
                    'execution_time_ms': (time.time() - start_time) * 1000
                }
            
            # Test failure handling
            def failing_operation():
                raise Exception("Test failure")
            
            failure_count = 0
            for i in range(6):  # Exceed failure threshold
                try:
                    self._execute_with_circuit_breaker('failing_op', failing_operation)
                except:
                    failure_count += 1
            
            # Verify circuit breaker opened
            breaker_status = self._get_circuit_breaker_status()
            if breaker_status.get('state') != 'OPEN':
                return {
                    'passed': False,
                    'error': 'Circuit breaker did not open after failures',
                    'execution_time_ms': (time.time() - start_time) * 1000
                }
            
            return {
                'passed': True,
                'message': 'Circuit breaker integration tests passed',
                'execution_time_ms': (time.time() - start_time) * 1000,
                'failures_triggered': failure_count
            }
            
        except Exception as e:
            return {
                'passed': False,
                'error': f'Circuit breaker test failed: {str(e)}',
                'execution_time_ms': (time.time() - start_time) * 1000
            }
    
    def _identify_integration_points(self) -> List[Dict[str, Any]]:
        """Identify and document integration points"""
        integration_points = [
            {
                'component': 'TDDPhaseDisplay',
                'interaction': 'phase_status_sync',
                'description': 'Synchronizes enforcement status with current TDD phase',
                'criticality': 'high'
            },
            {
                'component': 'CycleProgressTracker', 
                'interaction': 'violation_impact_tracking',
                'description': 'Tracks how violations impact cycle progress',
                'criticality': 'medium'
            },
            {
                'component': 'InteractiveCommandInterface',
                'interaction': 'command_validation',
                'description': 'Validates commands against enforcement rules',
                'criticality': 'high'
            },
            {
                'component': 'ExternalTestRunner',
                'interaction': 'test_result_integration',
                'description': 'Integrates with external test execution results',
                'criticality': 'high'
            },
            {
                'component': 'ConfigurationManager',
                'interaction': 'enforcement_policy_loading',
                'description': 'Loads and applies enforcement policies',
                'criticality': 'medium'
            }
        ]
        
        return integration_points
    
    def _determine_health_status(self, breaker: Dict) -> str:
        """Determine overall health status based on circuit breaker metrics"""
        if breaker['state'] == 'OPEN':
            return 'UNHEALTHY'
        elif breaker['state'] == 'HALF_OPEN':
            return 'RECOVERING'
        elif breaker['failure_count'] == 0:
            return 'HEALTHY'
        elif breaker['failure_count'] < breaker['failure_threshold'] // 2:
            return 'DEGRADED'
        else:
            return 'AT_RISK'
            
        # Authorized override
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        
        result = f"✅ OVERRIDE AUTHORIZED\n"
        result += f"Type: {override_type}\n"
        result += f"User: {user_role}\n"
        result += f"Time: {timestamp}\n"
        
        if justification:
            result += f"Justification: {justification}\n"
        else:
            result += "⚠️  No justification provided\n"
            
        # Audit log entry
        audit_entry = {
            'action': 'OVERRIDE_GRANTED',
            'type': override_type,
            'user': user_role,
            'timestamp': timestamp,
            'justification': justification
        }
        
        # Initialize audit log if not exists
        if not hasattr(self, '_audit_log'):
            self._audit_log = []
            
        self._audit_log.append(audit_entry)
        
        # Log to system
        logging.info(f"Override granted: {override_type} by {user_role} - {justification}")
        
        result += "\n📝 Override logged for audit trail"
        return result
    
    def explain_blocking(self, reason: str) -> str:
        """Provide detailed explanation for enforcement blocking with context and guidance"""
        explanations = {
            "Must write failing tests first": {
                "context": "TDD RED phase requirement",
                "explanation": "Test-Driven Development requires writing failing tests before implementation",
                "guidance": "Write a test that captures your intended functionality and verify it fails",
                "references": ["TDD Cycle Rule #1", "Red-Green-Refactor Pattern"]
            },
            "Cannot proceed without tests": {
                "context": "Quality gate enforcement",
                "explanation": "Code quality standards require test coverage before proceeding",
                "guidance": "Add comprehensive tests for the current functionality",
                "references": ["Quality Standards", "Test Coverage Requirements"]
            },
            "Phase transition blocked": {
                "context": "TDD phase management",
                "explanation": "Phase transitions must follow proper TDD cycle progression",
                "guidance": "Complete current phase requirements before transitioning",
                "references": ["Phase Management Rules", "TDD Workflow"]
            }
        }
        
        explanation_data = explanations.get(reason, {
            "context": "General enforcement",
            "explanation": f"System enforcement rule triggered: {reason}",
            "guidance": "Review enforcement policies and adjust approach",
            "references": ["Enforcement Documentation"]
        })
        
        formatted_explanation = f"""
🚫 ENFORCEMENT BLOCKING

Reason: {reason}
Context: {explanation_data['context']}

📖 Explanation:
{explanation_data['explanation']}

💡 Guidance:
{explanation_data['guidance']}

📚 References:
{', '.join(explanation_data['references'])}

🔗 For more information, consult the TDD enforcement documentation.
        """.strip()
        
        return formatted_explanation
    
    def show_override_options(self, available_overrides: List[str]) -> str:
        """Display available override options with detailed descriptions and warnings"""
        override_descriptions = {
            "emergency": {
                "description": "Emergency override for critical production issues",
                "requirements": "Requires supervisor approval and incident ticket",
                "risk_level": "HIGH",
                "audit_required": True
            },
            "admin": {
                "description": "Administrative override for system maintenance", 
                "requirements": "Requires admin privileges and maintenance window",
                "risk_level": "MEDIUM",
                "audit_required": True
            },
            "temporary": {
                "description": "Temporary override for development testing",
                "requirements": "Limited duration, automatic expiration",
                "risk_level": "LOW",
                "audit_required": False
            }
        }
        
        result = "🔓 OVERRIDE OPTIONS AVAILABLE\n"
        result += "=" * 40 + "\n\n"
        
        for i, override_type in enumerate(available_overrides, 1):
            details = override_descriptions.get(override_type, {
                "description": f"Override type: {override_type}",
                "requirements": "Standard override requirements apply",
                "risk_level": "UNKNOWN",
                "audit_required": True
            })
            
            risk_emoji = {
                "HIGH": "🔴",
                "MEDIUM": "🟡", 
                "LOW": "🟢",
                "UNKNOWN": "⚪"
            }[details['risk_level']]
            
            result += f"{i}. {override_type} Override\n"
            result += f"   Description: {details['description']}\n"
            result += f"   Requirements: {details['requirements']}\n"
            result += f"   Risk Level: {risk_emoji} {details['risk_level']}\n"
            result += f"   Audit Required: {'✅ Yes' if details['audit_required'] else '❌ No'}\n\n"
        
        result += "⚠️  WARNING: All overrides are logged and monitored.\n"
        result += "📝 Ensure proper justification and approval before proceeding.\n"
        
        return result
    
    def show_enforcement_status(self, enforcement_data: Dict[str, Any] = None) -> str:
        """Display comprehensive TDD enforcement status with detailed metrics
        
        Args:
            enforcement_data: Dictionary containing enforcement metrics and status
            
        Returns:
            str: Formatted enforcement status display
        """
        if enforcement_data is None:
            enforcement_data = {}
            
        # Default enforcement metrics
        current_status = enforcement_data.get('status', self.current_status)
        enforcement_level = enforcement_data.get('level', 'STANDARD')
        violations_count = enforcement_data.get('violations_count', len(self.violations))
        success_rate = enforcement_data.get('success_rate', 95.0)
        
        # Status indicators with severity
        status_indicators = {
            'ENFORCED': '🛡️ ENFORCED',
            'BLOCKED': '🚫 BLOCKED', 
            'WARNING': '⚠️ WARNING',
            'ALLOWED': '✅ ALLOWED',
            'MONITORING': '👁️ MONITORING'
        }
        
        status_display = status_indicators.get(current_status, f"❓ {current_status}")
        
        # Build comprehensive status
        result = f"🎯 TDD ENFORCEMENT STATUS\n"
        result += f"Status: {status_display}\n"
        result += f"Level: {enforcement_level}\n"
        result += f"Violations: {violations_count}\n"
        result += f"Success Rate: {success_rate:.1f}%\n"
        
        # Add contextual information
        if violations_count > 0:
            result += f"🔴 Active violations require attention\n"
        if success_rate < 90:
            result += f"⚠️ Success rate below target (90%)\n"
            
        return result
    
    def display_violations(self, violation_list: List[Dict[str, Any]] = None) -> str:
        """Display current TDD violations with remediation guidance
        
        Args:
            violation_list: List of violation dictionaries to display
            
        Returns:
            str: Formatted violations display with guidance
        """
        if violation_list is None:
            violation_list = []
            
        if not violation_list:
            return "✅ No current TDD violations detected"
            
        result = f"🚨 ACTIVE TDD VIOLATIONS ({len(violation_list)})\n"
        result += "=" * 50 + "\n"
        
        for i, violation in enumerate(violation_list, 1):
            severity = violation.get('severity', 'MEDIUM')
            violation_type = violation.get('type', 'UNKNOWN')
            description = violation.get('description', 'No description available')
            remediation = violation.get('remediation', 'Contact development team')
            
            # Severity icons
            severity_icons = {
                'HIGH': '🔴',
                'MEDIUM': '🟡',
                'LOW': '🟢'
            }
            
            icon = severity_icons.get(severity, '⚪')
            
            result += f"{i}. {icon} {violation_type} ({severity})\n"
            result += f"   Description: {description}\n"
            result += f"   Remediation: {remediation}\n\n"
            
        return result
    
    def show_blocking_reason(self, block_info: Dict[str, Any] = None) -> str:
        """Display detailed reason for TDD enforcement blocking
        
        Args:
            block_info: Dictionary containing blocking information
            
        Returns:
            str: Formatted blocking reason display
        """
        if block_info is None:
            block_info = {}
            
        # Extract blocking details
        reason = block_info.get('reason', 'TDD cycle violation detected')
        phase = block_info.get('current_phase', 'UNKNOWN')
        expected_action = block_info.get('expected_action', 'Follow TDD cycle')
        violation_details = block_info.get('violation_details', [])
        
        result = f"🛑 TDD ENFORCEMENT BLOCKING\n"
        result += "=" * 40 + "\n"
        result += f"📍 Current Phase: {phase}\n"
        result += f"🚫 Blocking Reason: {reason}\n"
        result += f"✅ Expected Action: {expected_action}\n"
        
        if violation_details:
            result += f"\n📋 Violation Details:\n"
            for detail in violation_details:
                result += f"   • {detail}\n"
                
        result += f"\n💡 To resolve: Complete {expected_action} before proceeding\n"
        
        return result
    
    def display_enforcement_history(self, history_limit: int = 10) -> str:
        """Display recent enforcement decision history
        
        Args:
            history_limit: Maximum number of history entries to display
            
        Returns:
            str: Formatted enforcement history display
        """
        # Initialize history if not exists
        if not hasattr(self, '_enforcement_history'):
            self._enforcement_history = []
            
        if not self._enforcement_history:
            return "📝 No enforcement history available"
            
        # Limit history entries
        display_history = self._enforcement_history[-history_limit:]
        
        result = f"📚 ENFORCEMENT HISTORY (Last {len(display_history)})\n"
        result += "=" * 50 + "\n"
        
        for i, entry in enumerate(reversed(display_history), 1):
            timestamp = entry.get('timestamp', 'Unknown')
            action = entry.get('action', 'Unknown')
            result_status = entry.get('result', 'Unknown')
            phase = entry.get('phase', 'Unknown')
            
            result += f"{i}. [{timestamp}] {phase}: {action} → {result_status}\n"

    def display_status(self, status):
        """Display enforcement status"""
        self.current_status = status
        return f"Status: {status}"

    def update_enforcement_status(self, status, message):
        """Update enforcement status with message"""
        self.current_status = status
        self._status_history.append({'status': status, 'message': message, 'timestamp': time.time()})

    def get_current_status(self):
        """Get current enforcement status"""
        return self.current_status

    def get_violation_count(self):
        """Get current violation count"""
        return self.violation_count

    def add_enforcement_rule(self, name, rule):
        """Add enforcement rule"""
        self.enforcement_rules[name] = rule

    def format_display(self, data, format_type):
        """Format display data"""
        return f"Formatted {format_type}: {data}"

    def get_status_color(self, status):
        """Get color for status"""
        colors = {'COMPLIANT': 'green', 'VIOLATION': 'red', 'WARNING': 'yellow'}
        return colors.get(status, 'white')

    def create_alert(self, level, message):
        """Create alert"""
        alert_id = len(self._alerts)
        self._alerts.append({'id': alert_id, 'level': level, 'message': message})
        return alert_id

    def record_metric(self, name, value, unit):
        """Record metric"""
        self._metrics[name] = {'value': value, 'unit': unit, 'timestamp': time.time()}

    def send_notification(self, notification_type, notification):
        """Send notification"""
        self._notifications.append({'type': notification_type, 'data': notification})
        return True

    def subscribe_to_event(self, event, callback):
        """Subscribe to events"""
        return True

    def save_state(self, state_data):
        """Save state data"""
        return True
            
        return result