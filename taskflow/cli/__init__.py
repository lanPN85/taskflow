from typer import Typer

from . import run, ps, version


def bind_app(app: Typer):
    app.command()(run.run)
    app.command()(ps.ps)
    app.command()(version.version)
