from abc import ABC, abstractmethod
from typing import List, Optional

from taskflow.model.task import Task, TaskList


class ITaskflowDb(ABC):
    """
    Interface for the Taskflow database module
    """

    async def init(self):
        """
        Initializes the database
        """
        pass

    async def shutdown(self):
        """
        Shuts down the database
        """
        pass

    @abstractmethod
    async def search_tasks(
        self,
        created_by: Optional[str] = None,
        is_running: Optional[bool] = None,
        start: int = 0,
        size: int = 20,
    ) -> TaskList:
        """
        Search tasks in the database

        :type created_by: Optional[str], optional
        :type is_running: Optional[bool], optional
        :param start: Offset index, defaults to 0
        :type start: int, optional
        :param size: Number of records to return, defaults to 20
        :type size: int, optional
        :rtype: TaskList
        """
        raise NotImplementedError

    @abstractmethod
    async def get_task_by_id(self, id: str) -> Optional[Task]:
        """
        Finds one task by its id

        :type id: str
        :return: The Task object, or None if not found
        :rtype: Optional[Task]
        """
        raise NotImplementedError

    @abstractmethod
    async def get_pending_tasks(self) -> List[Task]:
        """
        Get all pending tasks

        :rtype: List[Task]
        """
        raise NotImplementedError

    @abstractmethod
    async def get_running_tasks(self) -> List[Task]:
        """
        Get all running tasks

        :rtype: List[Task]
        """
        raise NotImplementedError

    @abstractmethod
    async def get_pending_tasks_count(self) -> int:
        """
        Counts the number of pending tasks

        :rtype: int
        """
        raise NotImplementedError

    @abstractmethod
    async def get_running_tasks_count(self) -> int:
        """
        Counts the number of running tasks

        :rtype: int
        """
        raise NotImplementedError

    @abstractmethod
    async def insert_task(self, task: Task):
        """
        Add a task

        :type task: Task
        """
        raise NotImplementedError

    @abstractmethod
    async def update_task(self, task: Task):
        """
        Update a task

        :type task: Task
        """
        raise NotImplementedError

    @abstractmethod
    async def delete_task(self, task: Task):
        """
        Delete a task

        :type task: Task
        """
        raise NotImplementedError
