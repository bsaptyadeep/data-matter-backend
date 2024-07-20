from pydantic import BaseModel
from typing import List, Optional

class UpdateAssistant(BaseModel):
    id: str
    name: Optional[str] = None
    default_model: Optional[str] = None
    description: Optional[str] = None
    connection_string: Optional[str] = None
    database_type: Optional[str] = None
    tables: Optional[List[str]] = None

