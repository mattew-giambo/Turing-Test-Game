from pydantic import BaseModel
from typing import List
from datetime import date

class Game(BaseModel):
    game_id: int
    player_role: str
    data: date
    terminated: bool
    
class UserGames(BaseModel):
    user_id: int
    user_games: List[Game]