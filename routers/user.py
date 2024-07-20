from fastapi import APIRouter, Body, HTTPException, Query
from models.user import User # Import the User model
from pymongo.results import InsertOneResult
from database import get_user_collection, get_access_token_collection
import psycopg2
from bson.objectid import ObjectId
from pydantic import BaseModel
import jwt

router = APIRouter(prefix="/user", tags=["user"])

ALGORITHM = "HS256"
JWT_SECRET_KEY = "your_secret_key"

def create_access_token(user_id: str):
    payload = {"user_id": user_id}
    encoded_jwt = jwt.encode(payload, JWT_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@router.post("/")
async def create_assistant(user: User = Body(...)):
    try:
        user_collection = get_user_collection()
        duplicate_user = await user_collection.find_one({ "email_id": user.email_id})
        print("duplicate_user", duplicate_user)
        if duplicate_user:
            return {
            "message": "User already exist",
            "already_exist": True
        }
        inserted_result: InsertOneResult = user_collection.insert_one(user.dict())
        inserted_result = await inserted_result
        print("user_inserted", inserted_result)

        # Check for successful insertion
        if not inserted_result.inserted_id:
            raise HTTPException(status_code=400, detail="Failed to create assistant")

        # Return the inserted user ID with a 201 Created status code
        return {
            "message": "User created successfully",
            "id": str(inserted_result.inserted_id)  # Convert to string for JSON compatibility
        }
    except Exception as e:
        # Catch unexpected errors
        print(f"Error: {e}")
        raise HTTPException(status_code=400, detail=f"Error: {e}")

@router.post("/login")
async def loginUser(user: User = Body(...)):
    try:
        user_collection = get_user_collection()
        valid_user = await user_collection.find_one({ "email_id": user.email_id})
        if valid_user == None:
            return {
                "message": "User Not Found",
            }
        access_token_collection = get_access_token_collection()
        existing_access_token = await access_token_collection.find_one({"user_id": valid_user["_id"]})
        print("existing_access_token", existing_access_token)
        if existing_access_token:
            return {
                "access_token": existing_access_token["access_token"],
                "existing_session": True
            }
        user_id_str = str(valid_user["_id"])
        print("testing_user_id", user_id_str)
        access_token = create_access_token(user_id=user_id_str)
        print("access_token", access_token)
        inserted_access_token_result = await access_token_collection.insert_one({
            "user_id": valid_user["_id"],
            "access_token": access_token
        })
        inserted_id = inserted_access_token_result.inserted_id
        access_token = await access_token_collection.find_one({"_id": inserted_id})
        return {
                "access_token": access_token["access_token"],
                "existing_session": False
            }
    except Exception as e:
        # Catch unexpected errors
        print(f"Error: {e}")
        raise HTTPException(status_code=400, detail=f"Error: {e}")
