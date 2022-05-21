import typer

from taskflow import VERSION


def version():
    """
    Prints taskflow version and exits
    """
    typer.echo(VERSION)
