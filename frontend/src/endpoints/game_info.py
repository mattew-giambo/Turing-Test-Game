from typing import Dict
from models.game_info import GameInfoInput, GameInfoOutput
import requests
from fastapi import HTTPException
from config.constants import API_BASE_URL
from urllib.parse import urljoin

def game_info(payload: GameInfoInput):
    try:
        response = requests.post(urljoin(API_BASE_URL, "/game-info-api"), json= payload.model_dump())
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
    
    return GameInfoOutput.model_validate(response.json())