import asyncio
import threading
import psutil

from loguru import logger
from py3nvml.py3nvml import *
from typing import Dict

from taskflow.utils import format_bytes


class SystemState:
    def __init__(self, gpu_available=True) -> None:
        self.memory_free_bytes = 0
        self.gpu_memory_free_bytes: Dict[str, int] = {}
        self.gpu_available = gpu_available

    def update(self):
        self._update_free_memory()
        if self.gpu_available:
            self._update_gpu_free_memory()

    def _update_free_memory(self):
        svmem = psutil.virtual_memory()
        self.memory_free_bytes = svmem.available

    def _update_gpu_free_memory(self):
        device_count = nvmlDeviceGetCount()
        for i in range(device_count):
            handle = nvmlDeviceGetHandleByIndex(i)
            self.gpu_memory_free_bytes[str(i)] = nvmlDeviceGetMemoryInfo(handle).free


class SystemStateUpdateCoroutine:
    def __init__(self, state: SystemState, interval_s: float = 5) -> None:
        self.state = state
        self.interval_s = interval_s
        self.__stop_signal = asyncio.Event()

    async def run(self):
        self.state.update()

        while True:
            should_stop = True
            try:
                await asyncio.wait_for(self.__stop_signal.wait(), self.interval_s)
            except asyncio.TimeoutError:
                should_stop = False
            if should_stop:
                break

            self.state.update()
            logger.debug(f"Free memory: {format_bytes(self.state.memory_free_bytes)}")

    def stop(self):
        self.__stop_signal.set()
