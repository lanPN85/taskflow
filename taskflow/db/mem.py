from typing import List, Optional
from littletable import Table

from taskflow.model.task import Task, TaskList
from .base import ITaskflowDb


class InMemoryDb(ITaskflowDb):
    """
    In-memory implementation of ITaskflowDB
    """

    def __init__(self) -> None:
        super().__init__()
        self.__tasks = Table("tasks")
        self.__tasks.create_index("id", unique=True)

    async def search_tasks(
        self,
        created_by: Optional[str] = None,
        is_running: Optional[bool] = None,
        start: int = 0,
        size: int = 20,
    ) -> TaskList:
        t = self.__tasks.clone()

        if created_by is not None:
            t = t.where(created_by=created_by)

        if is_running is not None:
            t = t.where(is_running=is_running)

        t.sort("created_at")

        total = len(t)

        t = t[start : start + size]

        return TaskList(tasks=list(t), total=total)

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
        return list(self.__tasks.where(lambda x: not x.is_running))

    async def get_running_tasks(self) -> List[Task]:
        return list(self.__tasks.where(lambda x: x.is_running))

    async def insert_task(self, task: Task):
        self.__tasks.insert(task)

    async def update_task(self, task: Task):
        self.__tasks.delete(id=task.id)
        self.__tasks.insert(task)

    async def delete_task(self, task: Task):
        self.__tasks.delete(id=task.id)
