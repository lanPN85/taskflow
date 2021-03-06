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


class DisplayMode(str, Enum):
    TABLE = "table"
    JSON = "json"
    PIPE = "pipe"


def ps(
    verbose: bool = typer.Option(False, "-v", help="Show additional info for tasks"),
    only_mine: bool = typer.Option(
        False, "--user", "-u", help="Only show tasks started by the current user"
    ),
    only_running: bool = typer.Option(False, "-r", help="Only show running tasks"),
    only_pending: bool = typer.Option(False, "-p", help="Only show pending tasks"),
    display_mode: DisplayMode = typer.Option(
        DisplayMode.TABLE, "-o", help="Set the display format", show_choices=True
    ),
):
    """
    Shows current pending and active tasks
    """

    di.init()
    settings = di.settings()
    current_user = getpass.getuser()

    params: Dict[str, Any] = {
        "start": 0,
        "size": 100,
    }

    if only_mine:
        params["created_by"] = current_user

    if only_running and only_pending:
        typer.secho("Both -r and -p are set", fg="red")
        raise typer.Exit(3)

    if only_running:
        params["is_running"] = True
    elif only_pending:
        params["is_running"] = False

    try:
        response = requests.get(
            f"http://localhost:{settings.api_port}/tasks/search", params=params
        )

        if response.status_code != 200:
            typer.secho(f"Got error response from daemon ({response.status_code})")
            raise typer.Exit(response.status_code)

        data = response.json()
        task_list = TaskList.parse_obj(data)

        if display_mode == DisplayMode.TABLE:
            print_task_table(task_list, abbrev=not verbose)
        elif display_mode == DisplayMode.JSON:
            print_task_json(task_list)
        elif display_mode == DisplayMode.PIPE:
            print_task_pipe(task_list)
    except requests.RequestException:
        typer.secho("Cannot connect to daemon. Is taskflowd running?", fg="red")
        raise typer.Exit(10)

    typer.secho(
        "For more detailed info on tasks, use `taskflow show <task-id>`", fg="yellow"
    )


def print_task_pipe(task_list: TaskList):
    for task in task_list.tasks:
        typer.echo(task.id)


def print_task_json(task_list: TaskList):
    typer.echo(task_list.json(indent=2))


def print_task_table(task_list: TaskList, abbrev=True):
    tasks = task_list.tasks

    if abbrev:
        headers = ["ID", "PID", "Command", "Status"]
    else:
        headers = [
            "ID",
            "PID",
            "Command",
            "Created by",
            "Priority",
            "Delay",
            "Status",
        ]

    rows = []
    for task in tasks:
        cmd = task.cmd
        if len(cmd) > 10:
            cmd = cmd[:10] + "..."

        priority = task.priority.name
        delay = str(task.init_delay_s) + "s"
        status = "PENDING" if not task.is_running else "RUNNING"

        if abbrev:
            rows.append([task.id, task.pid or "N/A", cmd, status])
        else:
            rows.append(
                [
                    task.id,
                    task.pid or "N/A",
                    cmd,
                    task.created_by,
                    priority,
                    delay,
                    status,
                ]
            )

    typer.echo(tabulate.tabulate(rows, headers=headers))
