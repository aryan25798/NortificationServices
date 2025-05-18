from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime

class NotificationCreate(BaseModel):
    id: str  # custom frontend id sent on creation
    user_id: int
    type: Literal["email", "sms", "in-app"]
    message: str

class NotificationResponse(BaseModel):
    id: str  # will hold custom_id from DB, not Mongo _id
    user_id: int
    type: Literal["email", "sms", "in-app"]
    message: str
    status: str
    created_at: Optional[datetime] = None  # Optional because it may not be always returned

    class Config:
        allow_population_by_field_name = True
        orm_mode = True
