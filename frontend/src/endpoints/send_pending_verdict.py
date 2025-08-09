from typing import Dict
from fastapi import Request, HTTPException
from fastapi.templating import Jinja2Templates
import requests
from urllib.parse import urljoin
from models.judge_game import JudgeGameAnswer
from models.pending_game import EndPendingGame
from config.constants import API_BASE_URL

def send_pending_verdict(game_id: int, request: Request, payload: JudgeGameAnswer, templates: Jinja2Templates) -> EndPendingGame:
    """
    Invia il verdetto del giudice per una partita in modalità 'pending' al backend.

    Args:
        game_id (int): Identificativo univoco della partita da concludere.
        request (Request): Oggetto di richiesta HTTP di FastAPI, necessario per il rendering dei template.
        payload (JudgeGameAnswer): Oggetto contenente il verdetto del giudice (AI o umano).
        templates (Jinja2Templates): Istanza per il rendering di template HTML.

    Returns:
        EndPendingGame: Oggetto con l'esito della partita (vittoria/sconfitta, messaggio e punti).

    Raises:
        HTTPException: Se si verificano errori di comunicazione o di validazione della risposta.
    """
    try:
        response = requests.post(
            urljoin(API_BASE_URL, f"/end-pending-game-api/{game_id}"),
            json=payload.model_dump()
        )
        response.raise_for_status()
        result = EndPendingGame.model_validate(response.json())

    except requests.RequestException as e:
        status_code: int = 500
        detail: str = "Errore sconosciuto"

        if e.response is not None:
            status_code = e.response.status_code
            try:
                error_data: Dict = e.response.json()
                detail = error_data.get("detail", detail)
            except Exception:
                detail = e.response.text or detail

            if status_code == 404:
                return templates.TemplateResponse("game_not_found.html", {"request": request})

        raise HTTPException(status_code=status_code, detail=detail)

    return result