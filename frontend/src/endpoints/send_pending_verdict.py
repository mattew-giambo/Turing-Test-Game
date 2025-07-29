from fastapi import Request, HTTPException
from fastapi.templating import Jinja2Templates
import requests
from models.judge_game import JudgeGameAnswer
from models.pending_game import EndPendingGame
from config.constants import API_BASE_URL
from typing import *
from urllib.parse import urljoin

def send_pending_verdict(game_id: int, request: Request, payload: JudgeGameAnswer, templates: Jinja2Templates):
    try:
        response = requests.post(
            urljoin(API_BASE_URL, f"/end-pending-game-api/{game_id}"),
            json=payload.model_dump()
        )
        response.raise_for_status()
        result = EndPendingGame.model_validate(response.json())

    except requests.RequestException as e:
        status_code = 500
        detail = "Errore sconosciuto"

        if e.response is not None:
            status_code = e.response.status_code
            try:
                error_data = e.response.json()
                detail = error_data.get("detail", detail)
            except Exception:
                detail = e.response.text or detail

            if status_code == 404:
                return templates.TemplateResponse("game_not_found.html", {"request": request})

        raise HTTPException(status_code=status_code, detail=detail)

    return result