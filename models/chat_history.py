from pydantic import BaseModel, Field
from bson.objectid import ObjectId
from typing import List, Optional
from models import Chat

class ChatHistory(BaseModel):
    assistant_id: ObjectId
    chats: List[Chat] = []

    model_config = {
        "arbitrary_types_allowed": True
    }

