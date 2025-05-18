# app/database.py

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from fastapi import Request
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise ValueError("MONGO_URI is not set in the environment variables.")

# Explicitly specify the database name here:
DB_NAME = os.getenv("MONGO_DB_NAME", "notifications_db")

# Create the MongoDB client
client = AsyncIOMotorClient(MONGO_URI)

# Explicitly get the database by name to avoid ConfigurationError
db = client[DB_NAME]

# Dependency to use in FastAPI
def get_mongo_db() -> AsyncIOMotorDatabase:
    return db
