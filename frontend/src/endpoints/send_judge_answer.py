from fastapi import Request, HTTPException
import requests
from models.judge_game import JudgeGameAnswer, EndJudgeGameOutput
from config.constants import API_BASE_URL
from typing import Dict
from urllib.parse import urljoin

def send_judge_answer(game_id: int, payload: JudgeGameAnswer) -> EndJudgeGameOutput:
    """
    Invia la risposta del giudice all'API per terminare la partita.

    Questa funzione comunica con l'endpoint '/end-judge-game-api/{game_id}' inviando
    la risposta del giudice (se ha individuato correttamente l'intelligenza artificiale).
    Gestisce eventuali errori di comunicazione con il backend e restituisce l'esito
    della partita, comprensivo di messaggio, esito e punteggio assegnato.

    Args:
        game_id (int): Identificativo univoco della partita da terminare.
        payload (JudgeGameAnswer): Oggetto contenente la risposta del giudice.

    Returns:
        EndJudgeGameOutput: Oggetto con il messaggio, l'esito e i punti guadagnati.

    Raises:
        HTTPException: 
            - 404 se partita, giudice o partecipante non trovati.
            - 403 se partita già terminata.
            - 500 in caso di errori di rete o errori non gestiti.
    """
    try:
        response = requests.post(
            urljoin(API_BASE_URL, f"/end-judge-game-api/{game_id}"),
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

    return EndJudgeGameOutput.model_validate(response.json())