import websockets
import getpass
import sys
import shlex
import os
import typer
import json
import asyncio

from loguru import logger
from typing import Tuple
from datetime import timedelta
from contextlib import contextmanager
from websockets.exceptions import ConnectionClosed
from websockets.client import WebSocketClientProtocol
from halo import Halo
from threading import Event, Thread

from taskflow.model.task import NewTask, Task, TaskPriority, TaskResourceUsage
from taskflow.model.ws import ClientUpdateInfo, SocketMessage, MessageType
from taskflow.utils import format_timedelta, get_timestamp_ms, format_timedelta


@contextmanager
def require(
    usage: TaskResourceUsage,
    daemon_host="localhost",
    daemon_port=4305,
    priority: TaskPriority = TaskPriority.MEDIUM,
    init_delay_s: int = 5,
):
    """
    Blocks execution until the underlying task is triggered by the Taskflow daemon
    """
    url = f"ws://{daemon_host}:{daemon_port}/tasks/start"
    new_task = NewTask(
        cmd=f"{shlex.join(sys.argv)}",
        created_by=getpass.getuser(),
        priority=priority,
        usage=usage,
        init_delay_s=init_delay_s,
        pid=os.getpid(),
        cwd=os.getcwd(),
    )

    task, ws = asyncio.get_event_loop().run_until_complete(
        __wait_for_task_start(new_task, url)
    )

    stop_event = Event()
    keepalive_thread = Thread(
        target=__ws_keepalive_loop,
        kwargs=dict(ws=ws, stop_event=stop_event),
        daemon=True,
    )
    keepalive_thread.start()

    try:
        yield task
    finally:
        stop_event.set()
        keepalive_thread.join()

        asyncio.get_event_loop().run_until_complete(__send_shutdown(ws))


def __ws_keepalive_loop(ws: WebSocketClientProtocol, stop_event: Event):
    async def send_ping():
        message = SocketMessage(type=MessageType.PING)
        await ws.send(message.json())

    ev = asyncio.new_event_loop()
    while not stop_event.wait(timeout=1.0):
        ev.run_until_complete(send_ping())


async def __send_shutdown(ws: WebSocketClientProtocol):
    try:
        await ws.send(json.dumps({"type": MessageType.TASK_FINISH}))
    except:
        typer.secho("Daemon did not respond", fg="yellow")


async def __wait_for_task_start(
    new_task: NewTask, uri
) -> Tuple[Task, WebSocketClientProtocol]:
    ws = await websockets.connect(uri)
    await ws.send(new_task.json())

    try:
        data = await ws.recv()
    except ConnectionClosed:
        raise RuntimeError("Daemon stopped unexpectedly")
    task = Task.parse_obj(json.loads(data))

    # Wait for start signal
    can_start = False

    typer.secho("Waiting for start signal...", fg="yellow")
    typer.echo(f"Task id: {task.id}")
    typer.secho(task.cmd, bold=True)

    spinner = Halo(spinner="line")
    spinner.start()

    try:
        while not can_start:
            data = await ws.recv()

            # Print elapsed time
            elapsed_ms = get_timestamp_ms() - task.created_at
            elapsed_td = timedelta(milliseconds=elapsed_ms)
            elapsed_str = typer.style(format_timedelta(elapsed_td), fg="blue")

            message = SocketMessage.parse_obj(json.loads(data))

            if message.type == MessageType.TASK_CAN_START:
                can_start = True
                continue

            if message.type == MessageType.INFO_UPDATE:
                info = ClientUpdateInfo.parse_obj(message.data)
                info_str = typer.style(
                    f"{info.pending_tasks_count} pending, {info.running_tasks_count} running"
                )
                display = f"{elapsed_str} - {info_str}\r"
                spinner.text = display
    except ConnectionClosed:
        spinner.fail()
        raise RuntimeError("Daemon stopped unexpectedly")

    spinner.succeed()
    typer.secho("Starting task...", fg="green")

    # Update task info
    task.started_at = get_timestamp_ms()
    task.is_running = True
    message = SocketMessage(type=MessageType.TASK_UPDATE, data=task)
    await ws.send(message.json())

    return task, ws
