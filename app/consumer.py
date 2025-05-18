# app/consumer.py

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
db_name = mongo_client.get_default_database().name if mongo_client.get_default_database() is not None else "notifications_db"
db = mongo_client[db_name]

async def consume_notifications():
    connection = await aio_pika.connect_robust(RABBITMQ_URL)
    async with connection:
        channel = await connection.channel()
        queue = await channel.declare_queue("notifications", durable=True)

        print("[*] Waiting for messages. To exit press CTRL+C")

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    max_processing_attempts = 3  # Retry whole message block up to 3 times
                    for attempt in range(1, max_processing_attempts + 1):
                        try:
                            payload = json.loads(message.body.decode())
                            notification_id = payload.get("id")

                            if not notification_id:
                                print("[Error] Missing 'id' in message payload.")
                                break

                            print(f"[Queue] Received notification ID: {notification_id}")

                            # Retry fetching the document if it's not yet available
                            max_doc_retries = 5
                            doc = None
                            for doc_attempt in range(1, max_doc_retries + 1):
                                doc = await db.notifications.find_one({"_id": ObjectId(notification_id)})
                                if doc:
                                    break
                                print(f"[Retry {doc_attempt}] Notification not found yet. Retrying...")
                                await asyncio.sleep(1.0)

                            if not doc:
                                print(f"[Error] Notification ID {notification_id} not found after {max_doc_retries} retries.")
                                break

                            # Simulate sending the notification
                            print(f"[>>] Sending notification to user {doc['user_id']} with message: {doc['message']}")

                            # Update status to 'sent'
                            await db.notifications.update_one(
                                {"_id": ObjectId(notification_id)},
                                {"$set": {"status": "sent"}}
                            )
                            print(f"[✓] Notification {notification_id} marked as sent.")
                            break  # Success: exit retry loop

                        except Exception as e:
                            print(f"[Attempt {attempt}] Error processing message: {e}")
                            if attempt == max_processing_attempts:
                                print("[Error] Max retries reached for message. Skipping.")
                            else:
                                backoff = 2 ** attempt
                                print(f"[Retrying in {backoff}s]")
                                await asyncio.sleep(backoff)

if __name__ == "__main__":
    asyncio.run(consume_notifications())
