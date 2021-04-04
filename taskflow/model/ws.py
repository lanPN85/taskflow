from typing import Any, Optional
from pydantic import BaseModel
from enum import IntEnum


class MessageType(IntEnum):
    TASK_CAN_START = 1
    INFO_UPDATE = 2
    TASK_FINISH = 3


class SocketMessage(BaseModel):
    type: MessageType
    data: Optional[Any] = None


class ClientUpdateInfo(BaseModel):
    pending_tasks_count: int = 0
    running_tasks_count: int = 0
