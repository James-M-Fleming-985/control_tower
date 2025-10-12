```python
import json
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime


class StageStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class StageResult:
    stage_number: int
    stage_name: str
    status: StageStatus
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    duration: Optional[float] = None
    output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result['status'] = self.status.value
        return result


@dataclass
class WorkflowResponse:
    workflow_id: str
    status: str
    stages: List[StageResult]
    total_duration: float
    start_time: float
    end_time: float
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_json(self) -> str:
        data = {
            'workflow_id': self.workflow_id,
            'status': self.status,
            'stages': [stage.to_dict() for stage in self.stages],
            'total_duration': self.total_duration,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'metadata': self.metadata
        }
        return json.dumps(data, indent=2)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'workflow_id': self.workflow_id,
            'status': self.status,
            'stages': [stage.to_dict() for stage in self.stages],
            'total_duration': self.total_duration,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'metadata': self.metadata
        }


class Stage:
    def __init__(self, number: int, name: str, prerequisites: List[int] = None):
        self.number = number
        self.name = name
        self.prerequisites = prerequisites or []

    def validate_prerequisites(self, completed_stages: List[int]) -> bool:
        return all(prereq in completed_stages for prereq in self.prerequisites)

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        time.sleep(0.01)
        return {
            'stage': self.number,
            'name': self.name,
            'result': 'success',
            'timestamp': time.time()
        }


class WorkflowEnforcer:
    def __init__(self):
        self.stages = self._initialize_stages()

    def _initialize_stages(self) -> List[Stage]:
        return [
            Stage(1, "Initialization", []),
            Stage(2, "Validation", [1]),
            Stage(3, "Preparation", [1, 2]),
            Stage(4, "Execution", [1, 2, 3]),
            Stage(5, "Processing", [1, 2, 3, 4]),
            Stage(6, "Analysis", [1, 2, 3, 4, 5]),
            Stage(7, "Verification", [1, 2, 3, 4, 5, 6]),
            Stage(8, "Finalization", [1, 2, 3, 4, 5, 6, 7]),
            Stage(9, "Reporting", [1, 2, 3, 4, 5, 6, 7, 8]),
            Stage(10, "Completion", [1, 2, 3, 4, 5, 6, 7, 8, 9]),
        ]

    def enforce(self, request: str) -> str:
        try:
            request_data = json.loads(request)
        except json.JSONDecodeError as e:
            error_response = {
                'workflow_id': 'unknown',
                'status': 'failed',
                'error': f'Invalid JSON request: {str(e)}',
                'stages': [],
                'total_duration': 0,
                'start_time': time.time(),
                'end_time': time.time()
            }
            return json.dumps(error_response, indent=2)

        workflow_id = request_data.get('workflow_id', f'workflow_{int(time.time())}')
        context = request_data.get('context', {})

        workflow_start = time.time()
        stage_results = []
        completed_stages = []
        workflow_status = 'completed'

        for stage in self.stages:
            stage_result = StageResult(
                stage_number=stage.number,
                stage_name=stage.name,
                status=StageStatus.PENDING
            )

            if not stage.validate_prerequisites(completed_stages):
                stage_result.status = StageStatus.FAILED
                stage_result.error = f"Prerequisites not met: {stage.prerequisites}"
                stage_results.append(stage_result)
                workflow_status = 'failed'
                break

            stage_result.status = StageStatus.RUNNING
            stage_result.start_time = time.time()

            try:
                output = stage.execute(context)
                stage_result.output = output
                stage_result.status = StageStatus.COMPLETED
                completed_stages.append(stage.number)
            except Exception as e:
                stage_result.status = StageStatus.FAILED
                stage_result.error = str(e)
                workflow_status = 'failed'

            stage_result.end_time = time.time()
            stage_result.duration = stage_result.end_time - stage_result.start_time
            stage_results.append(stage_result)

            if stage_result.status == StageStatus.FAILED:
                break

        workflow_end = time.time()
        total_duration = workflow_end - workflow_start

        response = WorkflowResponse(
            workflow_id=workflow_id,
            status=workflow_status,
            stages=stage_results,
            total_duration=total_duration,
            start_time=workflow_start,
            end_time=workflow_end,
            metadata={
                'total_stages': len(self.stages),
                'completed_stages': len(completed_stages),
                'request_data': request_data
            }
        )

        return response.to_json()

    def execute_workflow(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        request_json = json.dumps(request_data)
        response_json = self.enforce(request_json)
        return json.loads(response_json)


def create_enforcer() -> WorkflowEnforcer:
    return WorkflowEnforcer()


def invoke_enforcer(request: Dict[str, Any]) -> Dict[str, Any]:
    enforcer = create_enforcer()
    return enforcer.execute_workflow(request)


def validate_workflow_response(response: Dict[str, Any]) -> bool:
    required_fields = ['workflow_id', 'status', 'stages', 'total_duration', 'start_time', 'end_time']
    if not all(field in response for field in required_fields):
        return False
    
    if not isinstance(response['stages'], list):
        return False
    
    if len(response['stages']) != 10:
        return False
    
    for i, stage in enumerate(response['stages'], 1):
        if stage['stage_number'] != i:
            return False
        if 'status' not in stage:
            return False
    
    return True


def get_workflow_duration(response: Dict[str, Any]) -> float:
    return response.get('total_duration', 0)


def check_prerequisites(stage_number: int, completed_stages: List[int]) -> bool:
    stage_prerequisites = {
        1: [],
        2: [1],
        3: [1, 2],
        4: [1, 2, 3],
        5: [1, 2, 3, 4],
        6: [1, 2, 3, 4, 5],
        7: [1, 2, 3, 4, 5, 6],
        8: [1, 2, 3, 4, 5, 6, 7],
        9: [1, 2, 3, 4, 5, 6, 7, 8],
        10: [1, 2, 3, 4, 5, 6, 7, 8, 9],
    }
    
    prerequisites = stage_prerequisites.get(stage_number, [])
    return all(prereq in completed_stages for prereq in prerequisites)
```