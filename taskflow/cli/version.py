import typer

from taskflow import VERSION


def version():
    typer.echo(VERSION)
