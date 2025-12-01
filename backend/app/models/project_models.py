"""
SQLAlchemy models for Communication Projects Board feature.

Implements project management with tasks, dependencies, and progress tracking.
"""
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, Table, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from datetime import datetime
from typing import Optional

from app.db.base_class import Base


class CommunicationProject(Base):
    """
    Communication project with tasks and progress tracking.
    
    Represents a top-level project containing multiple tasks.
    Progress is calculated based on completed tasks.
    """
    __tablename__ = "communication_projects"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, default="planning")  # planning, active, on_hold, completed, archived
    priority = Column(String(50), nullable=False, default="medium")  # low, medium, high, urgent
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)
    color = Column(String(7), nullable=False, default="#4CAF50")  # Hex color for visual grouping
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    tasks = relationship("ProjectTask", back_populates="project", cascade="all, delete-orphan", lazy="selectin")
    
    def __repr__(self):
        return f"<CommunicationProject(id={self.id}, name={self.name}, status={self.status})>"
    
    def calculate_progress(self) -> float:
        """
        Calculate project progress based on task completion.
        
        Returns:
            float: Progress percentage (0.0 to 100.0)
        """
        if not self.tasks:
            return 0.0
        
        completed_tasks = sum(1 for task in self.tasks if task.status == "completed")
        total_tasks = len(self.tasks)
        
        return (completed_tasks / total_tasks) * 100.0 if total_tasks > 0 else 0.0
    
    def get_task_counts(self) -> dict:
        """
        Get task counts by status.
        
        Returns:
            dict: Task counts {'total': X, 'todo': Y, 'in_progress': Z, ...}
        """
        counts = {
            "total": len(self.tasks),
            "todo": 0,
            "in_progress": 0,
            "blocked": 0,
            "completed": 0
        }
        
        for task in self.tasks:
            if task.status in counts:
                counts[task.status] += 1
        
        return counts


class ProjectTask(Base):
    """
    Task within a communication project.
    
    Supports status tracking, priorities, due dates, and dependencies.
    Position field enables drag-and-drop ordering within projects.
    """
    __tablename__ = "project_tasks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("communication_projects.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, default="todo")  # todo, in_progress, blocked, completed
    priority = Column(String(50), nullable=False, default="medium")  # low, medium, high, urgent
    due_date = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    position = Column(Integer, nullable=False, default=0)  # For ordering within project
    estimated_hours = Column(Integer, nullable=True)  # Estimated hours to complete
    actual_hours = Column(Integer, nullable=True)  # Actual hours spent
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    project = relationship("CommunicationProject", back_populates="tasks")
    
    # Self-referential many-to-many for dependencies
    dependencies = relationship(
        "ProjectTask",
        secondary="task_dependencies",
        primaryjoin="ProjectTask.id==TaskDependency.task_id",
        secondaryjoin="ProjectTask.id==TaskDependency.depends_on_task_id",
        backref="dependents",
        lazy="selectin"
    )
    
    def __repr__(self):
        return f"<ProjectTask(id={self.id}, title={self.title}, status={self.status})>"
    
    def is_blocked(self) -> bool:
        """
        Check if task is blocked by incomplete dependencies.
        
        Returns:
            bool: True if any dependency is not completed
        """
        return any(dep.status != "completed" for dep in self.dependencies)
    
    def get_blocking_tasks(self) -> list:
        """
        Get list of incomplete dependency tasks that are blocking this task.
        
        Returns:
            list: List of ProjectTask instances that are blocking
        """
        return [dep for dep in self.dependencies if dep.status != "completed"]


# Association table for task dependencies (many-to-many self-referential)
class TaskDependency(Base):
    """
    Task dependency relationship.
    
    Defines that task_id depends on depends_on_task_id.
    Prevents circular dependencies at the application layer.
    """
    __tablename__ = "task_dependencies"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(UUID(as_uuid=True), ForeignKey("project_tasks.id", ondelete="CASCADE"), nullable=False)
    depends_on_task_id = Column(UUID(as_uuid=True), ForeignKey("project_tasks.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    __table_args__ = (
        UniqueConstraint('task_id', 'depends_on_task_id', name='unique_task_dependency'),
    )
    
    def __repr__(self):
        return f"<TaskDependency(task={self.task_id}, depends_on={self.depends_on_task_id})>"
