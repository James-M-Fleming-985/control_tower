```python
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import threading


class StageStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class StageResult:
    stage_name: str
    status: StageStatus
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stage_name": self.stage_name,
            "status": self.status.value,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration": self.duration,
            "error": self.error,
            "metadata": self.metadata
        }


@dataclass
class WorkflowProgress:
    current_stage: str
    progress_percentage: float
    total_stages: int
    completed_stages: int
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "current_stage": self.current_stage,
            "progress_percentage": self.progress_percentage,
            "total_stages": self.total_stages,
            "completed_stages": self.completed_stages,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class WorkflowSummary:
    workflow_id: str
    total_stages: int
    completed_stages: int
    failed_stages: int
    total_duration: float
    start_time: datetime
    end_time: Optional[datetime]
    stage_results: List[StageResult]
    status: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "workflow_id": self.workflow_id,
            "total_stages": self.total_stages,
            "completed_stages": self.completed_stages,
            "failed_stages": self.failed_stages,
            "total_duration": self.total_duration,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "stage_results": [result.to_dict() for result in self.stage_results],
            "status": self.status,
            "metadata": self.metadata
        }


class ProgressMonitor:
    def __init__(self, workflow_id: str, stages: List[str], update_interval: int = 10):
        self.workflow_id = workflow_id
        self.stages = stages
        self.update_interval = update_interval
        self.total_stages = len(stages)
        self.current_stage_index = 0
        self.stage_results: Dict[str, StageResult] = {}
        self.start_time = datetime.now()
        self.end_time: Optional[datetime] = None
        self.progress_callbacks = []
        self._monitor_thread: Optional[threading.Thread] = None
        self._stop_monitoring = threading.Event()
        self._lock = threading.Lock()
        
        for stage in stages:
            self.stage_results[stage] = StageResult(
                stage_name=stage,
                status=StageStatus.PENDING
            )

    def register_progress_callback(self, callback):
        """Register a callback for progress updates."""
        self.progress_callbacks.append(callback)

    def start_monitoring(self):
        """Start real-time progress monitoring."""
        if self._monitor_thread is None or not self._monitor_thread.is_alive():
            self._stop_monitoring.clear()
            self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self._monitor_thread.start()

    def stop_monitoring(self):
        """Stop real-time progress monitoring."""
        self._stop_monitoring.set()
        if self._monitor_thread:
            self._monitor_thread.join(timeout=1)

    def _monitor_loop(self):
        """Internal monitoring loop."""
        while not self._stop_monitoring.is_set():
            progress = self.get_progress()
            for callback in self.progress_callbacks:
                try:
                    callback(progress)
                except Exception:
                    pass
            self._stop_monitoring.wait(self.update_interval)

    def start_stage(self, stage_name: str):
        """Mark a stage as started."""
        with self._lock:
            if stage_name not in self.stage_results:
                raise ValueError(f"Stage '{stage_name}' not found in workflow")
            
            stage_result = self.stage_results[stage_name]
            stage_result.status = StageStatus.IN_PROGRESS
            stage_result.start_time = datetime.now()
            
            try:
                self.current_stage_index = self.stages.index(stage_name)
            except ValueError:
                pass

    def complete_stage(self, stage_name: str, metadata: Optional[Dict[str, Any]] = None):
        """Mark a stage as completed."""
        with self._lock:
            if stage_name not in self.stage_results:
                raise ValueError(f"Stage '{stage_name}' not found in workflow")
            
            stage_result = self.stage_results[stage_name]
            stage_result.status = StageStatus.COMPLETED
            stage_result.end_time = datetime.now()
            
            if stage_result.start_time:
                stage_result.duration = (stage_result.end_time - stage_result.start_time).total_seconds()
            
            if metadata:
                stage_result.metadata.update(metadata)

    def fail_stage(self, stage_name: str, error: str):
        """Mark a stage as failed."""
        with self._lock:
            if stage_name not in self.stage_results:
                raise ValueError(f"Stage '{stage_name}' not found in workflow")
            
            stage_result = self.stage_results[stage_name]
            stage_result.status = StageStatus.FAILED
            stage_result.end_time = datetime.now()
            stage_result.error = error
            
            if stage_result.start_time:
                stage_result.duration = (stage_result.end_time - stage_result.start_time).total_seconds()

    def get_progress(self) -> WorkflowProgress:
        """Get current workflow progress."""
        with self._lock:
            completed_stages = sum(
                1 for result in self.stage_results.values()
                if result.status == StageStatus.COMPLETED
            )
            
            progress_percentage = (completed_stages / self.total_stages * 100) if self.total_stages > 0 else 0.0
            
            current_stage = self.stages[self.current_stage_index] if self.current_stage_index < len(self.stages) else self.stages[-1]
            
            return WorkflowProgress(
                current_stage=current_stage,
                progress_percentage=progress_percentage,
                total_stages=self.total_stages,
                completed_stages=completed_stages,
                timestamp=datetime.now()
            )

    def generate_summary(self) -> WorkflowSummary:
        """Generate comprehensive workflow summary report."""
        with self._lock:
            completed_stages = sum(
                1 for result in self.stage_results.values()
                if result.status == StageStatus.COMPLETED
            )
            
            failed_stages = sum(
                1 for result in self.stage_results.values()
                if result.status == StageStatus.FAILED
            )
            
            self.end_time = datetime.now()
            total_duration = (self.end_time - self.start_time).total_seconds()
            
            if failed_stages > 0:
                status = "failed"
            elif completed_stages == self.total_stages:
                status = "completed"
            else:
                status = "in_progress"
            
            stage_results_list = [self.stage_results[stage] for stage in self.stages]
            
            return WorkflowSummary(
                workflow_id=self.workflow_id,
                total_stages=self.total_stages,
                completed_stages=completed_stages,
                failed_stages=failed_stages,
                total_duration=total_duration,
                start_time=self.start_time,
                end_time=self.end_time,
                stage_results=stage_results_list,
                status=status
            )

    def get_stage_result(self, stage_name: str) -> StageResult:
        """Get result for a specific stage."""
        with self._lock:
            if stage_name not in self.stage_results:
                raise ValueError(f"Stage '{stage_name}' not found in workflow")
            return self.stage_results[stage_name]

    def get_timing_metrics(self) -> Dict[str, Any]:
        """Get timing metrics and performance data."""
        with self._lock:
            metrics = {
                "total_duration": (datetime.now() - self.start_time).total_seconds(),
                "stage_durations": {},
                "average_stage_duration": 0.0,
                "slowest_stage": None,
                "fastest_stage": None
            }
            
            completed_durations = []
            
            for stage_name, result in self.stage_results.items():
                if result.duration is not None:
                    metrics["stage_durations"][stage_name] = result.duration
                    completed_durations.append((stage_name, result.duration))
            
            if completed_durations:
                metrics["average_stage_duration"] = sum(d for _, d in completed_durations) / len(completed_durations)
                slowest = max(completed_durations, key=lambda x: x[1])
                fastest = min(completed_durations, key=lambda x: x[1])
                metrics["slowest_stage"] = {"name": slowest[0], "duration": slowest[1]}
                metrics["fastest_stage"] = {"name": fastest[0], "duration": fastest[1]}
            
            return metrics


class WorkflowOrchestrator:
    def __init__(self):
        self.monitors: Dict[str, ProgressMonitor] = {}

    def create_workflow(self, workflow_id: str, stages: List[str], update_interval: int = 10) -> ProgressMonitor:
        """Create a new workflow with progress monitoring."""
        monitor = ProgressMonitor(workflow_id, stages, update_interval)
        self.monitors[workflow_id] = monitor
        return monitor

    def get_monitor(self, workflow_id: str) -> ProgressMonitor:
        """Get progress monitor for a workflow."""
        if workflow_id not in self.monitors:
            raise ValueError(f"Workflow '{workflow_id}' not found")
        return self.monitors[workflow_id]

    def remove_workflow(self, workflow_id: str):
        """Remove a workflow and its monitor."""
        if workflow_id in self.monitors:
            self.monitors[workflow_id].stop_monitoring()
            del self.monitors[workflow_id]
```