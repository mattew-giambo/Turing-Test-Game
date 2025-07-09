from pydantic import BaseModel
from typing import Literal

class ConfirmGame(BaseModel):
    game_id: int
    player_id: int