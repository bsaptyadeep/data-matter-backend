from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient
from decouple import config

# Database connection details (store these in environment variables for security)
DATABASE_URI = config("DATABASE_URI")

DATABASE_NAME = "artificial_intelligent"
ASSISTANT_COLLECTION_NAME = "ASSISTANT"
USER_COLLECTION_NAME = "USER"
ACCESS_TOKEN_COLLECTION_NAME="ACCESS_TOKEN"

# Connect to MongoDB
client = AsyncIOMotorClient(DATABASE_URI)
db = client[DATABASE_NAME]
assistant_collection = db[ASSISTANT_COLLECTION_NAME]
user_collection=db[USER_COLLECTION_NAME]
access_token_collection=db[ACCESS_TOKEN_COLLECTION_NAME]


# Function to get the database collection (optional, for reusability)
def get_assistant_collection():
    return assistant_collection

def get_user_collection():
    return user_collection

def get_access_token_collection():
    return access_token_collection
