from typing import Any, Optional
from pydantic import BaseModel
from enum import IntEnum


class MessageType(IntEnum):
    """
    Enum for specifying the type of websocket message
    """

    TASK_CAN_START = 1
    INFO_UPDATE = 2
    TASK_FINISH = 3
    TASK_UPDATE = 4


class SocketMessage(BaseModel):
    """
    A message passed through the websocket between taskflow and taskflowd
    """

    type: MessageType
    data: Optional[Any] = None


class ClientUpdateInfo(BaseModel):
    """
    Update info for the taskflow client
    """

    pending_tasks_count: int = 0
    running_tasks_count: int = 0
