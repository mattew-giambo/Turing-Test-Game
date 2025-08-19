from typing import Dict
from urllib.parse import urljoin
import requests
from fastapi import HTTPException
from models.participant_game import AnswerInput, ResponseSubmit
from config.constants import API_BASE_URL

def send_answers_participant_game(game_id: int, payload: AnswerInput) -> ResponseSubmit:
    """
    Invia le risposte del partecipante alla sessione di gioco al servizio API backend.

    Args:
        game_id (int): Identificativo univoco della sessione di gioco a cui si riferiscono le risposte.
        payload (AnswerInput): Oggetto contenente l'elenco delle risposte del partecipante.

    Returns:
        ResponseSubmit: Oggetto che rappresenta l'esito dell'operazione di invio risposte.

    Raises:
        HTTPException: 
            - 404 se partita, giudice o partecipante non trovati.
            - 403 se partita già terminata.
            - 500 in caso di errori di rete o errori non gestiti.
    """
    try:
        response = requests.post(
            urljoin(API_BASE_URL, f"/submit-participant-answers-api/{game_id}"),
            json=payload.model_dump()
        )
        response.raise_for_status()
        response_submit = ResponseSubmit.model_validate(response.json())
    
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

    return response_submit