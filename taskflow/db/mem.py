from typing import List, Optional
from littletable import Table

from taskflow.model.task import Task
from .base import ITaskflowDb


class InMemoryDb(ITaskflowDb):
    def __init__(self) -> None:
        super().__init__()
        self.__tasks = Table("tasks")
        self.__tasks.create_index("id", unique=True)

    async def get_task_by_id(self, id: str) -> Optional[Task]:
        try:
            return self.__tasks.by.id[id]
        except KeyError:
            return None

    async def get_pending_tasks_count(self) -> int:
        t = await self.get_pending_tasks()
        return len(t)

    async def get_running_tasks_count(self) -> int:
        t = await self.get_running_tasks()
        return len(t)

    async def get_pending_tasks(self) -> List[Task]:
        return list(self.__tasks.where(
            lambda x: not x.is_running
        ))

    async def get_running_tasks(self) -> List[Task]:
        return list(self.__tasks.where(
            lambda x: x.is_running
        ))

    async def insert_task(self, task: Task):
        self.__tasks.insert(task)

    async def update_task(self, task: Task):
        self.__tasks.delete(id=task.id)
        self.__tasks.insert(task)

    async def delete_task(self, task: Task):
        self.__tasks.delete(id=task.id)
