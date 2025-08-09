import asyncio
import random
from typing import Dict
from urllib.parse import urljoin

import requests
from fastapi import HTTPException
from config.constants import API_BASE_URL
from models.player_info import PlayerInfo
from models.confirm_game import ConfirmGame

async def start_pending_game(payload: PlayerInfo) -> ConfirmGame:
    """
    Funzione asincrona che avvia una partita in modalità 'pending' come giudice.
    Invia i dati del giocatore a un endpoint interno del backend per creare una nuova sessione di gioco,
    attende un tempo casuale tra 0 e 30 secondi per simulare il ritardo prima dell'avvio
    e restituisce i dettagli della partita creata.

    Args:
        payload (PlayerInfo): Modello contenente le informazioni del giocatore che avvia la partita.

    Returns:
        ConfirmGame: Dettagli della partita creata, inclusi game_id, player_id, player_name e player_role.

    Raises:
        HTTPException:
            - 4xx o 5xx in caso di errore durante la comunicazione con l'endpoint interno.
    """
    payload.player_role = "judge"
    
    try:
        response = requests.post(
            urljoin(API_BASE_URL, "/start-pending-game-api"),
            json=payload.model_dump()
        )
        response.raise_for_status()

        confirm_game = ConfirmGame.model_validate(response.json())
    
    except requests.RequestException as e:
        status_code: int = 500
        detail: str = "Errore sconosciuto nella comunicazione con il backend"

        if e.response is not None:
            status_code = e.response.status_code
            try:
                error_data: Dict = e.response.json()
                detail = error_data.get("detail", detail)
            except Exception:
                detail = e.response.text or detail

        raise HTTPException(status_code=status_code, detail=detail)
    
    # Attende un intervallo casuale tra 0 e 30 secondi per simulare il tempo di preparazione
    await asyncio.sleep(random.randint(0, 30))
    
    return confirm_game