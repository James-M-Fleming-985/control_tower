#!/usr/bin/env python3
"""
Priority Calculator - Core Discovery Engine Component

Analyzes work items to calculate priority scores and determine what should be worked on next.
Considers due dates, dependencies, business value, effort estimates, and blocking factors.

Part of the hierarchical requirements management system.
"""
                #!/usr/bin/env python3
"""
Priority Calculator - Core Discovery Engine Component

Analyzes work items to calculate priority scores and determine what should be worked on next.
Considers due dates, dependencies, business value, effort estimates, and blocking factors.

Part of the hierarchical requirements management system.
"""

import sys
import os
from datetime import datetime, date, timedelta
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from enum import Enum

# Import project modules
sys.path.append(os.path.dirname(__file__))
from clean_formatter import CleanOutput, OutputLevel, StatusType

# Import scanner for work items
from repository_scanner import WorkItem, RepositoryScannerendation
            self.formatter.status(StatusType.INFO, f"#{i} {rec.recommendation}")
            self.formatter.status(StatusType.INFO, f"    📋 {item.title[:60]}{'...' if len(item.title) > 60 else ''}")
            
                        # Display hierarchical context with correct terminology per project type
            level_text = f"[{item.requirement_level}]" if item.requirement_level else "[?]"
            
            if item.requirement_level == 'FR':
                # Application: Feature → System → Project → Repository
                # Standard Delivery: Milestone → Workpackage → Project → Repository  
                hierarchy_path = f"Feature/Milestone {level_text} → System/Workpackage → Project → {item.repository}"
            elif item.requirement_level == 'TR':
                # Application: Layer → Feature → System → Project → Repository
                # Standard Delivery: Task → Milestone → Workpackage → Project → Repository
                hierarchy_path = f"Layer/Task {level_text} → Feature/Milestone → System/Workpackage → Project → {item.repository}"
            elif item.requirement_level == 'PR':
                # Both types: Project → Repository
                hierarchy_path = f"Project {level_text} → {item.repository}"
            else:
                # Default: Level → Repository
                hierarchy_path = f"{level_text} → {item.repository}"
            
            self.formatter.status(StatusType.INFO, f"    🗂️  {hierarchy_path} → {item.id}{due_text}")import os
import sys
from datetime import datetime, date, timedelta
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from enum import Enum

# Add the scripts/output directory to sys.path for clean formatter
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'output'))
from clean_formatter import CleanOutput, OutputLevel, StatusType

# Import WorkItem from repository scanner
sys.path.insert(0, os.path.dirname(__file__))
from repository_scanner import WorkItem, RepositoryScanner

class UrgencyLevel(Enum):
    """Urgency levels based on due dates"""
    OVERDUE = 100      # Past due date
    DUE_TODAY = 90     # Due today
    DUE_SOON = 70      # Due within 3 days
    DUE_THIS_WEEK = 50 # Due within 7 days
    DUE_LATER = 30     # Due later
    NO_DEADLINE = 20   # No due date set

class BusinessImpact(Enum):
    """Business impact levels"""
    CRITICAL = 100     # Business critical
    HIGH = 80          # High business value
    MEDIUM = 50        # Medium business value
    LOW = 20           # Low business value
    UNKNOWN = 30       # Unknown business value

class EffortComplexity(Enum):
    """Effort complexity levels"""
    QUICK_WIN = 90     # Easy and high impact
    SMALL = 70         # Small effort
    MEDIUM = 50        # Medium effort  
    LARGE = 30         # Large effort
    MASSIVE = 10       # Massive effort
    UNKNOWN = 40       # Unknown effort

@dataclass
class PriorityScore:
    """Calculated priority score for a work item"""
    work_item: WorkItem
    total_score: float
    urgency_score: float
    business_impact_score: float
    effort_score: float
    dependency_score: float
    recommendation: str
    reasoning: List[str]
    next_action: str

