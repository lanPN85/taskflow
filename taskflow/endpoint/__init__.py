from fastapi import FastAPI

from . import task


def bind_app(app: FastAPI):
    """
    Binds API routes to an app

    :type app: FastAPI
    """

    app.include_router(task.router, prefix="/tasks")
