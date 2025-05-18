from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime

class NotificationCreate(BaseModel):
    user_id: int
    type: Literal["email", "sms", "in-app"]
    message: str

class NotificationResponse(BaseModel):
    id: str  # This maps to MongoDB's _id, returned as string
    user_id: int
    type: Literal["email", "sms", "in-app"]
    message: str
    status: str
    created_at: Optional[datetime] = None

    class Config:
        allow_population_by_field_name = True
        orm_mode = True
