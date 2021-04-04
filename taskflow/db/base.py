from abc import ABC, abstractmethod
from typing import List, Optional

from taskflow.model.task import Task


class ITaskflowDb(ABC):
    async def init(self):
        pass

    async def shutdown(self):
        pass

    @abstractmethod
    async def get_task_by_id(self, id: str) -> Optional[Task]:
        raise NotImplementedError

    @abstractmethod
    async def get_pending_tasks(self) -> List[Task]:
        raise NotImplementedError

    @abstractmethod
    async def get_running_tasks(self) -> List[Task]:
        raise NotImplementedError

    @abstractmethod
    async def get_pending_tasks_count(self) -> int:
        raise NotImplementedError

    @abstractmethod
    async def get_running_tasks_count(self) -> int:
        raise NotImplementedError

    @abstractmethod
    async def insert_task(self, task: Task):
        raise NotImplementedError

    @abstractmethod
    async def update_task(self, task: Task):
        raise NotImplementedError

    @abstractmethod
    async def delete_task(self, task: Task):
        raise NotImplementedError

