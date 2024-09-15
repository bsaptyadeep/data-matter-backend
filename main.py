from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from sqlalchemy import (create_engine)
from llama_index.core import SQLDatabase
from llama_index.llms.openai import OpenAI
from llama_index.core.indices.struct_store import (
    NLSQLTableQueryEngine,
    SQLTableRetrieverQueryEngine,
    NLStructStoreQueryEngine
)
from routers import assistant, user, chat
from database import get_assistant_collection
from bson.objectid import ObjectId
import os
from decouple import config


os.environ['OPENAI_API_KEY'] = config("OPENAI_API_KEY")

app = FastAPI()

# CORS - Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(assistant.router)
app.include_router(user.router)
app.include_router(chat.router)


@app.get("/testing")
def testing():
    return {"testing": True}

@app.post("/respond_query")
async def respond_query(assistant_id: str = Query(..., description="connection string"),
                  query: str = Query(..., description="user query")):
    assistant_collection = get_assistant_collection()
    assistant = await assistant_collection.find_one({ "_id": ObjectId(assistant_id) })
    engine = create_engine(assistant["connection_string"])
    sql_database = SQLDatabase(engine, include_tables=assistant["tables"])
    llm = OpenAI(model="gpt-3.5-turbo")
    query_engine_openai = NLSQLTableQueryEngine(sql_database, tables=assistant["tables"], llm=llm)
    response = query_engine_openai.query(query)
    print("testing~response", response)
    responseObj = {
        "user": query,
        "response": {
            "response": response.response,
            "sql_query": response.metadata["sql_query"],
            # "result": response.metadata["result"]
        }
    }
    return { "chat_content": responseObj }