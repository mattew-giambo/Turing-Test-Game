from pydantic import BaseModel

class UserInfo(BaseModel):
    id: int
    user_name: str
    email: str