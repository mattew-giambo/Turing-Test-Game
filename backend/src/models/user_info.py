from pydantic import BaseModel
from typing import Literal

class UserInfo(BaseModel):
    player_name: str
    player_role: Literal['judge', 'participant']