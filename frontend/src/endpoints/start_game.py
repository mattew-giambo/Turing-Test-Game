from fastapi import Request, HTTPException
import requests
from models.player_info import PlayerInfo
from models.confirm_game import ConfirmGame
from config.constants import API_BASE_URL
from typing import Dict
from urllib.parse import urljoin

def start_game(payload: PlayerInfo, request: Request):
    try:
        response = requests.post(urljoin(API_BASE_URL, "/start-game-api"), json= payload.model_dump())
        response.raise_for_status()
    except requests.RequestException as e:
        error_data: Dict =  e.response.json()
        raise HTTPException(
            status_code= error_data.get("status_code", 500),
            detail= error_data.get("detail", "Errore sconosciuto")
        )
    return ConfirmGame.model_validate(response.json())