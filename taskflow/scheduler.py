import asyncio

from typing import Dict, List, Optional
from functools import cmp_to_key
from loguru import logger

from taskflow.db.base import ITaskflowDb
from taskflow.model.state import SystemState
from taskflow.model.task import TaskPriority, Task

class TaskScheduler:
    DEFAULT_LOOP_INTERVAL_S = 5

    def __init__(self,
        state: SystemState,
        db: ITaskflowDb,
        reserved_memory_bytes: int,
        reserved_gpu_memory_bytes: int
    ) -> None:
        self.state = state
        self.db = db
        self.reserved_memory_bytes = reserved_memory_bytes
        self.reserved_gpu_memory_bytes = reserved_gpu_memory_bytes

        self.__stop_signal = asyncio.Event()
        self.__task_locks: Dict[str, asyncio.Event] = {}

    def stop(self):
        self.__stop_signal.set()

    async def loop(self):
        loop_interval = 0

        logger.debug("Scheduler started")
        while True:
            should_stop = True
            try:
                await asyncio.wait_for(self.__stop_signal.wait(), loop_interval)
            except asyncio.TimeoutError:
                should_stop = False
            if should_stop:
                break

            loop_interval = self.DEFAULT_LOOP_INTERVAL_S

            # Query pending tasks
            pending_tasks = await self.db.get_pending_tasks()
            self.clean_task_locks(pending_tasks)
            if (len(pending_tasks) < 1):
                logger.debug("No tasks pending")
                continue

            sorted_pending_tasks = self._sort_tasks_by_priority(
                pending_tasks
            )

            for task in sorted_pending_tasks:
                if self.can_task_run(task):
                    logger.info(f"Starting task {task.id}")

                    # Open the task's lock for it to run
                    task_lock = self.__task_locks.get(task.id)
                    if task_lock is None:
                        task_lock = asyncio.Event()
                        self.__task_locks[task.id] = task_lock
                    task_lock.set()

                    loop_interval = 2 + task.init_delay_s
                    break


    def clean_task_locks(self, pending_tasks: List[Task]):
        pending_ids = set([
            t.id for t in pending_tasks
        ])
        removed_ids = []
        for task_id in self.__task_locks.keys():
            if task_id not in pending_ids:
                removed_ids.append(task_id)

        if len(removed_ids) > 0:
            logger.debug(f"Cleaning {len(removed_ids)} task locks")
            for id in removed_ids:
                self.__task_locks.pop(id)

    def _sort_tasks_by_priority(self, tasks: List[Task]) -> List[Task]:
        return sorted(tasks, key=cmp_to_key(self.compare_tasks))

    @staticmethod
    def compare_tasks(t1: Task, t2: Task) -> int:
        # Look at priority first
        if t1.priority > t2.priority:
            return -1
        elif t2.priority > t1.priority:
            return 1

        # Older tasks get prioritized
        return t1.created_at - t2.created_at

    def can_task_run(self, task: Task) -> bool:
        task_mem = task.usage.memory_bytes or 0
        if self.state.memory_free_bytes - task_mem <= self.reserved_memory_bytes:
            return False

        if task.usage.gpu_memory_bytes is not None:
            # Check if there's enough space on gpus
            for gpu_id, usage_bytes in task.usage.gpu_memory_bytes.items():
                if gpu_id == "any":
                    is_any_avail = False
                    for avail in self.state.gpu_memory_free_bytes.values():
                        if avail - usage_bytes >= self.reserved_gpu_memory_bytes:
                            is_any_avail = True
                            break
                    if not is_any_avail:
                        return False
                    continue

                avail = self.state.gpu_memory_free_bytes.get(gpu_id, 0)
                if avail - usage_bytes <= self.reserved_gpu_memory_bytes:
                    return False

        return True

    async def wait_for_task_execution(self, task: Task, timeout=1) -> bool:
        task_lock = self.__task_locks.get(task.id)
        if task_lock is None:
            task_lock = asyncio.Event()
            self.__task_locks[task.id] = task_lock

        try:
            await asyncio.wait_for(
                task_lock.wait(), timeout
            )
            return True
        except asyncio.TimeoutError:
            return False
