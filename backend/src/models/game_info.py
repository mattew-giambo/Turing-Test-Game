from pydantic import BaseModel
from datetime import datetime

class GameInfo(BaseModel):
    player_name: str
    player_role: str
    game_date: datetime