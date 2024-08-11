from pydantic import BaseModel, Field
from bson.objectid import ObjectId
from typing import List, Optional

class Assistant(BaseModel):
    create_by_id: Optional[ObjectId] = Field(default_factory=ObjectId, alias="_id")
    name: str
    default_model: str
    description: str
    connection_string: str
    database_type: str
    tables: List[str] = []

    model_config = {
        "arbitrary_types_allowed": True
    }

