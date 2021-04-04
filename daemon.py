import asyncio
import sys
import uvicorn
import os
import time
import uvloop

from loguru import logger
from threading import Thread
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from taskflow.endpoint import bind_app
from taskflow import di
from taskflow.model.state import SystemStateUpdateCoroutine
from taskflow.model.settings import TaskflowSettings


def main():
    uvloop.install()
    di.init()
    settings = di.settings()

    is_debug = "TASKFLOW_DEBUG" in os.environ.keys()

    logger.remove()
    if is_debug:
        logger.add(sys.stderr, level="DEBUG")
    else:
        logger.add(sys.stderr, level="INFO")

    if di.nvml_available():
        logger.info("NVML available")
    else:
        logger.info("NVML not available")

    app = setup_api(
        debug= is_debug
    )
    api_coro = ApiCoroutine(
        app=app,
        api_host=settings.api_host,
        api_port=settings.api_port
    )

    state_coro = SystemStateUpdateCoroutine(
        state=di.state(),
        interval_s=settings.system_query_interval
    )

    # Run everything in 1 thread
    # Wait for interrupt signal
    try:
        loop = asyncio.get_event_loop()

        future = asyncio.gather(
            di.scheduler().loop(),
            state_coro.run(),
            api_coro.run()
        )
        loop.run_until_complete(future)
    except KeyboardInterrupt:
        logger.warning("Stopping daemon")

        di.scheduler().stop()
        state_coro.stop()
        api_coro.stop()


def setup_api(debug=False) -> FastAPI:
    app = FastAPI(
        title="Taskflow API",
        debug=debug
    )

    # Routes
    bind_app(app)

    # Middlewares
    app.add_middleware(
        CORSMiddleware,
        allow_origins='*',
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    async def on_startup():
        await di.db().init()

    @app.on_event("shutdown")
    async def on_shutdown():
        await di.db().shutdown()

    return app


class CustomServer(uvicorn.Server):
    def install_signal_handlers(self):
        pass


class ApiCoroutine:
    def __init__(self,
        app: FastAPI,
        api_host: str,
        api_port: int
    ) -> None:
        self.app = app
        self.api_host = api_host
        self.api_port = api_port

        config = uvicorn.Config(
            self.app, host=self.api_host,
            port=self.api_port,
            workers=1,
            loop="none"
        )

        self.server = CustomServer(config)

    async def run(self):
        await self.server.serve()

    def stop(self):
        self.server.should_exit = True


if __name__ == "__main__":
    main()
