"""
Concurrent Layer Executor Module.

Implements concurrent execution of layers with semaphore-based limiting
and real-time progress reporting.

Examples:
    >>> executor = ConcurrentLayerExecutor(max_concurrent=5)
    >>> layers = ['layer1', 'layer2', 'layer3', 'layer4', 'layer5']
    >>> results = executor.execute_layers(layers)
    >>> print(f"Processed {len(results)} layers")

Thread Safety:
    All methods are thread-safe using threading.Lock() for state updates
    and threading.Semaphore() for concurrency limiting.
"""
import threading
from queue import Queue
from typing import List, Any, Dict, Optional
import time


class ConcurrentLayerExecutor:
    """
    Executes layers concurrently with a maximum concurrency limit.

    Supports up to 5 concurrent layer executions using semaphore-based
    limiting and FIFO queue management.

    Attributes:
        max_concurrent: Maximum number of layers executing simultaneously
        semaphore: Threading semaphore for concurrency control
        queue: FIFO queue for layer management
        results: Dictionary storing execution results by layer index
        progress: Dictionary tracking execution progress
        lock: Thread lock for state synchronization

    Examples:
        >>> executor = ConcurrentLayerExecutor(max_concurrent=3)
        >>> layers = [1, 2, 3, 4, 5]
        >>> results = executor.execute_layers(layers)
        >>> progress = executor.get_progress()
    """

    def __init__(self, max_concurrent: int = 5):
        """
        Initialize the concurrent layer executor.

        Args:
            max_concurrent: Maximum number of concurrent executions
                          (default: 5, range: 1-10)

        Raises:
            ValueError: If max_concurrent < 1 or > 10
        """
        if max_concurrent < 1 or max_concurrent > 10:
            raise ValueError(
                "max_concurrent must be between 1 and 10"
            )
        self.max_concurrent = max_concurrent
        self.semaphore = threading.Semaphore(max_concurrent)
        self.queue: Queue = Queue()
        self.results: Dict[int, Any] = {}
        self.progress: Dict[str, Any] = {
            "total": 0,
            "completed": 0,
            "running": 0,
            "queued": 0
        }
        self.lock = threading.Lock()

    def execute_layers(self, layers: List[Any]) -> Dict[int, Any]:
        """
        Execute layers concurrently with semaphore limiting.

        Args:
            layers: List of layers to execute (can be any type)

        Returns:
            Dictionary mapping layer index to execution result

        Examples:
            >>> executor = ConcurrentLayerExecutor()
            >>> results = executor.execute_layers(['a', 'b', 'c'])
            >>> len(results) == 3
            True
        """
        if not layers:
            return {}

        with self.lock:
            self.progress["total"] = len(layers)
            self.progress["queued"] = len(layers)
            self.progress["completed"] = 0
            self.progress["running"] = 0

        threads = []
        for idx, layer in enumerate(layers):
            thread = threading.Thread(
                target=self._execute_single_layer,
                args=(idx, layer)
            )
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        return self.results

    def _execute_single_layer(self, idx: int, layer: Any) -> None:
        """
        Execute a single layer with semaphore control.

        Thread-safe execution of individual layers with progress tracking.

        Args:
            idx: Layer index for result storage
            layer: Layer object to execute
        """
        with self.lock:
            self.progress["queued"] -= 1

        self.semaphore.acquire()
        try:
            with self.lock:
                self.progress["running"] += 1

            # Simulate layer execution
            result = self._process_layer(layer)
            self.results[idx] = result

        finally:
            with self.lock:
                self.progress["running"] -= 1
                self.progress["completed"] += 1
            self.semaphore.release()

    def _process_layer(self, layer: Any) -> Any:
        """
        Process a single layer (implementation placeholder).

        Args:
            layer: Layer to process

        Returns:
            Processing result (formatted string)
        """
        # Simulate some processing time
        time.sleep(0.01)
        return f"processed_{layer}"

    def manage_queue(self) -> Dict[str, int]:
        """
        Manage and return queue status.

        Thread-safe access to queue and progress statistics.

        Returns:
            Dictionary with queue statistics including:
                - size: Current queue size
                - total: Total layers to process
                - queued: Layers waiting to start
                - running: Currently executing layers
                - completed: Finished layers

        Examples:
            >>> executor = ConcurrentLayerExecutor()
            >>> status = executor.manage_queue()
            >>> 'size' in status and 'total' in status
            True
        """
        with self.lock:
            return {
                "size": self.queue.qsize(),
                "total": self.progress["total"],
                "queued": self.progress["queued"],
                "running": self.progress["running"],
                "completed": self.progress["completed"]
            }

    def get_progress(self) -> Dict[str, Any]:
        """
        Get current execution progress.

        Thread-safe snapshot of current progress state.

        Returns:
            Dictionary with progress information:
                - total: Total layers
                - completed: Completed layers
                - running: Currently executing
                - queued: Waiting to execute

        Examples:
            >>> executor = ConcurrentLayerExecutor()
            >>> progress = executor.get_progress()
            >>> progress['total'] == 0
            True
        """
        with self.lock:
            return self.progress.copy()


