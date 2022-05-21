import sys

sys.path.append(".")
import time

from taskflow import require, TaskResourceUsage


with require(TaskResourceUsage(memory_bytes=100 * (2**20))):
    print("Enter")
    time.sleep(1)
