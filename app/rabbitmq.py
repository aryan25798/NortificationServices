# app/rabbitmq.py

import asyncio
import aio_pika
import os
import json
from dotenv import load_dotenv
from typing import Dict

load_dotenv()

RABBITMQ_URL = os.getenv("RABBITMQ_URL")

async def publish_notification(data: Dict):
    """
    Publishes a notification to the RabbitMQ 'notifications' queue.
    """
    try:
        # Establish a robust connection
        connection = await aio_pika.connect_robust(RABBITMQ_URL)
        async with connection:
            channel = await connection.channel()
            queue = await channel.declare_queue("notifications", durable=True)

            # Use JSON serialization for the message body
            message = aio_pika.Message(
                body=json.dumps(data).encode(),  # <-- JSON here
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT
            )

            await channel.default_exchange.publish(message, routing_key=queue.name)
            print(f"[Queue] Published notification ID {data.get('id')} to queue.")

    except Exception as e:
        print(f"[Error] Failed to publish message to queue: {e}")
