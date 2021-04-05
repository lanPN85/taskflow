from abc import ABC, abstractmethod
from typing import List, Optional

from taskflow.model.task import Task, TaskList


class ITaskflowDb(ABC):
    async def init(self):
        pass

    async def shutdown(self):
        pass

    @abstractmethod
    async def search_tasks(self,
        created_by: Optional[str] = None,
        is_running: Optional[bool] = None,
        start: int = 0,
        size: int = 20,
    ) -> TaskList:
        raise NotImplementedError

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

