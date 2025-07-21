from pydantic import BaseModel

class UserStats(BaseModel):
    user_id: int
    n_games: int
    n_games_judge: int
    n_games_part: int
    score_part: int
    score_judge: int
    won_part: int
    won_judge: int
    lost_part: int
    lost_judge: int