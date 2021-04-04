import time
import humanfriendly as hf

from typing import Optional
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
    units = ["B", "K", "M", "G", "T"]
    index = 0
    for i in range(len(units) - 1):
        if b < 1024:
            break
        b = b / 1024
        index = i + 1

    return f"{b:.2f}{units[index]}"


def convert_byte_any(b) -> Optional[int]:
    if b is None or isinstance(b, int):
        return b

    if isinstance(b, str):
        return hf.parse_size(b, binary=True)

    raise ValueError("Cannot covert to bytes value")
