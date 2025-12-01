"""
Repository layer for Communication Projects and Tasks.

Provides CRUD operations and business logic for project management.
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.models.project_models import CommunicationProject, ProjectTask, TaskDependency
from app.schemas.project_schemas import (
    ProjectCreate, ProjectUpdate,
    TaskCreate, TaskUpdate,
    TaskDependencyCreate
)


class ProjectRepository:
    """Repository for CommunicationProject operations."""
    
    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[CommunicationProject]:
        """Get all projects with pagination."""
        return db.query(CommunicationProject).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_by_id(db: Session, project_id: UUID) -> Optional[CommunicationProject]:
        """Get project by ID."""
        return db.query(CommunicationProject).filter(CommunicationProject.id == project_id).first()
    
    @staticmethod
    def get_by_status(db: Session, status: str) -> List[CommunicationProject]:
        """Get projects by status."""
        return db.query(CommunicationProject).filter(CommunicationProject.status == status).all()
    
    @staticmethod
    def create(db: Session, project_data: ProjectCreate) -> CommunicationProject:
        """Create a new project."""
        project = CommunicationProject(**project_data.model_dump())
        db.add(project)
        db.commit()
        db.refresh(project)
        return project
    
    @staticmethod
    def update(db: Session, project_id: UUID, project_data: ProjectUpdate) -> Optional[CommunicationProject]:
        """Update an existing project."""
        project = ProjectRepository.get_by_id(db, project_id)
        if not project:
            return None
        
        update_data = project_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(project, field, value)
        
        db.commit()
        db.refresh(project)
        return project
    
    @staticmethod
    def delete(db: Session, project_id: UUID) -> bool:
        """Delete a project (cascades to tasks and dependencies)."""
        project = ProjectRepository.get_by_id(db, project_id)
        if not project:
            return False
        
        db.delete(project)
        db.commit()
        return True
    
    @staticmethod
    def duplicate(db: Session, project_id: UUID, new_name: str) -> Optional[CommunicationProject]:
        """Duplicate a project with all its tasks."""
        original_project = ProjectRepository.get_by_id(db, project_id)
        if not original_project:
            return None
        
        # Create new project
        new_project = CommunicationProject(
            name=new_name,
            description=original_project.description,
            status="planning",  # Reset to planning
            priority=original_project.priority,
            color=original_project.color
        )
        db.add(new_project)
        db.flush()  # Get new_project.id
        
        # Duplicate tasks (without dependencies for now)
        task_mapping = {}  # old_id -> new_task
        for task in original_project.tasks:
            new_task = ProjectTask(
                project_id=new_project.id,
                title=task.title,
                description=task.description,
                status="todo",  # Reset to todo
                priority=task.priority,
                position=task.position,
                estimated_hours=task.estimated_hours
            )
            db.add(new_task)
            db.flush()
            task_mapping[task.id] = new_task
        
        # Recreate dependencies with new task IDs
        for old_task in original_project.tasks:
            new_task = task_mapping[old_task.id]
            for dep in old_task.dependencies:
                if dep.id in task_mapping:
                    new_dep = TaskDependency(
                        task_id=new_task.id,
                        depends_on_task_id=task_mapping[dep.id].id
                    )
                    db.add(new_dep)
        
        db.commit()
        db.refresh(new_project)
        return new_project


class TaskRepository:
    """Repository for ProjectTask operations."""
    
    @staticmethod
    def get_all_for_project(db: Session, project_id: UUID) -> List[ProjectTask]:
        """Get all tasks for a project."""
        return db.query(ProjectTask).filter(ProjectTask.project_id == project_id).order_by(ProjectTask.position).all()
    
    @staticmethod
    def get_by_id(db: Session, task_id: UUID) -> Optional[ProjectTask]:
        """Get task by ID."""
        return db.query(ProjectTask).filter(ProjectTask.id == task_id).first()
    
    @staticmethod
    def get_tasks_for_calendar(db: Session) -> List[ProjectTask]:
        """Get all tasks with due dates for calendar display."""
        return db.query(ProjectTask).filter(ProjectTask.due_date.isnot(None)).all()
    
    @staticmethod
    def create(db: Session, task_data: TaskCreate) -> ProjectTask:
        """Create a new task."""
        # Create task
        task_dict = task_data.model_dump(exclude={"dependency_ids"})
        task = ProjectTask(**task_dict)
        db.add(task)
        db.flush()  # Get task.id
        
        # Add dependencies
        if task_data.dependency_ids:
            for dep_id in task_data.dependency_ids:
                # Check for circular dependencies
                if TaskRepository._would_create_cycle(db, task.id, dep_id):
                    db.rollback()
                    raise ValueError(f"Adding dependency {dep_id} would create a circular dependency")
                
                dep = TaskDependency(
                    task_id=task.id,
                    depends_on_task_id=dep_id
                )
                db.add(dep)
        
        db.commit()
        db.refresh(task)
        return task
    
    @staticmethod
    def update(db: Session, task_id: UUID, task_data: TaskUpdate) -> Optional[ProjectTask]:
        """Update an existing task."""
        task = TaskRepository.get_by_id(db, task_id)
        if not task:
            return None
        
        update_data = task_data.model_dump(exclude_unset=True)
        
        # Handle status change to completed
        if "status" in update_data and update_data["status"] == "completed" and task.status != "completed":
            update_data["completed_at"] = datetime.utcnow()
        
        for field, value in update_data.items():
            setattr(task, field, value)
        
        db.commit()
        db.refresh(task)
        return task
    
    @staticmethod
    def delete(db: Session, task_id: UUID) -> bool:
        """Delete a task (cascades to dependencies)."""
        task = TaskRepository.get_by_id(db, task_id)
        if not task:
            return False
        
        db.delete(task)
        db.commit()
        return True
    
    @staticmethod
    def reorder(db: Session, task_id: UUID, new_position: int) -> Optional[ProjectTask]:
        """Reorder task within its project."""
        task = TaskRepository.get_by_id(db, task_id)
        if not task:
            return None
        
        old_position = task.position
        project_id = task.project_id
        
        # Get all tasks in project
        tasks = db.query(ProjectTask).filter(ProjectTask.project_id == project_id).order_by(ProjectTask.position).all()
        
        # Reorder
        if new_position > old_position:
            # Moving down: shift tasks between old and new position up
            for t in tasks:
                if old_position < t.position <= new_position:
                    t.position -= 1
        else:
            # Moving up: shift tasks between new and old position down
            for t in tasks:
                if new_position <= t.position < old_position:
                    t.position += 1
        
        task.position = new_position
        db.commit()
        db.refresh(task)
        return task
    
    @staticmethod
    def move_to_project(db: Session, task_id: UUID, new_project_id: UUID, new_position: int = 0) -> Optional[ProjectTask]:
        """Move task to a different project."""
        task = TaskRepository.get_by_id(db, task_id)
        if not task:
            return None
        
        old_project_id = task.project_id
        
        # Remove from old project's sequence
        old_tasks = db.query(ProjectTask).filter(ProjectTask.project_id == old_project_id).filter(ProjectTask.position > task.position).all()
        for t in old_tasks:
            t.position -= 1
        
        # Add to new project's sequence
        new_tasks = db.query(ProjectTask).filter(ProjectTask.project_id == new_project_id).filter(ProjectTask.position >= new_position).all()
        for t in new_tasks:
            t.position += 1
        
        task.project_id = new_project_id
        task.position = new_position
        
        db.commit()
        db.refresh(task)
        return task
    
    @staticmethod
    def add_dependency(db: Session, task_id: UUID, depends_on_task_id: UUID) -> bool:
        """Add a dependency to a task."""
        # Check if dependency already exists
        existing = db.query(TaskDependency).filter(
            TaskDependency.task_id == task_id,
            TaskDependency.depends_on_task_id == depends_on_task_id
        ).first()
        
        if existing:
            return True  # Already exists
        
        # Check for circular dependencies
        if TaskRepository._would_create_cycle(db, task_id, depends_on_task_id):
            raise ValueError("Adding this dependency would create a circular dependency")
        
        # Add dependency
        dep = TaskDependency(
            task_id=task_id,
            depends_on_task_id=depends_on_task_id
        )
        db.add(dep)
        db.commit()
        return True
    
    @staticmethod
    def remove_dependency(db: Session, task_id: UUID, depends_on_task_id: UUID) -> bool:
        """Remove a dependency from a task."""
        dep = db.query(TaskDependency).filter(
            TaskDependency.task_id == task_id,
            TaskDependency.depends_on_task_id == depends_on_task_id
        ).first()
        
        if not dep:
            return False
        
        db.delete(dep)
        db.commit()
        return True
    
    @staticmethod
    def _would_create_cycle(db: Session, task_id: UUID, new_dependency_id: UUID) -> bool:
        """
        Check if adding new_dependency_id as a dependency of task_id would create a cycle.
        
        Uses depth-first search to detect cycles.
        """
        if task_id == new_dependency_id:
            return True  # Task cannot depend on itself
        
        visited = set()
        
        def has_path(from_id: UUID, to_id: UUID) -> bool:
            """Check if there's a path from from_id to to_id via dependencies."""
            if from_id == to_id:
                return True
            
            if from_id in visited:
                return False
            
            visited.add(from_id)
            
            # Get all tasks that from_id depends on
            deps = db.query(TaskDependency).filter(TaskDependency.task_id == from_id).all()
            for dep in deps:
                if has_path(dep.depends_on_task_id, to_id):
                    return True
            
            return False
        
        # If new_dependency already has a path to task_id, adding the reverse would create a cycle
        return has_path(new_dependency_id, task_id)
