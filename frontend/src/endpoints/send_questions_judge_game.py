from fastapi import FastAPI, HTTPException
from typing import Dict
from urllib.parse import urljoin
import requests
import asyncio
import random

from models.judge_game import JudgeGameInput, JudgeGameOutput
from config.constants import API_BASE_URL

async def send_questions_judge_game(game_id: int, payload: JudgeGameInput) -> JudgeGameOutput:
    """
    Funzione asincrona che inoltra una lista di domande generate dal giudice a un endpoint interno del backend.
    Dopo l'invio, attende un tempo casuale tra 0 e 30 secondi per simulare il ritardo nelle risposte,
    quindi restituisce la lista delle risposte (generate o recuperate).

    Args:
        game_id (int): Identificativo della partita in corso.
        payload (JudgeGameInput): Modello contenente la lista di domande del giudice.

    Returns:
        JudgeGameOutput: Lista delle risposte associate alle domande fornite.
    
    Raises:
    HTTPException:
        - 4xx o 5xx in caso di errore durante la comunicazione con il backend.
    """
    try:
        response = requests.post(
            urljoin(API_BASE_URL, f"/judge-game-api/{game_id}"),
            json=payload.model_dump()
        )
        response.raise_for_status()

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

    # Simula un ritardo tra 0 e 30 secondi per imitare il tempo di risposta AI o umana
    await asyncio.sleep(random.randint(0, 30))

    return JudgeGameOutput.model_validate(response.json())