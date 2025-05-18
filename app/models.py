# app/models.py

from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime

# Base fields shared across models
class NotificationBase(BaseModel):
    user_id: int
    type: Literal["email", "sms", "in-app"]
    message: str

# Model for creating a new notification
class NotificationCreate(NotificationBase):
    pass

# Internal model for database (MongoDB)
class NotificationInDB(NotificationBase):
    id: Optional[str] = Field(None, alias="_id")  # MongoDB's native ID
    status: str = "pending"
    created_at: datetime = Field(default_factory=datetime.utcnow)  # Auto set UTC time

# Model for returning data to clients
class NotificationResponse(NotificationInDB):
    id: str  # Ensure ID is exposed as string

    class Config:
        allow_population_by_field_name = True  # Maps _id to id
        orm_mode = True
