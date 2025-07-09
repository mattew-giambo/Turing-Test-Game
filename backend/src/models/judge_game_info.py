from pydantic import BaseModel
from datetime import datetime

class JudgeGameInfo(BaseModel):
    player_name: str
    game_date: datetime