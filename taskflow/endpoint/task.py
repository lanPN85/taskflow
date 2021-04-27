from taskflow.utils import get_timestamp_ms
from typing import Optional
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, Query
from loguru import logger
from websockets.exceptions import ConnectionClosed

from taskflow import di
from taskflow.model.task import Task, NewTask, TaskList
from taskflow.db.base import ITaskflowDb
from taskflow.scheduler import TaskScheduler
from taskflow.model.ws import ClientUpdateInfo, MessageType, SocketMessage

router = APIRouter()


@router.get("/search", response_model=TaskList)
async def search_tasks(
    created_by: Optional[str] = Query(None),
    is_running: Optional[bool] = Query(None),
    start: int = Query(0),
    size: int = Query(20),
    db: ITaskflowDb = Depends(di.db),
):
    """
    Search endpoint for tasks
    """
    return await db.search_tasks(
        created_by=created_by, is_running=is_running, start=start, size=size
    )


@router.websocket("/start")
async def handle_task(
    websocket: WebSocket,
    db: ITaskflowDb = Depends(di.db),
    scheduler: TaskScheduler = Depends(di.scheduler),
):
    """
    Websocket endpoint for starting a task
    """

    task = None
    try:
        await websocket.accept()

        # The client sends the NewTask object
        data = await websocket.receive_json()
        new_task = NewTask.parse_obj(data)

        task_ = new_task.to_task()
        await db.insert_task(task_)
        task = task_

        # Sends the resolved task
        await websocket.send_text(task.json())

        # Waits for execution and sends updates periodically
        while True:
            pending_tasks_count = await db.get_pending_tasks_count()
            running_tasks_count = await db.get_running_tasks_count()
            message = SocketMessage(
                type=MessageType.INFO_UPDATE,
                data=ClientUpdateInfo(
                    pending_tasks_count=pending_tasks_count,
                    running_tasks_count=running_tasks_count,
                ),
            )
            await websocket.send_text(message.json())

            # Check if the task can be executed
            can_start = await scheduler.wait_for_task_execution(task)
            if can_start:
                message = SocketMessage(type=MessageType.TASK_CAN_START)
                await websocket.send_text(message.json())

                task.is_running = True
                task.started_at = get_timestamp_ms()
                await db.update_task(task)

                break

        # Wait for task finish
        can_finish = False
        while not can_finish:
            data = await websocket.receive_json()
            try:
                message = SocketMessage.parse_obj(data)
                if message.type == MessageType.TASK_FINISH:
                    can_finish = True
            except ValueError:
                logger.warning("Invalid JSON data")

        await websocket.close()
    except (WebSocketDisconnect, ConnectionClosed):
        logger.warning("Socket disconnected")
    except Exception as e:
        logger.exception("", e)
        await websocket.close()

    # Cleanup
    if task is not None:
        logger.info(f"Task {task.id} finished")
        await db.delete_task(task)
