import yaml

from pydantic import BaseModel


class TaskflowSettings(BaseModel):
    task_retention_days: int = 30
    api_host: str = "localhost"
    api_port: int = 4305
    reserved_memory_bytes: int = 100 * (1024**2)  # 100MB
    reserved_gpu_memory_bytes: int = 1 * (1024**2)  # 1MB
    system_query_interval: float = 5

    @classmethod
    def from_yaml(cls, f) -> 'TaskflowSettings':
        d = yaml.full_load(f)
        return cls.parse_obj(d)
