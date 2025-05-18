import asyncio
import aio_pika
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import os
import json
from dotenv import load_dotenv

load_dotenv()

RABBITMQ_URL = os.getenv("RABBITMQ_URL")
MONGO_URI = os.getenv("MONGO_URI")

if not RABBITMQ_URL:
    raise ValueError("RABBITMQ_URL is not set in environment variables.")
if not MONGO_URI:
    raise ValueError("MONGO_URI is not set in environment variables.")

# Connect to MongoDB
mongo_client = AsyncIOMotorClient(MONGO_URI)
# Fallback: use 'notifications_db' if no default DB name is provided in URI
db_name = mongo_client.get_default_database().name if mongo_client.get_default_database() is not None else "notifications_db"
db = mongo_client[db_name]

MAX_SEND_RETRIES = 3
RETRY_DELAY_SECONDS = 2

async def consume_notifications():
    connection = await aio_pika.connect_robust(RABBITMQ_URL)
    async with connection:
        channel = await connection.channel()
        queue = await channel.declare_queue("notifications", durable=True)

        print("[*] Waiting for messages. To exit press CTRL+C")

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    try:
                        payload = json.loads(message.body.decode())
                        notification_id = payload.get("id")

                        if not notification_id:
                            print("[Error] Missing 'id' in message payload.")
                            continue

                        print(f"[Queue] Received notification ID: {notification_id}")

                        # Retry fetching the document in case it's not yet available
                        max_retries = 5
                        doc = None
                        for attempt in range(max_retries):
                            doc = await db.notifications.find_one({"_id": ObjectId(notification_id)})
                            if doc:
                                break
                            await asyncio.sleep(1.0)  # Wait before retry

                        if not doc:
                            print(f"[Error] Notification ID {notification_id} not found after retries.")
                            continue

                        # Attempt to send the notification with retries
                        send_success = False
                        for send_attempt in range(1, MAX_SEND_RETRIES + 1):
                            try:
                                # Simulate sending (replace with real send logic)
                                print(f"[>>] Sending notification to user {doc['user_id']} with message: {doc['message']}")

                                # Here you can put actual send code, e.g., email, SMS, push, etc.
                                # await send_notification_function(doc)

                                send_success = True
                                break  # Exit retry loop if successful

                            except Exception as send_err:
                                print(f"[Error] Send attempt {send_attempt} failed: {send_err}")
                                if send_attempt < MAX_SEND_RETRIES:
                                    print(f"Retrying in {RETRY_DELAY_SECONDS} seconds...")
                                    await asyncio.sleep(RETRY_DELAY_SECONDS)

                        # Update status based on send outcome
                        if send_success:
                            await db.notifications.update_one(
                                {"_id": ObjectId(notification_id)},
                                {"$set": {"status": "sent"}}
                            )
                            print(f"[✓] Notification {notification_id} marked as sent.")
                        else:
                            await db.notifications.update_one(
                                {"_id": ObjectId(notification_id)},
                                {"$set": {"status": "failed"}}
                            )
                            print(f"[✗] Notification {notification_id} marked as failed after retries.")

                    except Exception as e:
                        print(f"[Error] Failed to process message: {e}")

if __name__ == "__main__":
    asyncio.run(consume_notifications())
