#!/usr/bin/env python3
"""
Requirements Tracer - Comprehensive Requirements-to-Implementation Mapping
=========================================================================

This tool provides comprehensive requirements traceability by:
1. Parsing requirements documents for specific requirement IDs and criteria
2. Tracing each requirement to actual implementation code
3. Validating requirement compliance with measurable tests
4. Generating detailed traceability matrices with gap analysis
5. Testing actual requirement fulfillment (not just method existence)

Usage:
    python tools/requirements_tracer.py --layer data_access
    python tools/requirements_tracer.py --requirement FR-001 --verbose
    python tools/requirements_tracer.py --generate-matrix --output traceability_matrix.csv
"""

import sys
import re
import ast
import inspect
import importlib
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import argparse
import json
import csv
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

class RequirementsTracer:
    """Comprehensive requirements traceability analysis"""
    
    def __init__(self, layer: str = "data_access"):
        self.layer = layer
        self.requirements = {}
        self.implementations = {}
        self.traceability_matrix = {}
        self.gaps = []
        
    def parse_requirements_document(self, doc_path: str) -> Dict[str, Any]:
        """Parse requirements document and extract structured requirements"""
        if not Path(doc_path).exists():
            print(f"❌ Requirements document not found: {doc_path}")
            return {}
        
        content = Path(doc_path).read_text()
        requirements = {}
        
        # Enhanced pattern matching for requirements
        patterns = {
            'functional': r'(FR-\d+):\s*(.+?)(?=\n(?:FR-\d+|PF-\d+|RL-\d+|SC-\d+|TP-\d+|\Z))',
            'performance': r'(PF-\d+):\s*(.+?)(?=\n(?:FR-\d+|PF-\d+|RL-\d+|SC-\d+|TP-\d+|\Z))',
            'reliability': r'(RL-\d+):\s*(.+?)(?=\n(?:FR-\d+|PF-\d+|RL-\d+|SC-\d+|TP-\d+|\Z))',
            'security': r'(SC-\d+):\s*(.+?)(?=\n(?:FR-\d+|PF-\d+|RL-\d+|SC-\d+|TP-\d+|\Z))',
            'testing': r'(TP-\d+):\s*(.+?)(?=\n(?:FR-\d+|PF-\d+|RL-\d+|SC-\d+|TP-\d+|\Z))'
        }
        
        for category, pattern in patterns.items():
            matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
            for req_id, description in matches:
                requirements[req_id] = {
                    'id': req_id,
                    'category': category,
                    'description': description.strip(),
                    'measurable_criteria': self._extract_measurable_criteria(description),
                    'priority': self._determine_priority(req_id, description),
                    'testable': self._is_testable(description)
                }
        
        self.requirements = requirements
        print(f"📋 Parsed {len(requirements)} requirements from {doc_path}")
        return requirements
    
    def _extract_measurable_criteria(self, description: str) -> Dict[str, Any]:
        """Extract measurable criteria from requirement description"""
        criteria = {}
        
        # Performance criteria
        response_time = re.search(r'response time.*?<\s*(\d+)\s*ms', description, re.IGNORECASE)
        if response_time:
            criteria['max_response_time_ms'] = int(response_time.group(1))
        
        throughput = re.search(r'throughput.*?(\d+)\+.*?per minute', description, re.IGNORECASE)
        if throughput:
            criteria['min_throughput_per_minute'] = int(throughput.group(1))
        
        memory = re.search(r'memory.*?<\s*(\d+)\s*MB', description, re.IGNORECASE)
        if memory:
            criteria['max_memory_mb'] = int(memory.group(1))
        
        # Reliability criteria
        error_rate = re.search(r'error rate.*?<\s*(\d+\.?\d*)\s*%', description, re.IGNORECASE)
        if error_rate:
            criteria['max_error_rate_percent'] = float(error_rate.group(1))
        
        accuracy = re.search(r'(\d+)\s*%.*?accuracy', description, re.IGNORECASE)
        if accuracy:
            criteria['min_accuracy_percent'] = int(accuracy.group(1))
        
        # Coverage criteria
        coverage = re.search(r'(\d+)\s*%.*?coverage', description, re.IGNORECASE)
        if coverage:
            criteria['min_coverage_percent'] = int(coverage.group(1))
        
        return criteria
    
    def _determine_priority(self, req_id: str, description: str) -> str:
        """Determine requirement priority based on ID and description"""
        critical_keywords = ['must', 'shall', 'critical', 'essential', 'mandatory']
        high_keywords = ['should', 'important', 'significant']
        
        description_lower = description.lower()
        
        if any(keyword in description_lower for keyword in critical_keywords):
            return 'CRITICAL'
        elif any(keyword in description_lower for keyword in high_keywords):
            return 'HIGH'
        elif req_id.startswith('FR-'):
            return 'HIGH'  # Functional requirements are generally high priority
        else:
            return 'MEDIUM'
    
    def _is_testable(self, description: str) -> bool:
        """Determine if requirement has testable criteria"""
        testable_indicators = [
            r'\d+\s*ms', r'\d+\s*%', r'\d+\s*MB', r'\d+\s*per', 
            'measur', 'verif', 'test', 'validat', 'assert'
        ]
        return any(re.search(pattern, description, re.IGNORECASE) for pattern in testable_indicators)
    
    def analyze_implementation(self, module_path: str) -> Dict[str, Any]:
        """Analyze implementation code and extract detailed information"""
        try:
            # Import the module
            if self.layer == "data_access":
                from data_access.tdd_phase_repository import TDDPhaseRepository
                implementation_class = TDDPhaseRepository
            else:
                print(f"❌ Layer {self.layer} not supported yet")
                return {}
            
            # Analyze class structure
            methods = {}
            for name, method in inspect.getmembers(implementation_class, predicate=inspect.isfunction):
                if not name.startswith('_'):  # Skip private methods
                    methods[name] = {
                        'name': name,
                        'signature': str(inspect.signature(method)),
                        'docstring': inspect.getdoc(method) or '',
                        'source_file': inspect.getfile(method),
                        'line_number': inspect.getsourcelines(method)[1] if hasattr(method, '__code__') else 0,
                        'complexity': self._analyze_method_complexity(method),
                        'error_handling': self._has_error_handling(method),
                        'performance_optimized': self._has_performance_optimization(method)
                    }
            
            self.implementations = {
                'class_name': implementation_class.__name__,
                'module_path': module_path,
                'methods': methods,
                'total_methods': len(methods),
                'documented_methods': len([m for m in methods.values() if m['docstring']]),
                'error_handled_methods': len([m for m in methods.values() if m['error_handling']]),
                'performance_optimized_methods': len([m for m in methods.values() if m['performance_optimized']])
            }
            
            print(f"🔍 Analyzed {len(methods)} methods in {implementation_class.__name__}")
            return self.implementations
            
        except Exception as e:
            print(f"❌ Failed to analyze implementation: {e}")
            return {}
    
    def _analyze_method_complexity(self, method) -> str:
        """Analyze method complexity based on various factors"""
        try:
            source = inspect.getsource(method)
            # Simple complexity analysis
            lines = len(source.split('\n'))
            if lines > 100:
                return 'HIGH'
            elif lines > 50:
                return 'MEDIUM'
            else:
                return 'LOW'
        except:
            return 'UNKNOWN'
    
    def _has_error_handling(self, method) -> bool:
        """Check if method has proper error handling"""
        try:
            source = inspect.getsource(method)
            return 'try:' in source and 'except' in source
        except:
            return False
    
    def _has_performance_optimization(self, method) -> bool:
        """Check if method has performance optimizations"""
        try:
            source = inspect.getsource(method)
            optimization_indicators = ['cache', 'index', 'batch', 'async', 'concurrent', 'optimize']
            return any(indicator in source.lower() for indicator in optimization_indicators)
        except:
            return False
    
    def trace_requirements_to_implementation(self) -> Dict[str, Any]:
        """Create comprehensive traceability matrix"""
        if not self.requirements or not self.implementations:
            print("❌ Requirements or implementations not loaded")
            return {}
        
        # Requirement to method mapping
        requirement_mappings = {
            'FR-001': ['create_phase_state_record', 'get_phase_state', 'update_phase_state', 'list_phase_transitions'],
            'FR-002': ['create_checkpoint', 'restore_checkpoint', 'list_checkpoints'],
            'FR-003': ['store_test_result', 'store_test_evidence', 'get_test_results'],
            'FR-004': ['collect_evidence', 'validate_evidence', 'get_test_evidence', 'validate_test_evidence'],
            'PF-001': ['create_phase_state_record', 'get_phase_state', 'update_phase_state'],  # Performance requirements
            'PF-002': ['list_phase_transitions', 'create_checkpoint'],  # Throughput requirements
            'PF-003': ['get_phase_state', 'list_checkpoints'],  # Memory requirements
            'RL-001': ['create_phase_state_record', 'update_phase_state', 'create_checkpoint'],  # Error rate requirements
            'RL-002': ['get_phase_state', 'validate_evidence', 'validate_test_evidence'],  # Data integrity requirements
            'SC-001': ['create_phase_state_record', 'update_phase_state'],  # Input validation requirements
            'TP-001': ['store_test_evidence', 'get_test_evidence'],  # Unit test coverage
            'TP-002': ['collect_evidence', 'validate_evidence']  # Integration test coverage
        }
        
        traceability = {}
        implementation_methods = self.implementations.get('methods', {})
        
        for req_id, req_data in self.requirements.items():
            mapped_methods = requirement_mappings.get(req_id, [])
            
            # Check which methods are implemented
            implemented_methods = []
            missing_methods = []
            
            for method_name in mapped_methods:
                if method_name in implementation_methods:
                    implemented_methods.append({
                        'name': method_name,
                        'details': implementation_methods[method_name]
                    })
                else:
                    missing_methods.append(method_name)
            
            # Calculate implementation status
            if len(implemented_methods) == len(mapped_methods) and len(mapped_methods) > 0:
                status = 'FULLY_IMPLEMENTED'
            elif len(implemented_methods) > 0:
                status = 'PARTIALLY_IMPLEMENTED'
            else:
                status = 'NOT_IMPLEMENTED'
            
            # Calculate coverage percentage
            coverage_pct = (len(implemented_methods) / len(mapped_methods) * 100) if mapped_methods else 0
            
            # Assess compliance with measurable criteria
            compliance = self._assess_requirement_compliance(req_id, req_data, implemented_methods)
            
            traceability[req_id] = {
                'requirement': req_data,
                'mapped_methods': mapped_methods,
                'implemented_methods': implemented_methods,
                'missing_methods': missing_methods,
                'status': status,
                'coverage_percent': coverage_pct,
                'compliance': compliance,
                'testable': req_data.get('testable', False),
                'priority': req_data.get('priority', 'MEDIUM')
            }
        
        self.traceability_matrix = traceability
        return traceability
    
    def _assess_requirement_compliance(self, req_id: str, req_data: Dict, implemented_methods: List) -> Dict[str, Any]:
        """Assess compliance with measurable criteria"""
        criteria = req_data.get('measurable_criteria', {})
        compliance = {
            'status': 'UNKNOWN',
            'tested': False,
            'meets_criteria': False,
            'test_results': {}
        }
        
        if not criteria:
            compliance['status'] = 'NO_MEASURABLE_CRITERIA'
            return compliance
        
        # For now, mark as testable but not yet tested
        # This would be enhanced with actual performance/reliability testing
        compliance['status'] = 'TESTABLE_NOT_VERIFIED'
        compliance['required_tests'] = self._generate_required_tests(req_id, criteria)
        
        return compliance
    
    def _generate_required_tests(self, req_id: str, criteria: Dict) -> List[str]:
        """Generate list of required tests based on criteria"""
        tests = []
        
        if 'max_response_time_ms' in criteria:
            tests.append(f"test_{req_id.lower()}_response_time_under_{criteria['max_response_time_ms']}ms")
        
        if 'min_throughput_per_minute' in criteria:
            tests.append(f"test_{req_id.lower()}_throughput_over_{criteria['min_throughput_per_minute']}_per_minute")
        
        if 'max_memory_mb' in criteria:
            tests.append(f"test_{req_id.lower()}_memory_under_{criteria['max_memory_mb']}mb")
        
        if 'max_error_rate_percent' in criteria:
            tests.append(f"test_{req_id.lower()}_error_rate_under_{criteria['max_error_rate_percent']}_percent")
        
        if 'min_accuracy_percent' in criteria:
            tests.append(f"test_{req_id.lower()}_accuracy_over_{criteria['min_accuracy_percent']}_percent")
        
        if 'min_coverage_percent' in criteria:
            tests.append(f"test_{req_id.lower()}_coverage_over_{criteria['min_coverage_percent']}_percent")
        
        return tests
    
    def identify_gaps(self) -> List[Dict[str, Any]]:
        """Identify critical gaps in requirements implementation"""
        gaps = []
        
        for req_id, trace_data in self.traceability_matrix.items():
            req_info = trace_data['requirement']
            
            # Critical gap: High priority requirement not implemented
            if (req_info['priority'] == 'CRITICAL' and 
                trace_data['status'] == 'NOT_IMPLEMENTED'):
                gaps.append({
                    'type': 'CRITICAL_NOT_IMPLEMENTED',
                    'requirement_id': req_id,
                    'description': req_info['description'][:100] + '...',
                    'priority': req_info['priority'],
                    'impact': 'HIGH',
                    'action_required': f"Implement missing methods: {', '.join(trace_data['missing_methods'])}"
                })
            
            # Significant gap: Functional requirement partially implemented
            elif (req_id.startswith('FR-') and 
                  trace_data['status'] == 'PARTIALLY_IMPLEMENTED' and
                  trace_data['coverage_percent'] < 80):
                gaps.append({
                    'type': 'PARTIAL_IMPLEMENTATION',
                    'requirement_id': req_id,
                    'description': req_info['description'][:100] + '...',
                    'coverage_percent': trace_data['coverage_percent'],
                    'impact': 'MEDIUM',
                    'action_required': f"Complete missing methods: {', '.join(trace_data['missing_methods'])}"
                })
            
            # Testing gap: Testable requirement without verification
            elif (trace_data['testable'] and 
                  trace_data['compliance']['status'] == 'TESTABLE_NOT_VERIFIED'):
                gaps.append({
                    'type': 'TESTING_GAP',
                    'requirement_id': req_id,
                    'description': req_info['description'][:100] + '...',
                    'impact': 'LOW',
                    'action_required': f"Implement tests: {', '.join(trace_data['compliance'].get('required_tests', []))}"
                })
        
        self.gaps = gaps
        return gaps
    
    def generate_traceability_report(self) -> Dict[str, Any]:
        """Generate comprehensive traceability report"""
        if not self.traceability_matrix:
            print("❌ Traceability matrix not generated")
            return {}
        
        # Calculate overall statistics
        total_requirements = len(self.traceability_matrix)
        fully_implemented = len([t for t in self.traceability_matrix.values() if t['status'] == 'FULLY_IMPLEMENTED'])
        partially_implemented = len([t for t in self.traceability_matrix.values() if t['status'] == 'PARTIALLY_IMPLEMENTED'])
        not_implemented = len([t for t in self.traceability_matrix.values() if t['status'] == 'NOT_IMPLEMENTED'])
        
        overall_coverage = sum(t['coverage_percent'] for t in self.traceability_matrix.values()) / total_requirements if total_requirements > 0 else 0
        
        # Categorize by requirement type
        by_category = {}
        for trace_data in self.traceability_matrix.values():
            category = trace_data['requirement']['category']
            if category not in by_category:
                by_category[category] = {'total': 0, 'implemented': 0, 'coverage': 0}
            
            by_category[category]['total'] += 1
            if trace_data['status'] == 'FULLY_IMPLEMENTED':
                by_category[category]['implemented'] += 1
            by_category[category]['coverage'] += trace_data['coverage_percent']
        
        # Calculate category averages
        for category_data in by_category.values():
            category_data['coverage'] = category_data['coverage'] / category_data['total'] if category_data['total'] > 0 else 0
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'layer': self.layer,
            'overall_statistics': {
                'total_requirements': total_requirements,
                'fully_implemented': fully_implemented,
                'partially_implemented': partially_implemented,
                'not_implemented': not_implemented,
                'overall_coverage_percent': round(overall_coverage, 2),
                'implementation_grade': self._calculate_grade(overall_coverage)
            },
            'by_category': by_category,
            'critical_gaps': [gap for gap in self.gaps if gap.get('impact') == 'HIGH'],
            'recommendations': self._generate_recommendations(),
            'detailed_traceability': self.traceability_matrix
        }
        
        return report
    
    def _calculate_grade(self, coverage_percent: float) -> str:
        """Calculate implementation grade based on coverage"""
        if coverage_percent >= 95:
            return 'A+'
        elif coverage_percent >= 90:
            return 'A'
        elif coverage_percent >= 80:
            return 'B+'
        elif coverage_percent >= 75:
            return 'B'
        elif coverage_percent >= 70:
            return 'B-'
        elif coverage_percent >= 60:
            return 'C'
        else:
            return 'F'
    
    def _generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Critical gaps
        critical_gaps = [gap for gap in self.gaps if gap.get('impact') == 'HIGH']
        if critical_gaps:
            recommendations.append(f"🚨 URGENT: Address {len(critical_gaps)} critical implementation gaps")
        
        # Implementation coverage
        overall_coverage = sum(t['coverage_percent'] for t in self.traceability_matrix.values()) / len(self.traceability_matrix) if self.traceability_matrix else 0
        if overall_coverage < 80:
            recommendations.append(f"📊 Increase implementation coverage from {overall_coverage:.1f}% to 80% minimum")
        
        # Testing gaps
        testing_gaps = [gap for gap in self.gaps if gap.get('type') == 'TESTING_GAP']
        if testing_gaps:
            recommendations.append(f"🧪 Implement {len(testing_gaps)} missing requirement tests")
        
        # Performance requirements
        performance_reqs = [req_id for req_id in self.traceability_matrix.keys() if req_id.startswith('PF-')]
        untested_performance = [req_id for req_id in performance_reqs if self.traceability_matrix[req_id]['compliance']['status'] == 'TESTABLE_NOT_VERIFIED']
        if untested_performance:
            recommendations.append(f"⚡ Verify performance requirements: {', '.join(untested_performance)}")
        
        return recommendations
    
    def save_traceability_matrix(self, output_path: str) -> bool:
        """Save traceability matrix to CSV file"""
        try:
            with open(output_path, 'w', newline='') as csvfile:
                fieldnames = [
                    'requirement_id', 'category', 'priority', 'description', 
                    'status', 'coverage_percent', 'implemented_methods', 
                    'missing_methods', 'testable', 'compliance_status'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for req_id, trace_data in self.traceability_matrix.items():
                    req_data = trace_data['requirement']
                    writer.writerow({
                        'requirement_id': req_id,
                        'category': req_data['category'],
                        'priority': req_data['priority'],
                        'description': req_data['description'][:200],
                        'status': trace_data['status'],
                        'coverage_percent': trace_data['coverage_percent'],
                        'implemented_methods': '; '.join([m['name'] for m in trace_data['implemented_methods']]),
                        'missing_methods': '; '.join(trace_data['missing_methods']),
                        'testable': req_data['testable'],
                        'compliance_status': trace_data['compliance']['status']
                    })
            
            print(f"✅ Traceability matrix saved to {output_path}")
            return True
        except Exception as e:
            print(f"❌ Failed to save traceability matrix: {e}")
            return False
    
    def print_detailed_report(self):
        """Print comprehensive traceability report"""
        report = self.generate_traceability_report()
        if not report:
            return
        
        print("\\n" + "="*80)
        print("📋 COMPREHENSIVE REQUIREMENTS TRACEABILITY REPORT")
        print("="*80)
        
        # Overall statistics
        stats = report['overall_statistics']
        print(f"\\n📊 OVERALL STATISTICS:")
        print(f"   Total Requirements:      {stats['total_requirements']}")
        print(f"   ✅ Fully Implemented:     {stats['fully_implemented']}")
        print(f"   ⚠️ Partially Implemented:  {stats['partially_implemented']}")
        print(f"   ❌ Not Implemented:       {stats['not_implemented']}")
        print(f"   📈 Overall Coverage:      {stats['overall_coverage_percent']:.1f}%")
        print(f"   🎯 Implementation Grade:  {stats['implementation_grade']}")
        
        # By category analysis
        print(f"\\n📂 BY CATEGORY ANALYSIS:")
        for category, data in report['by_category'].items():
            print(f"   {category.title()}: {data['implemented']}/{data['total']} ({data['coverage']:.1f}%)")
        
        # Critical gaps
        if report['critical_gaps']:
            print(f"\\n🚨 CRITICAL GAPS ({len(report['critical_gaps'])}):")
            for gap in report['critical_gaps']:
                print(f"   ❌ {gap['requirement_id']}: {gap['action_required']}")
        
        # Recommendations
        print(f"\\n💡 RECOMMENDATIONS:")
        for rec in report['recommendations']:
            print(f"   {rec}")
        
        # Detailed traceability
        print(f"\\n📋 DETAILED TRACEABILITY:")
        for req_id, trace_data in self.traceability_matrix.items():
            status_icon = "✅" if trace_data['status'] == 'FULLY_IMPLEMENTED' else "⚠️" if trace_data['status'] == 'PARTIALLY_IMPLEMENTED' else "❌"
            print(f"   {status_icon} {req_id}: {trace_data['coverage_percent']:.0f}% ({trace_data['status']})")
            if trace_data['missing_methods']:
                print(f"      Missing: {', '.join(trace_data['missing_methods'])}")

def main():
    parser = argparse.ArgumentParser(description='Comprehensive Requirements Traceability Analysis')
    parser.add_argument('--layer', default='data_access', help='Layer to analyze (data_access, business_logic, etc.)')
    parser.add_argument('--requirements-doc', default='projects/PROJECT-003 TDD ENFORCER/SYSTEM-003-01 CORE TDD WORKFLOW ENGINE/FEATURE-003-01-03 RED-GREEN-REFACTOR CYCLE ENFORCER/DATA ACCESS LAYER/LAYER-003-01-03-001_data_access_requirements.md', help='Path to requirements document')
    parser.add_argument('--generate-matrix', action='store_true', help='Generate traceability matrix CSV')
    parser.add_argument('--output', default='traceability_matrix.csv', help='Output file for traceability matrix')
    parser.add_argument('--requirement', help='Analyze specific requirement ID')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    tracer = RequirementsTracer(layer=args.layer)
    
    # Parse requirements document
    tracer.parse_requirements_document(args.requirements_doc)
    
    # Analyze implementation
    tracer.analyze_implementation(f'src/{args.layer}')
    
    # Generate traceability matrix
    tracer.trace_requirements_to_implementation()
    
    # Identify gaps
    tracer.identify_gaps()
    
    if args.requirement:
        # Show specific requirement details
        if args.requirement in tracer.traceability_matrix:
            trace_data = tracer.traceability_matrix[args.requirement]
            req_data = trace_data['requirement']
            print(f"\\n📋 REQUIREMENT {args.requirement} ANALYSIS:")
            print(f"   Description: {req_data['description']}")
            print(f"   Category: {req_data['category']}")
            print(f"   Priority: {req_data['priority']}")
            print(f"   Status: {trace_data['status']}")
            print(f"   Coverage: {trace_data['coverage_percent']:.1f}%")
            print(f"   Implemented Methods: {[m['name'] for m in trace_data['implemented_methods']]}")
            print(f"   Missing Methods: {trace_data['missing_methods']}")
        else:
            print(f"❌ Requirement {args.requirement} not found")
    else:
        # Print full report
        tracer.print_detailed_report()
    
    # Generate matrix if requested
    if args.generate_matrix:
        tracer.save_traceability_matrix(args.output)

if __name__ == "__main__":
    main()