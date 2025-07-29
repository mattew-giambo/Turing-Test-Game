from fastapi import HTTPException
import requests
from models.player_info import PlayerInfo
from models.confirm_game import ConfirmGame
from config.constants import API_BASE_URL
from urllib.parse import urljoin

def start_pending_game(player_id: int):
    payload = PlayerInfo(player_id=player_id, player_role="judge")
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
    
    return confirm_game