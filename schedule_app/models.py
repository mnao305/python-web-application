from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Schedule(BaseModel):
    id: Optional[int]
    title: str
    body: str
    begin_at: datetime
    end_at: datetime
    createdAt: Optional[datetime]
    updatedAt: Optional[datetime]
