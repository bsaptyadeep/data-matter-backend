from fastapi import APIRouter, Body, HTTPException, Depends, status, Query
from models.user import User # Import the User model
from pymongo.results import InsertOneResult
from database import get_user_collection, get_assistant_collection, get_chat_history_collection
import psycopg2
from bson.objectid import ObjectId
from pydantic import BaseModel
import jwt
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from routers.user import authenticate_user
from sqlalchemy import (create_engine)
from llama_index.core import SQLDatabase
from llama_index.llms.openai import OpenAI
from llama_index.core.indices.struct_store import (
    NLSQLTableQueryEngine,
)

router = APIRouter(prefix="/chat", tags=["chat"])

@router.get("/")
async def get_assistants(assistant_id: str = Query(..., description="Assistant AI id"), token: str = Depends(authenticate_user)):
    assistant_object_id = ObjectId(assistant_id)
    chat_history_collection = get_chat_history_collection()
    chat_history = await chat_history_collection.find_one({ "assistant_id": assistant_object_id })
    chat_history["_id"] = str(chat_history["_id"])
    chat_history["assistant_id"] = str(chat_history["assistant_id"])
    return {
        "chat_history": chat_history
    }

@router.post("/get-response")
async def respond_query(assistant_id: str = Query(..., description="assistant id"),
                  query: str = Query(..., description="user query")):
    assistant_collection = get_assistant_collection()
    assistant = await assistant_collection.find_one({ "_id": ObjectId(assistant_id) })
    if not assistant:
        return HTTPException(status_code=404, detail=f"assistant_id not found")
    chat_history_collection = get_chat_history_collection()
    chat_history = await chat_history_collection.find_one({ "assistant_id": assistant["_id"]})
    if not chat_history:
        return HTTPException(status_code=400, detail=f"chat history not initialized in DB")
    engine = create_engine(assistant["connection_string"])
    sql_database = SQLDatabase(engine, include_tables=assistant["tables"])
    llm = OpenAI(model="gpt-3.5-turbo")
    query_engine_openai = NLSQLTableQueryEngine(sql_database, tables=assistant["tables"], llm=llm)
    response = query_engine_openai.query(query)
    chat = {
        "user": query,
        "bot": response.response,
        "sql_query": response.metadata["sql_query"]
    }
    chat_history_push_result = await chat_history_collection.find_one_and_update(
            {"_id": chat_history["_id"]},
            {"$push": {"chats": chat}},
            return_document=True
        )
    if chat_history_push_result is None:
        print("testing~chat_history_push_result", chat_history_push_result.response)
        return HTTPException(status_code=400, detail=f"failed to push chat to chat_history")

    responseObj = {
        "user": query,
        "response": {
            "response": response.response,
            "sql_query": response.metadata["sql_query"],
            "result": response.metadata["result"]
        }
    }
    return { "chat_content": responseObj }