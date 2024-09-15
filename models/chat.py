from pydantic import BaseModel, Field
from bson.objectid import ObjectId
from typing import Optional

class Chat(BaseModel):
    user: str
    bot: str
    sql_query: Optional[str]