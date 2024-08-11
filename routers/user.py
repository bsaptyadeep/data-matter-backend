from fastapi import APIRouter, Body, HTTPException, Depends, status
from models.user import User # Import the User model
from pymongo.results import InsertOneResult
from database import get_user_collection, get_access_token_collection
import psycopg2
from bson.objectid import ObjectId
from pydantic import BaseModel
import jwt
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

router = APIRouter(prefix="/user", tags=["user"])

ALGORITHM = "HS256"
JWT_SECRET_KEY = "your_secret_key"

def create_access_token(user_id: str):
    payload = {"user_id": user_id}
    encoded_jwt = jwt.encode(payload, JWT_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def authenticate_user(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    if credentials.scheme != "Bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization scheme")
    access_token_collection = get_access_token_collection()
    existing_access_token = await access_token_collection.find_one({"access_token": credentials.credentials})
    if existing_access_token == None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token")
    return existing_access_token["user_id"]

@router.post("/")
async def create_assistant(user: User = Body(...)):
    try:
        user_collection = get_user_collection()
        duplicate_user = await user_collection.find_one({ "email_id": user.email_id})
        if duplicate_user:
            return {
            "message": "User already exist",
            "already_exist": True
        }
        inserted_result: InsertOneResult = user_collection.insert_one(user.dict())
        inserted_result = await inserted_result

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
        if existing_access_token:
            return {
                "access_token": existing_access_token["access_token"],
                "existing_session": True
            }
        user_id_str = str(valid_user["_id"])
        access_token = create_access_token(user_id=user_id_str)
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

@router.get("/protected")
async def protected_route(token: str = Depends(authenticate_user)):
    # Access token is valid, proceed with protected operations
    return {"message": "Access granted"}