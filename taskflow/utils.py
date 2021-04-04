import time

from py3nvml.py3nvml import NVMLError, nvmlInit


def get_timestamp_ms():
    return int(time.time() * 1000)


def check_has_nvml() -> bool:
    try:
        nvmlInit()
        return True
    except NVMLError:
        return False


def format_bytes(b: float) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]
    index = 0
    for i in range(len(units) - 1):
        if b < 1024:
            break
        b = b / 1024
        index = i + 1

    return f"{b:.2f}{units[index]}"
