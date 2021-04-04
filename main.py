import os
import typer
import getpass
import websockets
import asyncio
import json
import signal

from subprocess import Popen
from typing import Optional
from multiprocessing import Process

from taskflow import di
from taskflow.model.task import NewTask, Task, TaskPriority, TaskResourceUsage
from taskflow.model.ws import ClientUpdateInfo, SocketMessage, MessageType

app = typer.Typer()


@app.command()
def run(
    cmd: str,
    file: Optional[str] = typer.Option(None, "-f"),
    save_to_file: Optional[str] = typer.Option(None, "-s")
):
    di.init()
    current_user = getpass.getuser()

    new_task = ask_for_new_task(cmd, current_user)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_proc(new_task))


def ask_for_new_task(cmd: str, user: str) -> NewTask:
    priority = typer.prompt("Task priority (0-LOW, 100-MEDIUM, 200-HIGH)", type=int, default="100")
    try:
        priority = TaskPriority(int(priority))
    except ValueError:
        typer.echo(typer.style("Invalid priority value", fg="red"))
        raise typer.Exit(1)

    memory_usage = typer.prompt("Memory usage (eg. 100M, 2G,...). Leave blank if not known", default="none", show_default=False)

    init_delay_s = typer.prompt("Startup time in seconds. Default is 5", default="5", type=int)

    if memory_usage == "none":
        memory_usage = None

    gpu_memory_usage = None
    if di.nvml_available():
        gpu_names = typer.prompt("GPUs used. Leave blank if none will be used. Separate GPUs with ','.").replace(" ", "")

    return NewTask(
        cmd=cmd,
        created_by=user,
        priority=priority,
        init_delay_s=init_delay_s,
        usage=TaskResourceUsage(
            memory_bytes=memory_usage,
            gpu_memory_bytes=gpu_memory_usage
        )
    )

async def start_proc(
    new_task: NewTask
):
    uri = "ws://localhost:4305/tasks/start"

    async with websockets.connect(uri) as ws:
        try:
            await ws.send(new_task.json())

            data = await ws.recv()
            task = Task.parse_obj(json.loads(data))

            # Wait for start signal
            typer.echo("Waiting for start signal...")
            can_start = False
            while not can_start:
                data = await ws.recv()
                message = SocketMessage.parse_obj(json.loads(data))

                if message.type == MessageType.TASK_CAN_START:
                    can_start = True
                    continue

                if message.type == MessageType.INFO_UPDATE:
                    info = ClientUpdateInfo.parse_obj(message.data)
                    typer.echo(f"Pending tasks: {info.pending_tasks_count}")
                    typer.echo(f"Running tasks: {info.running_tasks_count}")
        except KeyboardInterrupt:
            typer.secho("Task cancelled", fg="red")
            raise typer.Exit(2)

        typer.echo(task.cmd)

        p = Popen(task.cmd, shell=True, env=os.environ)
        try:
            while True:
                is_done = p.poll() is not None
                if is_done:
                    break
        except KeyboardInterrupt:
            p.send_signal(signal.SIGTERM)
            p.wait()

        # Send finish signal
        await ws.send(json.dumps({
            "type": MessageType.TASK_FINISH
        }))
@app.command()
def ls():
    pass

def main():
    app()


if __name__ == "__main__":
    main()
