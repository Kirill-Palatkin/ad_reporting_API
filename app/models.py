from pydantic import BaseModel, Field
from typing import List


class Event(BaseModel):
    date: str
    channel: str
    campaign_id: str
    impressions: int
    clicks: int
    cost: float


class EventList(BaseModel):
    events: List[Event]
