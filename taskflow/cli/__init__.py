from typer import Typer

from . import run, ps

def bind_app(app: Typer):
    app.command()(run.run)
    app.command()(ps.ps)
