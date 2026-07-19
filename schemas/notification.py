from pydantic import BaseModel
from typing import Optional
from database.models import NotificationChannel


class NotificationInput(BaseModel):
    customer_id: int
    channel: NotificationChannel
    subject: Optional[str] = None
    body: str
    order_id: Optional[int] = None


class NotificationPreferenceInput(BaseModel):
    customer_id: int
    channel: NotificationChannel
    is_enabled: bool
    channel_address: Optional[str] = None  # email ou telegram chat_id
