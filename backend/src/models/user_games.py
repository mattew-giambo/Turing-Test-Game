from pydantic import BaseModel
from typing import List

class Game(BaseModel):
    game_id: int
    player_role: str

class UserGames(BaseModel):
    user_id: int
    user_games: List[Game]