class ProgressReporter:
    """
    Reports real-time progress for concurrent layer execution.

    Provides real-time updates and concurrent execution monitoring with
    thread-safe update tracking.

    Attributes:
        executor: ConcurrentLayerExecutor instance to monitor
        updates: List of progress update snapshots
        lock: Thread lock for update list synchronization

    Examples:
        >>> executor = ConcurrentLayerExecutor()
        >>> reporter = ProgressReporter(executor)
        >>> report = reporter.report_real_time()
        >>> 'timestamp' in report and 'progress' in report
        True
    """

    def __init__(
        self,
        executor: Optional[ConcurrentLayerExecutor] = None
    ):
        """
        Initialize the progress reporter.

        Args:
            executor: Optional ConcurrentLayerExecutor to monitor.
                     If None, reports will show zero progress.
        """
        self.executor = executor
        self.updates: List[Dict[str, Any]] = []
        self.lock = threading.Lock()

    def report_real_time(self) -> Dict[str, Any]:
        """
        Generate real-time progress report.

        Creates a timestamped snapshot of current execution progress
        including percentage completion.

        Returns:
            Dictionary with current progress state:
                - timestamp: Current time (epoch)
                - progress: Progress dictionary
                - percentage: Completion percentage (0-100)

        Examples:
            >>> reporter = ProgressReporter()
            >>> report = reporter.report_real_time()
            >>> report['percentage'] == 0
            True
        """
        if self.executor:
            progress = self.executor.get_progress()
        else:
            progress = {
                "total": 0,
                "completed": 0,
                "running": 0,
                "queued": 0
            }

        report = {
            "timestamp": time.time(),
            "progress": progress,
            "percentage": (
                (progress["completed"] / progress["total"] * 100)
                if progress["total"] > 0 else 0
            )
        }

        with self.lock:
            self.updates.append(report)

        return report

    def report_concurrent(self) -> Dict[str, Any]:
        """
        Generate concurrent execution report.

        Provides detailed statistics about concurrent execution status
        including queue management and concurrency limits.

        Returns:
            Dictionary with concurrent execution statistics:
                - timestamp: Current time (epoch)
                - concurrent_limit: Max concurrent executions
                - currently_running: Active execution count
                - queue_status: Queue statistics
                - total_updates: Number of updates recorded

        Examples:
            >>> executor = ConcurrentLayerExecutor(max_concurrent=3)
            >>> reporter = ProgressReporter(executor)
            >>> report = reporter.report_concurrent()
            >>> report['concurrent_limit'] == 3
            True
        """
        if self.executor:
            queue_status = self.executor.manage_queue()
            progress = self.executor.get_progress()
        else:
            queue_status = {
                "size": 0,
                "total": 0,
                "queued": 0,
                "running": 0,
                "completed": 0
            }
            progress = {
                "total": 0,
                "completed": 0,
                "running": 0,
                "queued": 0
            }

        report = {
            "timestamp": time.time(),
            "concurrent_limit": (
                self.executor.max_concurrent if self.executor else 0
            ),
            "currently_running": progress["running"],
            "queue_status": queue_status,
            "total_updates": len(self.updates)
        }

        return report
