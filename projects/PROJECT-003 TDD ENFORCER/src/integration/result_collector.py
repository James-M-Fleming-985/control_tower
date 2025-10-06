"""
Result Collector Module

Collects test results from execution and aggregates by pyramid level.

Requirements: REQ-INT-005
"""

from typing import List, Dict, Any


class ResultCollector:
    """Collect and aggregate test execution results"""
    
    def collect_results(
        self, test_execution_output: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Collect test results with pass/fail status and execution time
        
        Args:
            test_execution_output: Raw test execution output
            
        Returns:
            Structured result list
        """
        results = []
        tests = test_execution_output.get('tests', {})
        for test_name, outcome in tests.items():
            results.append({
                'test': test_name,
                'status': outcome.get('status', 'unknown'),
                'duration': outcome.get('duration', 0.0)
            })
        return results
    
    def aggregate_by_level(
        self, results: List[Dict[str, Any]]
    ) -> Dict[str, Dict[str, int]]:
        """
        Aggregate results by pyramid level (unit/integration/e2e)
        
        Args:
            results: List of test results
            
        Returns:
            Aggregated dict with level -> summary
        """
        aggregated = {
            'Unit': {'passed': 0, 'failed': 0},
            'Integration': {'passed': 0, 'failed': 0},
            'E2E': {'passed': 0, 'failed': 0}
        }
        
        for result in results:
            test_name = result.get('test', '')
            category = self._infer_category(test_name)
            
            if result['status'] == 'passed':
                aggregated[category]['passed'] += 1
            else:
                aggregated[category]['failed'] += 1
        
        return aggregated
    
    def _infer_category(self, test_name: str) -> str:
        """Infer category from test name"""
        test_lower = test_name.lower()
        if 'e2e' in test_lower or 'end_to_end' in test_lower:
            return 'E2E'
        elif 'integration' in test_lower or '/integration/' in test_lower:
            return 'Integration'
        else:
            return 'Unit'
    
    def calculate_pass_rates(
        self, aggregated_results: Dict[str, Dict[str, int]]
    ) -> Dict[str, float]:
        """
        Calculate pass rates for each pyramid level
        
        Args:
            aggregated_results: Dict of aggregated results by level
            
        Returns:
            Pass rates as percentages
        """
        pass_rates = {}
        for category, counts in aggregated_results.items():
            total = counts['passed'] + counts['failed']
            if total == 0:
                pass_rates[category] = 0.0
            else:
                pass_rates[category] = (counts['passed'] / total) * 100.0
        return pass_rates
