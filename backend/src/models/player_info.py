from pydantic import BaseModel
from typing import Literal

class PlayerInfo(BaseModel):
    player_id: int
    player_role: Literal['judge', 'participant']