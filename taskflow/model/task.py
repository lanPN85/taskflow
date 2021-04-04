import uuid

from pydantic import BaseModel, validator
from enum import IntEnum
from typing import Dict, List, Optional

from taskflow.utils import convert_byte_any, get_timestamp_ms


class TaskPriority(IntEnum):
    LOW = 0
    MEDIUM = 100
    HIGH = 200


class TaskResourceUsage(BaseModel):
    memory_bytes: Optional[int] = None
    gpu_memory_bytes: Optional[Dict[str, int]] = None

    @validator("memory_bytes", "gpu_memory_bytes", pre=True, always=True)
    def convert_byte_value(cls, v):
        return convert_byte_any(v)

class Task(BaseModel):
    id: str
    cmd: str
    created_at: int
    created_by: str
    priority: TaskPriority
    usage: TaskResourceUsage
    is_running: bool = False
    init_delay_s: int = 5


class NewTask(BaseModel):
    cmd: str
    created_by: str
    priority: TaskPriority
    usage: TaskResourceUsage
    init_delay_s: int = 5

    @staticmethod
    def generate_id() -> str:
        return str(uuid.uuid4())[:8]

    def to_task(self) -> Task:
        return Task(
            id=self.generate_id(),
            cmd=self.cmd,
            created_at=get_timestamp_ms(),
            created_by=self.created_by,
            priority=self.priority,
            usage=self.usage,
            init_delay_s=self.init_delay_s
        )
