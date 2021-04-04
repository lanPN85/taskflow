from taskflow.model.ws import ClientUpdateInfo, MessageType, SocketMessage
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from loguru import logger

from taskflow import di
from taskflow.model.task import Task, NewTask
from taskflow.db.base import ITaskflowDb
from taskflow.scheduler import TaskScheduler

router = APIRouter()


@router.get("/search",
    response_model=Task
)
async def search_tasks(

):
    pass


@router.websocket("/start")
async def handle_task(
    websocket: WebSocket,
    db: ITaskflowDb = Depends(di.db),
    scheduler: TaskScheduler = Depends(di.scheduler)
):
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
                    running_tasks_count=running_tasks_count
                )
            )
            await websocket.send_text(message.json())

            # Check if the task can be executed
            can_start = await scheduler.wait_for_task_execution(task)
            if can_start:
                message = SocketMessage(
                    type=MessageType.TASK_CAN_StART
                )
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
        
    except WebSocketDisconnect:
        logger.warning("Socket disconnected")
    except ValueError:
        logger.warning("Invalid JSON data")
        await websocket.close()
    except Exception as e:
        logger.exception("", e)
        await websocket.close()

    # Cleanup
    if task is not None:
        await db.delete_task(task)
