from fastapi import Request
from fastapi.templating import Jinja2Templates
from models.user_stats import UserStats
from models.user_games import UserGames
from models.user_info import UserInfo
from typing import *

from utility.get_user_stats import get_user_stats
from utility.get_user_info import get_user_info
from utility.get_user_games import get_user_games

def get_profilo(user_id: int, request: Request, templates: Jinja2Templates, sessioni_attive: Dict[int, Dict[str, str]]):
    if user_id not in sessioni_attive.keys():
        return templates.TemplateResponse(
            "login.html", {"request": request}
        )
    user_info: UserInfo = get_user_info(user_id)
    user_stats: UserStats = get_user_stats(user_id)
    user_games: UserGames = get_user_games(user_id)

    return templates.TemplateResponse(
        "profilo.html",{
            "username": user_info.user_name,
            "email": user_info.email,
            "n_games": user_stats.n_games,
            "n_games_judge": user_stats.n_games_judge,
            "n_games_part": user_stats.n_games_part,
            "score_part": user_stats.score_part,
            "score_judge": user_stats.score_judge,
            "won_part": user_stats.won_part,
            "won_judge": user_stats.won_judge,
            "lost_part": user_stats.lost_part,
            "lost_judge": user_stats.lost_judge,
            "user_games": user_games.user_games
        }
    )