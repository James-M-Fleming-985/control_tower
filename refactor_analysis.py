#!/usr/bin/env python3
"""
STAGE GATE 6: REFACTOR Analysis & Verification
Professional code quality analysis with systematic refactoring plan
"""

import ast
import os
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass
import time

@dataclass
class RefactorIssue:
    """Represents a code quality issue that needs refactoring"""
    file: str
    type: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    description: str
    line_number: int = 0
    function_name: str = ""
    estimated_effort: str = ""  # QUICK, MODERATE, SUBSTANTIAL

@dataclass
class RefactorPlan:
    """Systematic refactoring plan with priorities"""
    critical_issues: List[RefactorIssue]
    high_priority: List[RefactorIssue]
    medium_priority: List[RefactorIssue]
    estimated_time: str
    success_criteria: List[str]

class RefactorAnalyzer:
    """Professional refactoring analysis with stage gate verification"""
    
    def __init__(self):
        self.issues = []
        self.files_analyzed = []
        
    def analyze_data_access_layer(self) -> RefactorPlan:
        """Analyze all data access layer files for refactoring opportunities"""
        print("🔍 STAGE GATE 6: REFACTOR Analysis - Code Quality Assessment")
        print("=" * 80)
        
        # Key files to analyze
        files_to_analyze = [
            "src/data_access/test_generator.py",
            "src/data_access/tdd_workflow_enforcer.py", 
            "src/data_access/requirements_parser.py",
            "src/data_access/data_models.py",
            "src/data_access/interfaces.py"
        ]
        
        for file_path in files_to_analyze:
            if os.path.exists(file_path):
                print(f"📁 Analyzing {file_path}...")
                self._analyze_file(file_path)
                self.files_analyzed.append(file_path)
        
        return self._create_refactor_plan()
    
    def _analyze_file(self, filepath: str):
        """Analyze individual file for refactoring issues"""
        try:
            with open(filepath, 'r') as f:
                content = f.read()
            
            tree = ast.parse(content)
            lines = content.split('\n')
            file_size = len(lines)
            
            # CRITICAL: Files too large (>800 lines)
            if file_size > 800:
                self.issues.append(RefactorIssue(
                    file=filepath,
                    type="FILE_SIZE",
                    severity="CRITICAL",
                    description=f"File too large: {file_size} lines (should be <800)",
                    estimated_effort="SUBSTANTIAL"
                ))
            
            # Analyze functions
            functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            for func in functions:
                func_lines = getattr(func, 'end_lineno', 0) - func.lineno
                
                # CRITICAL: Functions too large (>50 lines)
                if func_lines > 50:
                    self.issues.append(RefactorIssue(
                        file=filepath,
                        type="FUNCTION_SIZE",
                        severity="CRITICAL" if func_lines > 80 else "HIGH",
                        description=f"Function {func.name}() too large: {func_lines} lines",
                        line_number=func.lineno,
                        function_name=func.name,
                        estimated_effort="MODERATE" if func_lines < 80 else "SUBSTANTIAL"
                    ))
                
                # HIGH: Missing docstrings
                if not ast.get_docstring(func):
                    self.issues.append(RefactorIssue(
                        file=filepath,
                        type="MISSING_DOCSTRING",
                        severity="HIGH",
                        description=f"Missing docstring for {func.name}()",
                        line_number=func.lineno,
                        function_name=func.name,
                        estimated_effort="QUICK"
                    ))
            
            # Check for import issues
            self._check_import_issues(filepath, content)
            
        except Exception as e:
            print(f"❌ Error analyzing {filepath}: {e}")
    
    def _check_import_issues(self, filepath: str, content: str):
        """Check for import-related issues"""
        lines = content.split('\n')
        
        # Check for try/except import blocks (code smell)
        in_try_import = False
        for i, line in enumerate(lines):
            if 'try:' in line and any(imp in lines[i+1] if i+1 < len(lines) else '' 
                                    for imp in ['import', 'from']):
                self.issues.append(RefactorIssue(
                    file=filepath,
                    type="IMPORT_FALLBACK",
                    severity="HIGH",
                    description="Complex fallback import pattern detected",
                    line_number=i+1,
                    estimated_effort="MODERATE"
                ))
                break
    
    def _create_refactor_plan(self) -> RefactorPlan:
        """Create systematic refactoring plan with priorities"""
        critical = [i for i in self.issues if i.severity == "CRITICAL"]
        high = [i for i in self.issues if i.severity == "HIGH"]
        medium = [i for i in self.issues if i.severity == "MEDIUM"]
        
        # Estimate time based on issue complexity
        total_substantial = len([i for i in self.issues if i.estimated_effort == "SUBSTANTIAL"])
        total_moderate = len([i for i in self.issues if i.estimated_effort == "MODERATE"])
        total_quick = len([i for i in self.issues if i.estimated_effort == "QUICK"])
        
        estimated_time = f"{total_substantial*2 + total_moderate*0.5 + total_quick*0.1:.1f} hours"
        
        success_criteria = [
            "All files under 800 lines",
            "All functions under 50 lines", 
            "All public functions have docstrings",
            "Clean import structure",
            "All tests still pass",
            "Code maintainability index >80"
        ]
        
        return RefactorPlan(
            critical_issues=critical,
            high_priority=high,
            medium_priority=medium,
            estimated_time=estimated_time,
            success_criteria=success_criteria
        )
    
    def print_refactor_report(self, plan: RefactorPlan):
        """Print comprehensive refactor analysis report"""
        print(f"\n📊 REFACTOR ANALYSIS COMPLETE")
        print("=" * 50)
        print(f"📁 Files Analyzed: {len(self.files_analyzed)}")
        print(f"🚨 Critical Issues: {len(plan.critical_issues)}")
        print(f"⚠️  High Priority: {len(plan.high_priority)}")
        print(f"📋 Medium Priority: {len(plan.medium_priority)}")
        print(f"⏱️  Estimated Time: {plan.estimated_time}")
        
        if plan.critical_issues:
            print(f"\n🚨 CRITICAL ISSUES (Must Fix First):")
            for issue in plan.critical_issues[:5]:  # Show first 5
                print(f"   📁 {os.path.basename(issue.file)}")
                print(f"      {issue.description}")
                print(f"      Effort: {issue.estimated_effort}")
        
        if plan.high_priority:
            print(f"\n⚠️  HIGH PRIORITY ISSUES:")
            for issue in plan.high_priority[:3]:  # Show first 3
                print(f"   📁 {os.path.basename(issue.file)}")
                print(f"      {issue.description}")
        
        print(f"\n✅ SUCCESS CRITERIA:")
        for criteria in plan.success_criteria:
            print(f"   - {criteria}")
        
        print(f"\n🎯 REFACTOR PLAN PHASES:")
        print("   Phase 1: Fix critical file/function size issues")
        print("   Phase 2: Extract functions and improve structure")  
        print("   Phase 3: Add documentation and clean imports")
        print("   Phase 4: Performance optimization")
        print("   Phase 5: Final quality verification")
        
        return True

def main():
    """Execute Stage Gate 6: REFACTOR Analysis"""
    analyzer = RefactorAnalyzer()
    plan = analyzer.analyze_data_access_layer()
    success = analyzer.print_refactor_report(plan)
    
    if success:
        print(f"\n✅ STAGE GATE 6: REFACTOR Analysis Complete")
        print(f"🎯 Ready to begin systematic refactoring with {len(plan.critical_issues + plan.high_priority)} priority issues")
        return True
    else:
        print(f"\n❌ STAGE GATE 6: Analysis failed")
        return False

if __name__ == "__main__":
    main()