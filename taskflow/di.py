from typing import Optional

from taskflow.model.settings import TaskflowSettings
from taskflow.model.state import SystemState
from taskflow.db.base import ITaskflowDb
from taskflow.db.mem import InMemoryDb
from taskflow.utils import check_has_nvml
from taskflow.scheduler import TaskScheduler

__settings: Optional[TaskflowSettings] = None
__nvml_available: bool = check_has_nvml()
__state: Optional[SystemState] = None
__db: Optional[ITaskflowDb] = None
__scheduler: Optional[TaskScheduler] = None


def init(settings_path="/etc/taskflow/settings.yml"):
    global __settings
    with open(settings_path, "rt") as f:
        __settings = TaskflowSettings.from_yaml(f)

    global __state
    __state = SystemState(gpu_available=nvml_available())

    global __db
    __db = InMemoryDb()

    global __scheduler
    __scheduler = TaskScheduler(
        state=state(),
        db=db(),
        reserved_memory_bytes=settings().reserved_memory_bytes,
        reserved_gpu_memory_bytes=settings().reserved_gpu_memory_bytes,
    )


def settings() -> TaskflowSettings:
    if __settings is None:
        raise ValueError("Value not initialized")
    return __settings


def state() -> SystemState:
    if __state is None:
        raise ValueError("Value not initialized")
    return __state


def db() -> ITaskflowDb:
    if __db is None:
        raise ValueError("Value not initialized")
    return __db


def scheduler() -> TaskScheduler:
    if __scheduler is None:
        raise ValueError("Value not initialized")
    return __scheduler


def nvml_available() -> bool:
    return __nvml_available
