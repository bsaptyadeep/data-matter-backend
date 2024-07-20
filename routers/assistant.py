from fastapi import APIRouter, Body, HTTPException, Query
from models.assistant import Assistant
from models.update_assistant import UpdateAssistant
from pymongo.results import InsertOneResult
from database import get_assistant_collection
import psycopg2
from bson.objectid import ObjectId

router = APIRouter(prefix="/assistant", tags=["assistant"])

@router.get("/")
async def get_assistants():
    assistant_collection = get_assistant_collection()
    cursor = assistant_collection.find()
    assistants = await cursor.to_list(length=100)
    assistant_list = []
    for assistant in assistants:
        assistant["_id"] = str(assistant["_id"])
        assistant_list.append(assistant)
    return {
        "assistant": assistant_list
    }

@router.post("/")
async def create_assistant(assistant: Assistant = Body(...)):
    try:
        conn = psycopg2.connect(assistant.connection_string)
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
        inserted_result: InsertOneResult = assistant_collection.insert_one(assistant.dict())
        inserted_result = await inserted_result
        print("assistant_inserted", inserted_result)

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
async def update_assistant(req_body: UpdateAssistant = Body(...)):
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