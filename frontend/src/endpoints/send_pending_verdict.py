from fastapi import Request, HTTPException
from fastapi.templating import Jinja2Templates
import requests
from models.judge_game import JudgeGameAnswer
from models.pending_game import JudgeGameAnswer, EndPendingGame
from config.constants import API_BASE_URL
from typing import *
from urllib.parse import urljoin

def send_pending_verdict(game_id: int, request: Request, payload: JudgeGameAnswer, templates: Jinja2Templates):
    try:
        response = requests.post(urljoin(API_BASE_URL, f"/end-pending-game-api/{game_id}"), json=payload.model_dump())
        response.raise_for_status()
        result = EndPendingGame.model_validate(response.json())

    except requests.RequestException as e:
        try:
            detail = e.response.json().get("detail", "Errore nella richiesta")
        except Exception:
            detail = str(e)
        if e.response and e.response.status_code == 404:
            return templates.TemplateResponse("game_not_found.html", {"request": request})
        raise HTTPException(status_code=e.response.status_code if e.response else 500, detail=detail)

    return result