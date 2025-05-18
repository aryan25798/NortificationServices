# app/notifier.py

import os
import ast
import asyncio
import aio_pika
from datetime import datetime
from app.database import get_mongo_db
from app.models import NotificationInDB

MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds between retries

async def process_notifications():
    connection = await aio_pika.connect_robust(os.getenv("RABBITMQ_URL"))
    async with connection:
        channel = await connection.channel()
        queue = await channel.declare_queue("notifications", durable=True)

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    try:
                        data = ast.literal_eval(message.body.decode())
                        success = await handle_notification(data)

                        if not success:
                            retries = data.get("retries", 0)
                            if retries < MAX_RETRIES:
                                data["retries"] = retries + 1
                                await asyncio.sleep(RETRY_DELAY)
                                await channel.default_exchange.publish(
                                    aio_pika.Message(
                                        body=str(data).encode(),
                                        delivery_mode=aio_pika.DeliveryMode.PERSISTENT
                                    ),
                                    routing_key="notifications"
                                )
                                print(f"[Retry {data['retries']}] Requeued message for notification ID {data['id']}")
                            else:
                                print(f"[Dropped] Max retries reached for notification ID {data['id']}")
                    except Exception as e:
                        print(f"[Error] Failed to process message: {e}")


async def handle_notification(data):
    db = get_mongo_db()
    notifications_collection = db.notifications

    try:
        notification = await notifications_collection.find_one({"_id": data["id"]})
        if not notification:
            print(f"[Error] Notification ID {data['id']} not found.")
            return False

        # Simulate sending notification
        print(f"[Sending] {notification['type']} to user {notification['user_id']}: {notification['message']}")

        await notifications_collection.update_one(
            {"_id": data["id"]},
            {
                "$set": {
                    "status": "sent",
                    "updated_at": datetime.utcnow()
                }
            }
        )
        return True

    except Exception as e:
        print(f"[Failure] Error sending notification ID {data['id']}: {e}")
        await notifications_collection.update_one(
            {"_id": data["id"]},
            {
                "$set": {
                    "status": "failed",
                    "updated_at": datetime.utcnow()
                }
            }
        )
        return False
