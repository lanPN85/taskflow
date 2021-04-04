import yaml

from pydantic import BaseModel, validator

from taskflow.utils import convert_byte_any


class TaskflowSettings(BaseModel):
    task_retention_days: int = 30
    api_host: str = "localhost"
    api_port: int = 4305
    reserved_memory_bytes: int = 100 * (1024**2)  # 100MB
    reserved_gpu_memory_bytes: int = 1 * (1024**2)  # 1MB
    system_query_interval: float = 2

    @classmethod
    def from_yaml(cls, f) -> 'TaskflowSettings':
        d = yaml.full_load(f)
        return cls.parse_obj(d)

    @validator("reserved_memory_bytes", "reserved_gpu_memory_bytes", pre=True, always=True)
    def convert_byte_value(cls, v):
        return convert_byte_any(v)
