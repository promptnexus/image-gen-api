from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ComputeUsage(BaseModel):
    customer_id: str
    subscription_item_id: str
    milliseconds: int
    timestamp: Optional[datetime] = None
