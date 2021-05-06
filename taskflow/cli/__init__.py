from typer import Typer

from . import run, ps, version, show


def bind_app(app: Typer):
    app.command()(run.run)
    app.command()(ps.ps)
    app.command()(version.version)
    app.command()(show.show)
