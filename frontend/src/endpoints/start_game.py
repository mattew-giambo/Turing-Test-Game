from fastapi import HTTPException
from urllib.parse import urljoin
from typing import Dict
import requests

from models.player_info import PlayerInfo
from models.confirm_game import ConfirmGame
from config.constants import API_BASE_URL

def start_game(payload: PlayerInfo):
    try:
        response = requests.post(urljoin(API_BASE_URL, "/start-game-api"), json=payload.model_dump())
        response.raise_for_status()
    except requests.RequestException as e:
        status_code = 500
        detail = "Errore sconosciuto"

        if e.response is not None:
            status_code = e.response.status_code
            try:
                error_data: Dict = e.response.json()
                detail = error_data.get("detail", detail)
            except ValueError:
                # Il body non è in formato JSON
                detail = e.response.text

        raise HTTPException(
            status_code=status_code,
            detail=detail
        )

    return ConfirmGame.model_validate(response.json())