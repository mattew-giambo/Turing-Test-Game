from fastapi import Request, HTTPException
from fastapi.templating import Jinja2Templates
import requests
from models.judge_game import JudgeGameAnswer, EndJudgeGameOutput
from models.pending_game import JudgeGameAnswer
from config.constants import API_BASE_URL
from typing import Dict
from urllib.parse import urljoin

def send_judge_answer(game_id: int, request: Request, payload: JudgeGameAnswer):
    try:
        response = requests.post(urljoin(API_BASE_URL, f"/judge-game-api/{game_id}"), json= payload.model_dump())
        response.raise_for_status()
    except requests.RequestException as e:
        error_data: Dict =  e.response.json()
        raise HTTPException(
            status_code= error_data.get("status_code", 500),
            detail= error_data.get("detail", "Errore sconosciuto")
        )
        
    return EndJudgeGameOutput.model_validate(response.json())