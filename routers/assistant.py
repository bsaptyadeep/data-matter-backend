from fastapi import APIRouter, Body, HTTPException, Query, Depends
from models.assistant import Assistant
from models.update_assistant import UpdateAssistant
from pymongo.results import InsertOneResult
from database import get_assistant_collection
import psycopg2
from bson.objectid import ObjectId
from routers.user import authenticate_user

router = APIRouter(prefix="/assistant", tags=["assistant"])

@router.get("/")
async def get_assistants(token: str = Depends(authenticate_user)):
    user_id = ObjectId(token)
    assistant_collection = get_assistant_collection()
    cursor = assistant_collection.find({"create_by_id": user_id})
    assistants = await cursor.to_list(length=100)
    assistant_list = []
    for assistant in assistants:
        assistant["_id"] = str(assistant["_id"])
        assistant["create_by_id"] = str(assistant["create_by_id"])
        assistant_list.append(assistant)
    return {
        "assistant": assistant_list
    }

@router.post("/")
async def create_assistant(assistant: dict = Body(...), user_id: str = Depends(authenticate_user)):
    try:
        conn = psycopg2.connect(assistant["connection_string"])
        cur = conn.cursor()
        cur.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public';  -- Modify if needed
        """)
        tables = [row[0] for row in cur.fetchall()]
        if len(tables) == 0:
            return {
                "status": "error",
                "message": ""
            }
        # Logic to create a new assistant
        assistant_collection = get_assistant_collection()
        assistant["create_by_id"]=ObjectId(user_id)
        inserted_result: InsertOneResult = assistant_collection.insert_one(assistant)
        inserted_result = await inserted_result

        # Check for successful insertion
        if not inserted_result.inserted_id:
            raise HTTPException(status_code=400, detail="Failed to create assistant")

        # Return the inserted assistant ID with a 201 Created status code
        return {
            "message": "Assistant created successfully",
            "id": str(inserted_result.inserted_id)  # Convert to string for JSON compatibility
        }
    except Exception as e:
        # Catch unexpected errors
        print(f"Error: {e}")
        raise HTTPException(status_code=400, detail=f"Error: {e}")

@router.put("/")
async def update_assistant(req_body: UpdateAssistant = Body(...), token: str = Depends(authenticate_user)):
    update_assistant = {}
    update_filter = {"_id": ObjectId(req_body.id)}
    if req_body.tables:
        update_assistant["tables"] = req_body.tables
    update = {"$set": update_assistant}  # Update operation with $set
    assistant_collection = get_assistant_collection()
    updated_product = await assistant_collection.find_one_and_update(update_filter, update)
    if updated_product is None:
        return {"message": "Product not found"}
    updated_product["_id"] = str(updated_product["_id"])
    updated_product["create_by_id"] = str(updated_product["create_by_id"])
    return {"message": "Product updated successfully", "product": updated_product}

@router.get("/table")
async def get_tables(id: str = Query(..., description="Assistant AI id")):
    tables = []
    try:
        object_id = ObjectId(id)
        assistant_collection = get_assistant_collection()
        assistant = await assistant_collection.find_one({ "_id": object_id })
        conn_string = assistant["connection_string"]
        conn = psycopg2.connect(conn_string)
        cur = conn.cursor()

        cur.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public';  -- Modify if needed
        """)

        tables = [row[0] for row in cur.fetchall()]
        if conn:
            conn.close()
    except Exception as e:
        raise Exception(f"Error retrieving tables: {str(e)}")  # Raise specific error message

    return {"tables": tables}