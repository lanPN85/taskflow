import time
import humanfriendly as hf

from typing import Optional
from py3nvml.py3nvml import NVMLError, nvmlInit
from datetime import timedelta


def get_timestamp_ms() -> int:
    """
    Get the current timestamp in milliseconds

    :rtype: int
    """
    return int(time.time() * 1000)


def check_has_nvml() -> bool:
    """
    Determines if libnvml is available on the system.
    True means CUDA is available

    :rtype: bool
    """
    try:
        nvmlInit()
        return True
    except NVMLError:
        return False


def format_bytes(b: float) -> str:
    """
    Formats an amount of bytes into a string containing the value in the highest possible unit

    :param b: Number of bytes to convert
    :type b: float
    :return: Formatted string
    :rtype: str
    """
    units = ["B", "K", "M", "G", "T"]
    index = 0
    for i in range(len(units) - 1):
        if b < 1024:
            break
        b = b / 1024
        index = i + 1

    return f"{b:.2f}{units[index]}"


def convert_byte_any(b) -> Optional[int]:
    """
    Converts a byte value into its integer value

    :param b: A number of bytes, or a formatted string containing a byte value and unit
    :raises ValueError: If the type is not int, float or str
    :rtype: Optional[int]
    """
    if b is None or isinstance(b, int):
        return b

    if isinstance(b, float):
        return int(b)

    if isinstance(b, str):
        return hf.parse_size(b, binary=True)

    raise ValueError("Cannot covert to bytes value")


def format_timedelta(t: timedelta) -> str:
    """
    Formats a timedelta object into HH:MM:SS

    :type t: timedelta
    :return: Formatted string
    :rtype: str
    """
    total = t.total_seconds()

    hours = int(total / 3600)
    rem = total % 3600
    mins = int(rem / 60)
    secs = int(rem % 60)

    return f"{hours:02d}:{mins:02d}:{secs:02d}"
