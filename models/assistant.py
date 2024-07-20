from pydantic import BaseModel
from typing import List

class Assistant(BaseModel):
    name: str
    default_model: str
    description: str
    connection_string: str
    database_type: str
    tables: List[str] = []