class PriorityCalculator:
    """Calculates priority scores for work items"""
    
    def __init__(self, output_level: OutputLevel = OutputLevel.NORMAL):
        self.formatter = CleanOutput(output_level)
        
    def calculate_priorities(self, work_items: List[WorkItem]) -> List[PriorityScore]:
        """Calculate priority scores for all work items"""
        self.formatter.debug(f"Calculating priorities for {len(work_items)} work items")
        
        # Filter for actionable work based on project type:
        # Application Projects: Show Features (FR) that are due/late
        # Standard Delivery Projects: Show Tasks (TR) and Milestones (PR) that are due/late
        actionable_items = []
        
        for item in work_items:
            # Include if it has a due date and isn't NSR (long-term vision)
            if item.due_date and item.requirement_level != 'NSR':
                # Application Projects: Include Features (FR)
                # Standard Delivery: Include Project milestones (PR) and Tasks (TR)
                if item.requirement_level in ['FR', 'PR', 'TR']:
                    actionable_items.append(item)
        
        self.formatter.debug(f"Filtered to {len(actionable_items)} actionable items (Features for Apps, Milestones/Tasks for Delivery)")
        
        priority_scores = []
        
        for item in actionable_items:
            score = self._calculate_single_priority(item, actionable_items)
            priority_scores.append(score)
        
        # Sort by total score (highest first)
        priority_scores.sort(key=lambda x: x.total_score, reverse=True)
        
        return priority_scores
    
    def _calculate_single_priority(self, item: WorkItem, all_items: List[WorkItem]) -> PriorityScore:
        """Calculate priority score for a single work item"""
        
        # Calculate component scores
        urgency_score = self._calculate_urgency(item)
        business_impact_score = self._calculate_business_impact(item)
        effort_score = self._calculate_effort_score(item)
        dependency_score = self._calculate_dependency_score(item, all_items)
        
        # Weight the scores (can be tuned)
        weights = {
            'urgency': 0.35,        # Due dates are important
            'business_impact': 0.30, # Business value matters
            'effort': 0.20,         # Prefer easier tasks when equal
            'dependency': 0.15      # Dependencies matter but less
        }
        
        total_score = (
            urgency_score * weights['urgency'] +
            business_impact_score * weights['business_impact'] +
            effort_score * weights['effort'] +
            dependency_score * weights['dependency']
        )
        
        # Generate recommendation and reasoning
        recommendation, reasoning, next_action = self._generate_recommendation(
            item, urgency_score, business_impact_score, effort_score, dependency_score
        )
        
        return PriorityScore(
            work_item=item,
            total_score=total_score,
            urgency_score=urgency_score,
            business_impact_score=business_impact_score,
            effort_score=effort_score,
            dependency_score=dependency_score,
            recommendation=recommendation,
            reasoning=reasoning,
            next_action=next_action
        )
    
    def _calculate_urgency(self, item: WorkItem) -> float:
        """Calculate urgency score based on due date"""
        if not item.due_date:
            return UrgencyLevel.NO_DEADLINE.value
        
        try:
            due = datetime.fromisoformat(item.due_date).date()
            today = date.today()
            days_until_due = (due - today).days
            
            if days_until_due < 0:  # Overdue
                return UrgencyLevel.OVERDUE.value
            elif days_until_due == 0:  # Due today
                return UrgencyLevel.DUE_TODAY.value
            elif days_until_due <= 3:  # Due soon
                return UrgencyLevel.DUE_SOON.value
            elif days_until_due <= 7:  # Due this week
                return UrgencyLevel.DUE_THIS_WEEK.value
            else:  # Due later
                return UrgencyLevel.DUE_LATER.value
                
        except ValueError:
            return UrgencyLevel.NO_DEADLINE.value
    
    def _calculate_business_impact(self, item: WorkItem) -> float:
        """Calculate business impact score"""
        business_value = item.business_value
        
        if not business_value:
            return BusinessImpact.UNKNOWN.value
        
        value_lower = business_value.lower()
        
        if value_lower in ['critical', 'blocker']:
            return BusinessImpact.CRITICAL.value
        elif value_lower in ['high', 'important']:
            return BusinessImpact.HIGH.value
        elif value_lower in ['medium', 'moderate']:
            return BusinessImpact.MEDIUM.value
        elif value_lower in ['low', 'nice-to-have']:
            return BusinessImpact.LOW.value
        else:
            return BusinessImpact.UNKNOWN.value
    
    def _calculate_effort_score(self, item: WorkItem) -> float:
        """Calculate effort score (higher score = easier/quicker tasks)"""
        effort = item.effort_estimate
        
        if not effort:
            return EffortComplexity.UNKNOWN.value
        
        effort_lower = effort.lower()
        
        # Quick wins: high business value + low effort
        business_high = item.business_value and item.business_value.lower() in ['high', 'critical']
        
        if any(keyword in effort_lower for keyword in ['quick', 'easy', 'simple', '1 hour', '30 min']):
            return EffortComplexity.QUICK_WIN.value if business_high else EffortComplexity.SMALL.value
        elif any(keyword in effort_lower for keyword in ['small', 'short', '1-2 hours', 'half day']):
            return EffortComplexity.SMALL.value
        elif any(keyword in effort_lower for keyword in ['medium', '1 day', '2-3 hours']):
            return EffortComplexity.MEDIUM.value
        elif any(keyword in effort_lower for keyword in ['large', 'big', '2-3 days', 'week']):
            return EffortComplexity.LARGE.value
        elif any(keyword in effort_lower for keyword in ['massive', 'huge', 'weeks', 'months']):
            return EffortComplexity.MASSIVE.value
        else:
            return EffortComplexity.UNKNOWN.value
    
    def _calculate_dependency_score(self, item: WorkItem, all_items: List[WorkItem]) -> float:
        """Calculate dependency score (higher = fewer blockers)"""
        base_score = 70.0  # Default score
        
        # Reduce score for each dependency
        dependency_penalty = len(item.dependencies) * 10
        
        # Check if this item is blocking others (increases priority)
        blocking_bonus = 0
        item_id = item.id
        for other_item in all_items:
            if item_id in other_item.dependencies:
                blocking_bonus += 15  # This item is blocking others
        
        # Check if dependencies are completed
        completed_dependencies = 0
        for dep_id in item.dependencies:
            for other_item in all_items:
                if other_item.id == dep_id and other_item.status.lower() in ['completed', 'done']:
                    completed_dependencies += 1
        
        # Bonus for having completed dependencies
        completion_bonus = completed_dependencies * 5
        
        return min(100, max(0, base_score - dependency_penalty + blocking_bonus + completion_bonus))
    
    def _generate_recommendation(self, item: WorkItem, urgency: float, business: float, 
                               effort: float, dependency: float) -> Tuple[str, List[str], str]:
        """Generate recommendation and reasoning for work item"""
        reasoning = []
        
        # Analyze urgency
        if urgency >= UrgencyLevel.OVERDUE.value:
            reasoning.append("⚠️ OVERDUE - immediate attention required")
        elif urgency >= UrgencyLevel.DUE_TODAY.value:
            reasoning.append("🎯 Due today - high priority")
        elif urgency >= UrgencyLevel.DUE_SOON.value:
            reasoning.append("📅 Due within 3 days")
        
        # Analyze business impact
        if business >= BusinessImpact.CRITICAL.value:
            reasoning.append("🔥 Critical business impact")
        elif business >= BusinessImpact.HIGH.value:
            reasoning.append("💼 High business value")
        
        # Analyze effort
        if effort >= EffortComplexity.QUICK_WIN.value:
            reasoning.append("⚡ Quick win - high impact, low effort")
        elif effort >= EffortComplexity.SMALL.value:
            reasoning.append("✅ Small effort required")
        elif effort <= EffortComplexity.LARGE.value:
            reasoning.append("⏳ Large effort required")
        
        # Analyze dependencies
        if dependency <= 30:
            reasoning.append("🚫 Blocked by dependencies")
        elif dependency >= 80:
            reasoning.append("🚀 No blocking dependencies")
        
        # Generate recommendation
        total_score = urgency * 0.35 + business * 0.30 + effort * 0.20 + dependency * 0.15
        
        if total_score >= 80:
            recommendation = "🔴 WORK ON THIS NOW"
        elif total_score >= 65:
            recommendation = "🟡 HIGH PRIORITY"
        elif total_score >= 45:
            recommendation = "🟢 MEDIUM PRIORITY"
        else:
            recommendation = "⚪ LOW PRIORITY"
        
        # Generate next action
        if item.status.lower() in ['not started', 'todo']:
            next_action = f"make work-on ITEM={item.id}"
        elif item.status.lower() == 'in progress':
            next_action = f"Continue work on {item.id}"
        else:
            next_action = f"Review status of {item.id}"
        
        return recommendation, reasoning, next_action
    
    def get_top_recommendations(self, priority_scores: List[PriorityScore], 
                              limit: int = 5) -> List[PriorityScore]:
        """Get top N recommendations"""
        return priority_scores[:limit]
    
    def format_recommendations(self, recommendations: List[PriorityScore]) -> None:
        """Format and display recommendations using clean output"""
        if not recommendations:
            self.formatter.status(StatusType.INFO, "No work items found")
            return
        
        self.formatter.header("🎯 What Should You Work On Next?")
        
        for i, rec in enumerate(recommendations[:5], 1):
            item = rec.work_item
            
            # Format the work item nicely
            due_text = ""
            if item.due_date:
                try:
                    due = datetime.fromisoformat(item.due_date).date()
                    days_diff = (due - date.today()).days
                    if days_diff < 0:
                        due_text = f" (OVERDUE by {abs(days_diff)} days)"
                    elif days_diff == 0:
                        due_text = f" (DUE TODAY)"
                    elif days_diff <= 7:
                        due_text = f" (due in {days_diff} days)"
                except ValueError:
                    pass
            
            # Main recommendation
            self.formatter.status(StatusType.INFO, f"#{i} {rec.recommendation}")
            self.formatter.status(StatusType.INFO, f"    📋 {item.title[:60]}{'...' if len(item.title) > 60 else ''}")
            
            # Add requirement level indicator and hierarchical context
            level_text = f"[{item.requirement_level}]" if item.requirement_level else "[?]"
            hierarchy_path = f"{item.repository} → {level_text}"
            self.formatter.status(StatusType.INFO, f"    �️  {hierarchy_path} → {item.id}{due_text}")
            
            # Show reasoning (top 2 reasons)
            if rec.reasoning:
                for reason in rec.reasoning[:2]:
                    self.formatter.status(StatusType.INFO, f"    {reason}")
            
            # Next action
            self.formatter.status(StatusType.SUCCESS, f"    ▶️  {rec.next_action}")
            
            if i < len(recommendations):
                self.formatter.section_break()

def main():
    """Main entry point for priority calculator"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Calculate work item priorities")
    parser.add_argument("--base-path", default="/workspaces/control_tower/cloned_repos",
                       help="Base path for repositories")
    parser.add_argument("--top", type=int, default=5, help="Number of top recommendations")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--quiet", action="store_true", help="Quiet output")
    
    args = parser.parse_args()
    
    # Set output level
    if args.quiet:
        output_level = OutputLevel.QUIET
    elif args.verbose:
        output_level = OutputLevel.VERBOSE
    else:
        output_level = OutputLevel.NORMAL
    
    # Get work items from scanner
    scanner = RepositoryScanner(args.base_path, output_level)
    repositories = scanner.scan_all_repositories()
    all_work_items = scanner.get_all_work_items()
    
    # Calculate priorities
    calculator = PriorityCalculator(output_level)
    priority_scores = calculator.calculate_priorities(all_work_items)
    
    # Get and display top recommendations
    top_recommendations = calculator.get_top_recommendations(priority_scores, args.top)
    calculator.format_recommendations(top_recommendations)

if __name__ == "__main__":
    main()