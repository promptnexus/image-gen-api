from pydantic import BaseModel


class ComputeUsage(BaseModel):
    compute_time_ms: int  # milliseconds for precision
    image_size: str
    instance_type: str = "g4dn.xlarge"
