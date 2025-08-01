import asyncio
import random
from fastapi import HTTPException
import requests
from models.player_info import PlayerInfo
from models.confirm_game import ConfirmGame
from config.constants import API_BASE_URL
from urllib.parse import urljoin

async def start_pending_game(payload: PlayerInfo):
    payload.player_role = "judge"
    
    try:
        response = requests.post(urljoin(API_BASE_URL, "/start-pending-game-api"), json= payload.model_dump())
        response.raise_for_status()
        confirm_game = ConfirmGame.model_validate(response.json())
    
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

        raise HTTPException(status_code=status_code, detail=detail)
    
    # Attendi un tempo randomico tra 0 e 30s
    await asyncio.sleep(random.randint(0, 30))
    
    return confirm_game