import os
import typer
import getpass
import websockets
import asyncio
import json
import signal
import yaml
import humanfriendly as hf

from websockets.exceptions import ConnectionClosed
from halo import Halo
from subprocess import Popen
from typing import Any, Dict, Optional, List
from datetime import timedelta

from taskflow import di
from taskflow.model.task import NewTask, Task, TaskPriority, TaskResourceUsage
from taskflow.model.ws import ClientUpdateInfo, SocketMessage, MessageType
from taskflow.utils import format_timedelta, get_timestamp_ms, format_bytes


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
        60, "-d", "--delay",
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
        await ws.send(new_task.json())

        try:
            data = await ws.recv()
        except ConnectionClosed:
            typer.secho("Daemon stopped unexpectedly", fg="red")
            raise typer.Exit(5)
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
                    info_str = typer.style(f"{info.pending_tasks_count} pending, {info.running_tasks_count} running")
                    display = f"{elapsed_str} - {info_str}\r"
                    spinner.text = display
        except ConnectionClosed:
            spinner.fail("Daemon stopped unexpectedly")
            raise typer.Exit(5)

        spinner.succeed()
        typer.secho("Starting task...", fg="green")

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
            typer.secho("Daemon did not respond", fg="yellow")

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
