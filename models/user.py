from pydantic import BaseModel

class User(BaseModel):
    name: str
    email_id: str
    image_url: str
    client_id: str
