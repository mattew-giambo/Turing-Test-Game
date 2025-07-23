from fastapi import Request, HTTPException
from fastapi.templating import Jinja2Templates
import os
import requests
from models.game_info import GameInfoInput, GameInfoOutput
from models.pending_game import GameReviewOutput
from config.constants import API_BASE_URL
from typing import Dict

def get_verdict_game(game_id: int, player_id: int, request: Request, templates: Jinja2Templates, sessioni_attive: Dict[int, Dict[str, str]]):
    if player_id not in sessioni_attive.keys():
        return templates.TemplateResponse(
            "login.html", {"request": request}
        )
    # 1 Ottiene info sulla partita
    try:
        payload = GameInfoInput(player_id=player_id, game_id=game_id)
        response = requests.post(os.path.join(API_BASE_URL, "/game-info-api"), json=payload.model_dump())
        response.raise_for_status()
        game_info = GameInfoOutput.model_validate(response.json())
    except requests.RequestException as e:
        try:
            error_data = e.response.json() if e.response else {}
        except Exception:
            error_data = {}

        if e.response and e.response.status_code == 404:
            return templates.TemplateResponse("404.html", {"request": request})

        raise HTTPException(
            status_code=error_data.get("status_code", 500),
            detail=error_data.get("detail", "Errore sconosciuto")
        )

    # 2 Blocca se partita terminata o se è il participant
    if game_info.terminated or game_info.player_role == "participant":
        return templates.TemplateResponse("partita_terminata.html", {"request": request})

    # 3 Ottiene la sessione da "/pending-game-session/{game_id}"
    try:
        response = requests.get(os.path.join(API_BASE_URL, f"/pending-game-session/{game_id}"))
        response.raise_for_status()
        game_data = GameReviewOutput.model_validate(response.json())
    except requests.RequestException as e:
        try:
            error_detail = e.response.json().get("detail", str(e))
        except Exception:
            error_detail = str(e)

        if e.response and e.response.status_code == 404:
            return templates.TemplateResponse("game_not_found.html", {"request": request})

        raise HTTPException(status_code=500, detail=f"Errore durante il recupero: {error_detail}")
    
    # 4 Renderizza il template con la sessione
    return templates.TemplateResponse(
        "verdict_game.html",
        {
            "request": request,
            "game_id": game_info.game_id,
            "player_id": game_info.player_id,
            "data": game_info.data,
            "session": game_data.session
        }
    )