from pydantic import BaseModel

class SendBody(BaseModel):
    message: str
