from pydantic import BaseModel

class DisconnectResponse(BaseModel):
    message: str