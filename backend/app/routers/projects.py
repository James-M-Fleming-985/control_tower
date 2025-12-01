"""
FastAPI router for Communication Projects Board API.

Provides RESTful endpoints for project and task management.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.db.session import get_db
from app.repositories.project_repository import ProjectRepository, TaskRepository
from app.schemas.project_schemas import (
    ProjectCreate, ProjectUpdate, ProjectResponse, ProjectListResponse,
    TaskCreate, TaskUpdate, TaskResponse, TaskListResponse,
    CalendarTaskResponse, TaskReorderRequest, TaskMoveRequest,
    TaskDependencyCreate, TaskDependencyDelete
)
from app.models.project_models import CommunicationProject, ProjectTask

router = APIRouter(prefix="/api/projects", tags=["projects"])


# ==================== Helper Functions ====================

def project_to_response(project: CommunicationProject) -> ProjectResponse:
    """Convert SQLAlchemy project model to Pydantic response."""
    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        status=project.status,
        priority=project.priority,
        start_date=project.start_date,
        end_date=project.end_date,
        color=project.color,
        created_at=project.created_at,
        updated_at=project.updated_at,
        progress=project.calculate_progress(),
        task_counts=project.get_task_counts()
    )


def task_to_response(task: ProjectTask) -> TaskResponse:
    """Convert SQLAlchemy task model to Pydantic response."""
    return TaskResponse(
        id=task.id,
        project_id=task.project_id,
        title=task.title,
        description=task.description,
        status=task.status,
        priority=task.priority,
        due_date=task.due_date,
        completed_at=task.completed_at,
        position=task.position,
        estimated_hours=task.estimated_hours,
        actual_hours=task.actual_hours,
        created_at=task.created_at,
        updated_at=task.updated_at,
        is_blocked=task.is_blocked(),
        dependency_ids=[dep.id for dep in task.dependencies]
    )


# ==================== Project Endpoints ====================

@router.get("/", response_model=List[ProjectListResponse])
def list_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: str = Query(None, description="Filter by status"),
    db: Session = Depends(get_db)
):
    """
    Get all projects with pagination and optional status filter.
    
    Returns project list with progress and task counts.
    """
    if status:
        projects = ProjectRepository.get_by_status(db, status)
    else:
        projects = ProjectRepository.get_all(db, skip=skip, limit=limit)
    
    return [
        ProjectListResponse(
            id=p.id,
            name=p.name,
            status=p.status,
            priority=p.priority,
            color=p.color,
            progress=p.calculate_progress(),
            task_counts=p.get_task_counts(),
            start_date=p.start_date,
            end_date=p.end_date,
            created_at=p.created_at,
            updated_at=p.updated_at
        )
        for p in projects
    ]


@router.post("/", response_model=ProjectResponse, status_code=201)
def create_project(
    project_data: ProjectCreate,
    db: Session = Depends(get_db)
):
    """Create a new communication project."""
    project = ProjectRepository.create(db, project_data)
    return project_to_response(project)


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a project by ID with all its tasks."""
    project = ProjectRepository.get_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project_to_response(project)


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: UUID,
    project_data: ProjectUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing project."""
    project = ProjectRepository.update(db, project_id, project_data)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project_to_response(project)


@router.delete("/{project_id}", status_code=204)
def delete_project(
    project_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete a project (cascades to tasks and dependencies)."""
    success = ProjectRepository.delete(db, project_id)
    if not success:
        raise HTTPException(status_code=404, detail="Project not found")
    return None


@router.post("/{project_id}/duplicate", response_model=ProjectResponse, status_code=201)
def duplicate_project(
    project_id: UUID,
    new_name: str = Query(..., description="Name for the duplicated project"),
    db: Session = Depends(get_db)
):
    """Duplicate a project with all its tasks."""
    project = ProjectRepository.duplicate(db, project_id, new_name)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project_to_response(project)


# ==================== Task Endpoints ====================

@router.get("/{project_id}/tasks", response_model=List[TaskListResponse])
def list_tasks_for_project(
    project_id: UUID,
    db: Session = Depends(get_db)
):
    """Get all tasks for a project."""
    # Verify project exists
    project = ProjectRepository.get_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    tasks = TaskRepository.get_all_for_project(db, project_id)
    return [
        TaskListResponse(
            id=t.id,
            project_id=t.project_id,
            title=t.title,
            status=t.status,
            priority=t.priority,
            due_date=t.due_date,
            position=t.position,
            is_blocked=t.is_blocked(),
            created_at=t.created_at,
            updated_at=t.updated_at
        )
        for t in tasks
    ]


