from fastapi import Request, HTTPException
import requests
from models.player_info import PlayerInfo
from models.confirm_game import ConfirmGame
from config.constants import API_BASE_URL
from urllib.parse import urljoin

def start_pending_game(player_id: int, request: Request):
    payload = PlayerInfo(player_id=player_id, player_role="judge")
    try:
        response = requests.post(urljoin(API_BASE_URL, "/start-pending-game-api"), json= payload.model_dump())
        response.raise_for_status()
        confirm_game = ConfirmGame.model_validate(response.json())
    except requests.RequestException as e:
        status_code = e.response.status_code if e.response else 500
        try:
            detail = e.response.json().get("detail", str(e))
        except Exception:
            detail = str(e)

        raise HTTPException(status_code=status_code, detail=detail)
    
    return confirm_game