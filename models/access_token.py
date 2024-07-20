from pydantic import BaseModel, Field
from bson.objectid import ObjectId

class AccessToken(BaseModel):
    user_id: ObjectId = Field(default_factory=ObjectId, alias="_id")
    access_token: str