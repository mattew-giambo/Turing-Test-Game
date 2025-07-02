from pydantic import BaseModel
from typing import Literal

class UserInfo(BaseModel):
    user_name: str
    user_role: Literal["judge", "partecipant"]