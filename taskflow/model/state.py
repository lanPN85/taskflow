import asyncio
import threading
import psutil

from loguru import logger
from py3nvml.py3nvml import *
from typing import Dict

from taskflow.utils import format_bytes


class SystemState:
    """
    Class for managing the local system's state
    """

    __slots__ = ["memory_free_bytes", "gpu_memory_free_bytes", "gpu_available"]

    def __init__(self, gpu_available=True) -> None:
        self.memory_free_bytes = 0
        self.gpu_memory_free_bytes: Dict[str, int] = {}
        self.gpu_available = gpu_available

    def update(self):
        """
        Update the state by running OS queries
        """
        self._update_free_memory()
        if self.gpu_available:
            self._update_gpu_free_memory()

    def _update_free_memory(self):
        """
        Update the amount of available memory
        """
        svmem = psutil.virtual_memory()
        self.memory_free_bytes = svmem.available

    def _update_gpu_free_memory(self):
        """
        Update the amount of available GPU memory
        """
        device_count = nvmlDeviceGetCount()
        for i in range(device_count):
            handle = nvmlDeviceGetHandleByIndex(i)
            self.gpu_memory_free_bytes[str(i)] = nvmlDeviceGetMemoryInfo(handle).free


class SystemStateUpdateCoroutine:
    """
    Class encapsulating a system state loop

    :param state: The state to continually update
    :param interval_s: Time in seconds between each update
    """

    def __init__(self, state: SystemState, interval_s: float = 5) -> None:
        self.state = state
        self.interval_s = interval_s
        self.__stop_signal = asyncio.Event()

    async def run(self):
        """
        Runs the update loop asynchronously
        """
        self.__stop_signal.clear()
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
            # logger.debug(f"Free memory: {format_bytes(self.state.memory_free_bytes)}")
            used_mem_bytes = psutil.Process(os.getpid()).memory_info().rss
            logger.debug(f"Used memory; {format_bytes(used_mem_bytes)}")

    def stop(self):
        """
        Stop the current loop
        """
        self.__stop_signal.set()
