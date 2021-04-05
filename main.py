import os
from requests.api import head
import typer
import getpass
import websockets
import asyncio
import json
import signal
import yaml
import humanfriendly as hf
import requests
import tabulate

from subprocess import Popen
from typing import Optional, List
from multiprocessing import Process
from datetime import timedelta, datetime

from taskflow import di
from taskflow.model.task import NewTask, Task, TaskList, TaskPriority, TaskResourceUsage
from taskflow.model.ws import ClientUpdateInfo, SocketMessage, MessageType
from taskflow.utils import get_timestamp_ms, format_bytes

app = typer.Typer()


@app.command()
def run(
    cmd: str,
    priority = typer.Option(
        "100", "-p",
        help="Task priority (0-LOW, 100-MEDIUM, 200-HIGH)"
    ),
    memory_usage = typer.Option(
        None, "-m",
        help="Memory usage (eg. 100M, 2G,...)"
    ),
    init_delay_s: int = typer.Option(
        5, "-d", "--delay",
        help="Startup time in seconds"
    ),
    gpu_usage_strings: Optional[List[str]] = typer.Option(
        None, "--gpu",
        help="Specify memory usage for each GPU, with format <gpu-id>:<usage>. Eg. 0:1G"
    ),
    file: Optional[str] = typer.Option(
        None, "-f",
        help="Path to options file to load"
    ),
    save_to_file: Optional[str] = typer.Option(
        None, "-s",
        help="Path to file on which options will be saved"
    )
):
    di.init()
    current_user = getpass.getuser()
    new_task = None

    if file is None:
        # Parse from CLI options
        try:
            priority = TaskPriority(int(priority))
        except ValueError:
            typer.echo(typer.style("Invalid priority value", fg="red"))
            raise typer.Exit(1)

        gpu_memory_usage = None
        if gpu_usage_strings is not None:
            # Parse GPU settings
            gpu_memory_usage = {}
            for gs in gpu_usage_strings:
                gpu_id, usage = gs.split(":")
                gpu_memory_usage[gpu_id] = usage

        new_task = NewTask(
            cmd=cmd,
            created_by=current_user,
            priority=priority,
            init_delay_s=init_delay_s,
            usage=TaskResourceUsage(
                memory_bytes=memory_usage,
                gpu_memory_bytes=gpu_memory_usage
            )
        )
    else:
        # Parse from file
        with open(file, "rt") as f:
            d = yaml.full_load(f)
        d["cmd"] = cmd
        d["created_by"] = current_user
        new_task = NewTask.parse_obj(d)

    # Save to file
    if save_to_file is not None:
        dout = convert_newtask_to_dict(new_task)
        with open(save_to_file, "wt") as f:
            yaml.dump(dout, f)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_proc(
        new_task, port=di.settings().api_port
    ))


async def start_proc(
    new_task: NewTask,
    port: int
):
    uri = f"ws://localhost:{port}/tasks/start"

    async with websockets.connect(uri) as ws:
        try:
            await ws.send(new_task.json())

            data = await ws.recv()
            task = Task.parse_obj(json.loads(data))

            # Wait for start signal
            can_start = False

            os.system("clear")
            while not can_start:
                data = await ws.recv()

                os.system("clear")
                typer.secho("Waiting for start signal...", fg="yellow")
                typer.echo(f"Task id: {task.id}")
                typer.secho(task.cmd, bold=True)
                typer.echo()

                # Print elapsed time
                elapsed_ms = get_timestamp_ms() - task.created_at
                elapsed_td = timedelta(milliseconds=elapsed_ms)
                typer.secho(f"Wait time: {hf.format_timespan(elapsed_td)}", bold=True)

                message = SocketMessage.parse_obj(json.loads(data))

                if message.type == MessageType.TASK_CAN_START:
                    can_start = True
                    continue

                if message.type == MessageType.INFO_UPDATE:
                    info = ClientUpdateInfo.parse_obj(message.data)
                    typer.secho(
                        f"Pending tasks: {info.pending_tasks_count}",
                        fg="blue"
                    )
                    typer.secho(
                        f"Running tasks: {info.running_tasks_count}",
                        fg="blue"
                    )
        except KeyboardInterrupt:
            typer.secho("Task cancelled", fg="red")
            raise typer.Exit(2)

        os.system("clear")
        typer.echo(f"Task id: {task.id}")
        typer.echo(task.cmd)

        p = Popen(task.cmd, shell=True, env=os.environ)
        status = None
        try:
            while True:
                status = p.poll()
                is_done = status is not None
                if is_done:
                    break
                await asyncio.sleep(0.5)
        except KeyboardInterrupt:
            p.send_signal(signal.SIGTERM)
            p.wait()

        # Send finish signal
        try:
            await ws.send(json.dumps({
                "type": MessageType.TASK_FINISH
            }))
        except:
            pass

        raise typer.Exit(status or 0)


def convert_newtask_to_dict(new_task: NewTask):
    dout = json.loads(new_task.json())
    dout.pop("cmd")
    dout.pop("created_by")

    if dout["usage"].get("memory_bytes") is not None:
        dout["usage"]["memory_bytes"] = format_bytes(dout["usage"]["memory_bytes"])
    if dout["usage"].get("gpu_memory_bytes") is not None:
        for k, v in dout["usage"]["gpu_memory_bytes"].items():
            dout["usage"]["gpu_memory_bytes"][k] = format_bytes(v)

    return dout


@app.command()
def ps():
    di.init()
    settings = di.settings()
    current_user = getpass.getuser()

    params = {
        "start": 0,
        "size": 100,
    }

    response = requests.get(
        f"http://localhost:{settings.api_port}/tasks/search",
        params=params
    )

    if response.status_code != 200:
        typer.secho(f"Got error response from daemon ({response.status_code})")
        raise typer.Exit(response.status_code)

    data = response.json()
    task_list = TaskList.parse_obj(data)
    print_task_list(task_list)


def print_task_list(task_list: TaskList):
    tasks = task_list.tasks
    headers = ["ID", "Command", "Created by", "Created at", "Priority", "Delay", "Status"]

    rows = []
    for task in tasks:
        cmd = task.cmd
        if len(cmd) > 10:
            cmd = cmd[:10] + "..."

        created_at_dt = datetime.fromtimestamp(task.created_at / 1000)
        created_at = created_at_dt.strftime("%Y-%m-%d, %H:%M:%S")
        priority = task.priority.name
        delay = str(task.init_delay_s) + "s"
        status = "PENDING" if not task.is_running else "RUNNING"

        rows.append([
            task.id, cmd, task.created_by,
            created_at, priority,
            delay, status
        ])

    typer.echo(tabulate.tabulate(rows, headers=headers))

def main():
    app()


if __name__ == "__main__":
    main()
