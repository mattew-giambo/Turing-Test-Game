from pydantic import BaseModel
from typing import Literal
from datetime import date

class GameInfoInput(BaseModel):
    player_id: int
    game_id: int

class GameInfoOutput(BaseModel):
    game_id: int
    data: date 
    terminated: bool 
    player_id: int 
    player_role: Literal["judge", "participant"]