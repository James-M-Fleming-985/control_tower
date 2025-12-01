"""
Pydantic schemas for Communication Projects Board API.

Defines request/response models for validation and serialization.
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID


# ==================== Project Schemas ====================

class ProjectBase(BaseModel):
    """Base schema for project data."""
    name: str = Field(..., min_length=1, max_length=255, description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    status: str = Field(default="planning", description="Project status: planning, active, on_hold, completed, archived")
    priority: str = Field(default="medium", description="Project priority: low, medium, high, urgent")
    start_date: Optional[datetime] = Field(None, description="Project start date")
    end_date: Optional[datetime] = Field(None, description="Project end date")
    color: str = Field(default="#4CAF50", description="Hex color code for visual grouping")
    
    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        allowed = ["planning", "active", "on_hold", "completed", "archived"]
        if v not in allowed:
            raise ValueError(f"Status must be one of {allowed}")
        return v
    
    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v):
        allowed = ["low", "medium", "high", "urgent"]
        if v not in allowed:
            raise ValueError(f"Priority must be one of {allowed}")
        return v
    
    @field_validator("color")
    @classmethod
    def validate_color(cls, v):
        if not v.startswith("#") or len(v) != 7:
            raise ValueError("Color must be a valid hex code (e.g., #4CAF50)")
        return v


class ProjectCreate(ProjectBase):
    """Schema for creating a new project."""
    pass


class ProjectUpdate(BaseModel):
    """Schema for updating an existing project (all fields optional)."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    color: Optional[str] = None
    
    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        if v is not None:
            allowed = ["planning", "active", "on_hold", "completed", "archived"]
            if v not in allowed:
                raise ValueError(f"Status must be one of {allowed}")
        return v
    
    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v):
        if v is not None:
            allowed = ["low", "medium", "high", "urgent"]
            if v not in allowed:
                raise ValueError(f"Priority must be one of {allowed}")
        return v


class ProjectResponse(ProjectBase):
    """Schema for project response with calculated fields."""
    id: UUID
    created_at: datetime
    updated_at: datetime
    progress: float = Field(..., description="Project completion percentage (0-100)")
    task_counts: dict = Field(..., description="Task counts by status")
    
    model_config = {
        "from_attributes": True
    }


class ProjectListResponse(BaseModel):
    """Schema for project response in list view."""
    id: UUID
    name: str
    status: str
    priority: str
    color: str
    progress: float
    task_counts: dict
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    model_config = {
        "from_attributes": True
    }


# ==================== Task Schemas ====================

class TaskBase(BaseModel):
    """Base schema for task data."""
    title: str = Field(..., min_length=1, max_length=255, description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    status: str = Field(default="todo", description="Task status: todo, in_progress, blocked, completed")
    priority: str = Field(default="medium", description="Task priority: low, medium, high, urgent")
    due_date: Optional[datetime] = Field(None, description="Task due date")
    position: int = Field(default=0, description="Position for ordering within project")
    estimated_hours: Optional[int] = Field(None, ge=0, description="Estimated hours to complete")
    actual_hours: Optional[int] = Field(None, ge=0, description="Actual hours spent")
    
    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        allowed = ["todo", "in_progress", "blocked", "completed"]
        if v not in allowed:
            raise ValueError(f"Status must be one of {allowed}")
        return v
    
    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v):
        allowed = ["low", "medium", "high", "urgent"]
        if v not in allowed:
            raise ValueError(f"Priority must be one of {allowed}")
        return v


class TaskCreate(TaskBase):
    """Schema for creating a new task."""
    project_id: UUID = Field(..., description="ID of the parent project")
    dependency_ids: Optional[List[UUID]] = Field(default_factory=list, description="IDs of tasks this task depends on")


class TaskUpdate(BaseModel):
    """Schema for updating an existing task (all fields optional)."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[datetime] = None
    position: Optional[int] = None
    estimated_hours: Optional[int] = Field(None, ge=0)
    actual_hours: Optional[int] = Field(None, ge=0)
    project_id: Optional[UUID] = None
    
    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        if v is not None:
            allowed = ["todo", "in_progress", "blocked", "completed"]
            if v not in allowed:
                raise ValueError(f"Status must be one of {allowed}")
        return v


class TaskResponse(TaskBase):
    """Schema for task response with relationships."""
    id: UUID
    project_id: UUID
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    is_blocked: bool = Field(..., description="Whether task is blocked by incomplete dependencies")
    dependency_ids: List[UUID] = Field(default_factory=list, description="IDs of tasks this task depends on")
    
    model_config = {
        "from_attributes": True
    }


class TaskListResponse(BaseModel):
    """Schema for task response in list view."""
    id: UUID
    project_id: UUID
    title: str
    status: str
    priority: str
    due_date: Optional[datetime]
    position: int
    is_blocked: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = {
        "from_attributes": True
    }


# ==================== Calendar Integration Schemas ====================

class CalendarTaskResponse(BaseModel):
    """Schema for tasks formatted for calendar display."""
    id: UUID
    project_id: UUID
    project_name: str
    project_color: str
    title: str
    description: Optional[str]
    status: str
    priority: str
    due_date: datetime
    estimated_hours: Optional[int]
    
    model_config = {
        "from_attributes": True
    }


# ==================== Bulk Operations ====================

class TaskReorderRequest(BaseModel):
    """Schema for reordering tasks within a project."""
    task_id: UUID
    new_position: int = Field(..., ge=0, description="New position in the task list")


class TaskMoveRequest(BaseModel):
    """Schema for moving task to different project."""
    task_id: UUID
    new_project_id: UUID
    new_position: int = Field(default=0, ge=0, description="Position in new project")


class TaskDependencyCreate(BaseModel):
    """Schema for creating a task dependency."""
    depends_on_task_id: UUID = Field(..., description="ID of the task that this task depends on")


class TaskDependencyDelete(BaseModel):
    """Schema for deleting a task dependency."""
    depends_on_task_id: UUID = Field(..., description="ID of the dependency to remove")