@router.post("/{project_id}/tasks", response_model=TaskResponse, status_code=201)
def create_task(
    project_id: UUID,
    task_data: TaskCreate,
    db: Session = Depends(get_db)
):
    """Create a new task in a project."""
    # Verify project exists
    project = ProjectRepository.get_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Ensure project_id matches route parameter
    if task_data.project_id != project_id:
        raise HTTPException(status_code=400, detail="Project ID mismatch")
    
    try:
        task = TaskRepository.create(db, task_data)
        return task_to_response(task)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a task by ID with dependencies."""
    task = TaskRepository.get_by_id(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task_to_response(task)


@router.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: UUID,
    task_data: TaskUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing task."""
    task = TaskRepository.update(db, task_id, task_data)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task_to_response(task)


@router.patch("/tasks/{task_id}/status", response_model=TaskResponse)
def update_task_status(
    task_id: UUID,
    status: str = Query(..., description="New status"),
    db: Session = Depends(get_db)
):
    """Quick status update for a task."""
    task_data = TaskUpdate(status=status)
    task = TaskRepository.update(db, task_id, task_data)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task_to_response(task)


@router.delete("/tasks/{task_id}", status_code=204)
def delete_task(
    task_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete a task."""
    success = TaskRepository.delete(db, task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return None


# ==================== Task Positioning (Drag-and-Drop) ====================

@router.patch("/tasks/{task_id}/position", response_model=TaskResponse)
def reorder_task(
    task_id: UUID,
    request: TaskReorderRequest,
    db: Session = Depends(get_db)
):
    """Update task position (for drag-and-drop reordering)."""
    if request.task_id != task_id:
        raise HTTPException(status_code=400, detail="Task ID mismatch")
    
    task = TaskRepository.reorder(db, task_id, request.new_position)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task_to_response(task)


@router.post("/tasks/{task_id}/move", response_model=TaskResponse)
def move_task(
    task_id: UUID,
    request: TaskMoveRequest,
    db: Session = Depends(get_db)
):
    """Move task to a different project."""
    if request.task_id != task_id:
        raise HTTPException(status_code=400, detail="Task ID mismatch")
    
    task = TaskRepository.move_to_project(db, task_id, request.new_project_id, request.new_position)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task_to_response(task)


# ==================== Task Dependencies ====================

@router.get("/tasks/{task_id}/dependencies", response_model=List[TaskListResponse])
def get_task_dependencies(
    task_id: UUID,
    db: Session = Depends(get_db)
):
    """Get all dependencies for a task."""
    task = TaskRepository.get_by_id(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return [
        TaskListResponse(
            id=dep.id,
            project_id=dep.project_id,
            title=dep.title,
            status=dep.status,
            priority=dep.priority,
            due_date=dep.due_date,
            position=dep.position,
            is_blocked=dep.is_blocked(),
            created_at=dep.created_at,
            updated_at=dep.updated_at
        )
        for dep in task.dependencies
    ]


@router.post("/tasks/{task_id}/dependencies", status_code=201)
def add_task_dependency(
    task_id: UUID,
    dependency: TaskDependencyCreate,
    db: Session = Depends(get_db)
):
    """Add a dependency to a task."""
    try:
        success = TaskRepository.add_dependency(db, task_id, dependency.depends_on_task_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to add dependency")
        return {"message": "Dependency added successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/tasks/{task_id}/dependencies/{dependency_id}", status_code=204)
def remove_task_dependency(
    task_id: UUID,
    dependency_id: UUID,
    db: Session = Depends(get_db)
):
    """Remove a dependency from a task."""
    success = TaskRepository.remove_dependency(db, task_id, dependency_id)
    if not success:
        raise HTTPException(status_code=404, detail="Dependency not found")
    return None


# ==================== Calendar Integration ====================

@router.get("/calendar/tasks", response_model=List[CalendarTaskResponse])
def get_tasks_for_calendar(db: Session = Depends(get_db)):
    """Get all tasks with due dates for calendar display."""
    tasks = TaskRepository.get_tasks_for_calendar(db)
    
    return [
        CalendarTaskResponse(
            id=task.id,
            project_id=task.project_id,
            project_name=task.project.name,
            project_color=task.project.color,
            title=task.title,
            description=task.description,
            status=task.status,
            priority=task.priority,
            due_date=task.due_date,
            estimated_hours=task.estimated_hours
        )
        for task in tasks
    ]


@router.patch("/tasks/{task_id}/due_date", response_model=TaskResponse)
def update_task_due_date(
    task_id: UUID,
    due_date: str = Query(..., description="New due date (ISO format)"),
    db: Session = Depends(get_db)
):
    """Update task due date (used when dragging on calendar)."""
    from datetime import datetime
    
    try:
        parsed_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
        task_data = TaskUpdate(due_date=parsed_date)
        task = TaskRepository.update(db, task_id, task_data)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        return task_to_response(task)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")
