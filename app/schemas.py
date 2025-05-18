# app/schemas.py

from pydantic import BaseModel, Field
from typing import Literal
from datetime import datetime

class NotificationCreate(BaseModel):
    user_id: int
    type: Literal["email", "sms", "in-app"]
    message: str

class NotificationResponse(BaseModel):
    id: str = Field(..., alias="_id")  # maps MongoDB's _id to "id"
    user_id: int
    type: Literal["email", "sms", "in-app"]
    message: str
    status: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {
        "populate_by_name": True,  # allows using 'id' instead of '_id'
        "from_attributes": True
    }
