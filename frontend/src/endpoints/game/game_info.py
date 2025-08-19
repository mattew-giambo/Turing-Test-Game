from typing import Dict
from models.game_info import GameInfoInput, GameInfoOutput
import requests
from fastapi import HTTPException
from config.constants import API_BASE_URL
from urllib.parse import urljoin

def game_info(payload: GameInfoInput) -> GameInfoOutput:
    """
    Effettua una richiesta POST a un endpoint interno del backend per ottenere informazioni
    dettagliate su una partita specifica, dato il player_id e game_id.

    La funzione si occupa di inviare i dati serializzati, gestire eventuali errori di comunicazione
    o di risposta non valida, e di validare i dati ricevuti nel modello di output.

    Args:
        payload (GameInfoInput): Modello Pydantic contenente player_id e game_id della partita richiesta.

    Returns:
        GameInfoOutput: Modello Pydantic con le informazioni dettagliate della partita,
        inclusi stato, ruolo del giocatore e risultato.

    Raises:
        HTTPException:
            - 404 se la partita non esiste o non è associata al giocatore.
            - 500 in caso di errori di rete o errori non gestiti.
    """
    try:
        response = requests.post(
            urljoin(API_BASE_URL, "/game-info-api"),
            json=payload.model_dump()
        )
        response.raise_for_status()
    except requests.RequestException as e:
        status_code: int = 500
        detail: str = "Errore sconosciuto"

        if e.response is not None:
            status_code = e.response.status_code
            try:
                error_data: Dict = e.response.json()
                detail = error_data.get("detail", detail)
            except ValueError:
                # Il corpo della risposta non è JSON
                detail = e.response.text or detail

        raise HTTPException(
            status_code=status_code,
            detail=detail
        )
    
    return GameInfoOutput.model_validate(response.json())