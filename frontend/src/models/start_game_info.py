from pydantic import BaseModel
from typing import Literal

class StartGameInfo(BaseModel):
    player_id: int
    player_role: Literal['judge', 'participant']
    mode: Literal["classic", "verdict"]