from typing import Dict
from fastapi import HTTPException
import requests
from models.participant_game import AnswerInput, ResponseSubmit
from config.constants import API_BASE_URL
from urllib.parse import urljoin

def send_answers_participant_game(game_id: int, payload: AnswerInput):
    try:
        response = requests.post(
            urljoin(API_BASE_URL, f"/submit-participant-answers-api/{game_id}"),
            json=payload.model_dump()
        )
        response.raise_for_status()
        response_submit = ResponseSubmit.model_validate(response.json())
    
    except requests.RequestException as e:
        status_code = 500
        detail = "Errore sconosciuto"

        if e.response is not None:
            status_code = e.response.status_code
            try:
                error_data: Dict = e.response.json()
                detail = error_data.get("detail", detail)
            except Exception:
                detail = e.response.text or detail

        raise HTTPException(status_code=status_code, detail=detail)

    return response_submit