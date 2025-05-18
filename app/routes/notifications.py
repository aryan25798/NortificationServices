from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from bson.errors import InvalidId
from app.database import get_mongo_db
from app import schemas, rabbitmq
from app.utils import is_valid_notification_type
import asyncio

router = APIRouter()

# Background task to simulate delivery
async def simulate_delivery_and_mark_sent(db: AsyncIOMotorDatabase, mongo_id: str):
    await asyncio.sleep(1)
    await db.notifications.update_one(
        {"_id": ObjectId(mongo_id)},
        {"$set": {"status": "sent"}}
    )

# Send notification
@router.post("/notifications", response_model=schemas.NotificationResponse)
async def send_notification(
    notification: schemas.NotificationCreate,
    background_tasks: BackgroundTasks,
    db: AsyncIOMotorDatabase = Depends(get_mongo_db)
):
    if not is_valid_notification_type(notification.type):
        raise HTTPException(status_code=400, detail="Invalid notification type")

    # Extract frontend ID from request, store as custom_id in Mongo
    doc = notification.dict()
    frontend_id = doc.pop("id")  # remove 'id' and keep separately
    doc["custom_id"] = frontend_id
    doc["status"] = "pending"

    result = await db.notifications.insert_one(doc)

    # Publish using frontend id
    await rabbitmq.publish_notification({"id": frontend_id})

    # Run background task using Mongo internal _id
    background_tasks.add_task(simulate_delivery_and_mark_sent, db, str(result.inserted_id))

    return schemas.NotificationResponse(
        id=frontend_id,
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
            id=doc.get("custom_id", str(doc["_id"])),
            user_id=doc["user_id"],
            type=doc["type"],
            message=doc["message"],
            status=doc["status"]
        ) for doc in results
    ]

# Delete a notification with validation by MongoDB internal _id
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
