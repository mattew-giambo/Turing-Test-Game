from fastapi import Request, HTTPException
from fastapi.templating import Jinja2Templates
import requests
from models.user_stats import UserStats
from config.constants import API_BASE_URL
from typing import *
from urllib.parse import urljoin

def get_user_stats(user_id: int, request: Request, templates: Jinja2Templates):
    try:
        response = requests.get(urljoin(API_BASE_URL, f"/user-stats-api/{user_id}"))
        response.raise_for_status()
    except requests.RequestException as e:
        error_data: Dict = e.response.json()
        if error_data.status_code == 404:
            return templates.TemplateResponse(
            "game_not_found.html", {
                "request": request
            }
        )
        else:
            raise HTTPException(
                status_code= error_data.get("status_code", 500),
                detail= error_data.get("detail", "Errore sconosciuto")
            )
        
    response_data = UserStats.model_validate(response.json())

    return templates.TemplateResponse(
        "user_stats.html", {
            "request": request,
            "user_id": response_data.user_id,
            "n_games": response_data.n_games,
            "score_part": response_data.score_part,
            "score_judge": response_data.score_judge,
            "won_part": response_data.won_part,
            "won_judge": response_data.won_judge,
            "lost_part": response_data.lost_part,
            "lost_judge": response_data.lost_judge
        })