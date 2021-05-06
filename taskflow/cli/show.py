import os
import typer
import getpass
import humanfriendly as hf
import requests
import tabulate

from enum import Enum
from typing import Any, Dict, Optional, List
from datetime import timedelta, datetime

from taskflow import di
from taskflow.model.task import NewTask, Task, TaskList, TaskPriority, TaskResourceUsage
from taskflow.utils import format_int_timestamp, get_timestamp_ms, format_bytes


def show(task_id: str):
    """
    Function for taskflow show
    """
    di.init()
    settings = di.settings()

    try:
        response = requests.get(
            f"http://localhost:{settings.api_port}/tasks/id/{task_id}"
        )

        if response.status_code == 404:
            typer.secho(f"Task with id {task_id} not found", fg="red")
            raise typer.Exit(404)

        if response.status_code != 200:
            typer.secho(f"Got error response from daemon ({response.status_code})")
            raise typer.Exit(response.status_code)

        data = response.json()
        task = Task.parse_obj(data)
        print_task(task)

    except requests.RequestException:
        typer.secho("Cannot connect to daemon. Is taskflowd running?", fg="red")
        raise typer.Exit(10)


def print_task(task: Task):
    priority = task.priority.name
    delay = str(task.init_delay_s) + "s"
    status = "PENDING" if not task.is_running else "RUNNING"
    created_at = format_int_timestamp(task.created_at)
    started_at = format_int_timestamp(task.started_at)
    memory_usage = (
        format_bytes(task.usage.memory_bytes)
        if task.usage.memory_bytes is not None
        else "N/A"
    )

    gpu_bytes = task.usage.gpu_memory_bytes or {}
    gpu_usages = []
    for k, v in gpu_bytes.items():
        val = format_bytes(v)
        gpu_usages.append(f"{k}:{val}")
    gpu_usage_str = "N/A"
    if len(gpu_usages) > 0:
        gpu_usage_str = " ".join(gpu_usages)

    typer.secho(f"Task {task.id} (PID={task.pid or 'None'})", bold=True)
    typer.echo(f"Command: {task.cmd}")
    typer.echo(f"Working directory: {task.cwd or 'N/A'}")
    typer.echo()

    typer.secho(f"RAM usage: {memory_usage}")
    typer.echo(f"GPU usage: {gpu_usage_str}")
    typer.echo()

    typer.echo(f"Status: {status}")
    typer.echo(f"Priority: {priority}")
    typer.echo(f"Created by: {task.created_by}")
    typer.secho(f"Created at: {created_at}")
    typer.secho(f"Started at: {started_at}")
