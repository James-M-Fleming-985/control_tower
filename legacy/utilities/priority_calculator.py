#!/usr/bin/env python3
"""
Priority Calculator - Business Logic Layer Implementation

REFACTOR PHASE: Polished implementation with better algorithm and structure
Based on TR-BL-002 specifications from Phase 1 Layer Requirements
"""

from typing import List, Tuple
from datetime import date
from enum import Enum
from dataclasses import dataclass
from src.business_logic.work_item_model import WorkItem, ItemStatus


class PriorityCategory(Enum):
    """Priority categories for work items"""
    OVERDUE = "overdue"
    DUE_TODAY = "due_today"
    FUTURE = "future"
    NO_DATE = "no_date"


@dataclass
class PriorityResult:
    """Result of priority calculation"""
    score: int
    category: PriorityCategory
    rationale: str


class BasicPriorityCalculator:
    """
    Basic priority calculator for Phase 1 implementation
    
    Implements clean, maintainable prioritization logic with clear
    separation of concerns and comprehensive error handling.
    
    Priority Rules (Phase 1):
    1. Overdue items: Priority score 100+ (more overdue = higher score)
    2. Due today items: Priority score 50-99
    3. Future items: Priority score 25-49
    4. No date items: Priority score 10 (lowest)
    5. Within categories: Maintain discovery order
    """
    
    # Priority score ranges
    OVERDUE_BASE_SCORE = 100
    DUE_TODAY_SCORE = 75
    FUTURE_SCORE = 25
    NO_DATE_SCORE = 10
    
    def calculate_priority_score(self, item: WorkItem) -> int:
        """
        Calculate priority score for a work item
        
        Args:
            item: Work item to calculate priority for
            
        Returns:
            Priority score (higher = more urgent)
            
        Raises:
            ValueError: If item is None or invalid
        """
        if not item:
            raise ValueError("Work item cannot be None")
        
        result = self._calculate_priority_detailed(item)
        return result.score
    
    def sort_by_priority(self, items: List[WorkItem]) -> List[WorkItem]:
        """
        Sort work items by priority maintaining discovery order within categories
        
        Args:
            items: List of work items to sort
            
        Returns:
            Sorted list with highest priority items first
            
        Raises:
            ValueError: If items list contains None values
        """
        if not items:
            return []
        
        # Validate input
        if any(item is None for item in items):
            raise ValueError("Work items list cannot contain None values")
        
        # Group items by priority category while maintaining discovery order
        categorized_items = self._categorize_items(items)
        
        # Sort within each category by priority score (stable sort preserves discovery order)
        sorted_categories = self._sort_within_categories(categorized_items)
        
        # Combine categories in priority order
        return self._combine_sorted_categories(sorted_categories)
    
    def is_overdue(self, item: WorkItem) -> bool:
        """
        Check if work item is overdue
        
        Args:
            item: Work item to check
            
        Returns:
            True if item is overdue, False otherwise
        """
        if not item or item.due_date is None:
            return False
        
        # Check both status and actual date for robustness
        return (item.status == ItemStatus.OVERDUE or 
                item.due_date < date.today())
    
    def is_due_today(self, item: WorkItem) -> bool:
        """
        Check if work item is due today
        
        Args:
            item: Work item to check
            
        Returns:
            True if item is due today, False otherwise
        """
        if not item or item.due_date is None:
            return False
        
        # Check both status and actual date for robustness
        return (item.status == ItemStatus.DUE_TODAY or 
                item.due_date == date.today())
    
    def get_priority_explanation(self, item: WorkItem) -> str:
        """
        Get human-readable explanation of priority calculation
        
        Args:
            item: Work item to explain
            
        Returns:
            String explanation of priority reasoning
        """
        result = self._calculate_priority_detailed(item)
        return result.rationale
    
    def _calculate_priority_detailed(self, item: WorkItem) -> PriorityResult:
        """Calculate priority with detailed result information"""
        if item.due_date is None:
            return PriorityResult(
                score=self.NO_DATE_SCORE,
                category=PriorityCategory.NO_DATE,
                rationale="No due date specified - lowest priority"
            )
        
        today = date.today()
        
        if item.due_date < today:
            days_overdue = (today - item.due_date).days
            score = self.OVERDUE_BASE_SCORE + days_overdue
            return PriorityResult(
                score=score,
                category=PriorityCategory.OVERDUE,
                rationale=f"Overdue by {days_overdue} days - highest priority"
            )
        elif item.due_date == today:
            return PriorityResult(
                score=self.DUE_TODAY_SCORE,
                category=PriorityCategory.DUE_TODAY,
                rationale="Due today - high priority"
            )
        else:
            days_until_due = (item.due_date - today).days
            return PriorityResult(
                score=self.FUTURE_SCORE,
                category=PriorityCategory.FUTURE,
                rationale=f"Due in {days_until_due} days - lower priority"
            )
    
    def _categorize_items(self, items: List[WorkItem]) -> dict[PriorityCategory, List[WorkItem]]:
        """Group items by priority category"""
        categories = {
            PriorityCategory.OVERDUE: [],
            PriorityCategory.DUE_TODAY: [],
            PriorityCategory.FUTURE: [],
            PriorityCategory.NO_DATE: []
        }
        
        for item in items:
            result = self._calculate_priority_detailed(item)
            categories[result.category].append(item)
        
        return categories
    
    def _sort_within_categories(self, categorized_items: dict) -> dict:
        """Sort items within each category by priority score"""
        sorted_categories = {}
        
        for category, items in categorized_items.items():
            if category == PriorityCategory.OVERDUE:
                # Sort overdue items by days overdue (most overdue first)
                sorted_items = sorted(items, 
                                    key=lambda x: self.calculate_priority_score(x), 
                                    reverse=True)
            else:
                # Other categories maintain discovery order (stable sort)
                sorted_items = items[:]  # Copy to maintain original order
            
            sorted_categories[category] = sorted_items
        
        return sorted_categories
    
    def _combine_sorted_categories(self, sorted_categories: dict) -> List[WorkItem]:
        """Combine sorted categories in priority order"""
        result = []
        
        # Add categories in priority order
        priority_order = [
            PriorityCategory.OVERDUE,
            PriorityCategory.DUE_TODAY,
            PriorityCategory.FUTURE,
            PriorityCategory.NO_DATE
        ]
        
        for category in priority_order:
            result.extend(sorted_categories[category])
        
        return result