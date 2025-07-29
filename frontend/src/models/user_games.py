from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class Game(BaseModel):
    game_id: int
    player_role: str
    data: date
    is_terminated: bool
    is_won: Optional[bool]
    points: int
    
class UserGames(BaseModel):
    user_id: int
    user_games: List[Game]