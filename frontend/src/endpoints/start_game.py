from fastapi import HTTPException
from urllib.parse import urljoin
from typing import Dict
import requests

from models.player_info import PlayerInfo
from models.confirm_game import ConfirmGame
from config.constants import API_BASE_URL

def start_game(payload: PlayerInfo) -> ConfirmGame:
    """
    Invia i dati del giocatore all’endpoint '/start-game-api' per avviare una nuova partita.

    Args:
        payload (PlayerInfo): Oggetto contenente l’ID del giocatore e il suo ruolo ('judge' o 'participant').

    Returns:
        ConfirmGame: Oggetto contenente i dati della partita avviata.

    Raises:
        HTTPException:
            - 4xx in caso di errori lato client (es. utente non trovato).
            - 5xx in caso di errori lato server o problemi di rete.
    """
    try:
        response = requests.post(
            urljoin(API_BASE_URL, "/start-game-api"),
            json=payload.model_dump()
        )
        response.raise_for_status()
    except requests.RequestException as e:
        status_code: int = 500
        detail: str = "Errore sconosciuto durante la creazione della partita"

        if e.response is not None:
            status_code = e.response.status_code
            try:
                error_data: Dict = e.response.json()
                detail = error_data.get("detail", detail)
            except ValueError:
                detail = e.response.text

        raise HTTPException(status_code=status_code, detail=detail)

    return ConfirmGame.model_validate(response.json())