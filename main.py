"""
Entrypoint for the Taskflow CLI
"""

import typer

from taskflow.cli import bind_app

app = typer.Typer()


def main():
    bind_app(app)
    app()


if __name__ == "__main__":
    main()
