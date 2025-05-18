from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from bson.errors import InvalidId
from app.database import get_mongo_db
from app import schemas, rabbitmq
from app.utils import is_valid_notification_type
import asyncio

router = APIRouter()

# Background task to simulate delivery
async def simulate_delivery_and_mark_sent(db: AsyncIOMotorDatabase, notification_id: str):
    await asyncio.sleep(1)  # Simulate sending delay
    await db.notifications.update_one(
        {"_id": ObjectId(notification_id)},
        {"$set": {"status": "sent"}}
    )

# Send notification
@router.post("/notifications", response_model=schemas.NotificationResponse)
async def send_notification(
    notification: schemas.NotificationCreate,
    db: AsyncIOMotorDatabase = Depends(get_mongo_db)
):
    if not is_valid_notification_type(notification.type):
        raise HTTPException(status_code=400, detail="Invalid notification type")

    doc = {**notification.dict(), "status": "pending"}
    result = await db.notifications.insert_one(doc)
    doc["_id"] = result.inserted_id

    await rabbitmq.publish_notification({"id": str(result.inserted_id)})
    asyncio.create_task(simulate_delivery_and_mark_sent(db, str(result.inserted_id)))

    return schemas.NotificationResponse(
        id=str(doc["_id"]),
        user_id=doc["user_id"],
        type=doc["type"],
        message=doc["message"],
        status=doc["status"]
    )

# Get notifications for a user
@router.get("/users/{user_id}/notifications", response_model=list[schemas.NotificationResponse])
async def get_user_notifications(user_id: int, db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    cursor = db.notifications.find({"user_id": user_id})
    results = await cursor.to_list(length=100)
    return [
        schemas.NotificationResponse(
            id=str(doc["_id"]),
            user_id=doc["user_id"],
            type=doc["type"],
            message=doc["message"],
            status=doc["status"]
        ) for doc in results
    ]

# Delete a notification
@router.delete("/notifications/{notification_id}")
async def delete_notification(notification_id: str, db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    try:
        obj_id = ObjectId(notification_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid notification ID")

    result = await db.notifications.delete_one({"_id": obj_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Notification not found")

    return {"detail": "Notification deleted successfully"}
