from fastapi import Request, HTTPException
from fastapi.templating import Jinja2Templates
import requests
from models.participant_game import AnswerInput, ResponseSubmit
from config.constants import API_BASE_URL
from urllib.parse import urljoin

def send_answers_participant_game(game_id: int, request: Request, answer1: str, answer2: str, answer3: str, templates: Jinja2Templates):
    try:
        payload = AnswerInput(answers=[answer1, answer2, answer3])
        response = requests.post(urljoin(API_BASE_URL, f"/submit-participant-answers-api/{game_id}"), json=payload.model_dump())
        response.raise_for_status()
        response_submit = ResponseSubmit.model_validate(response.json())
    except requests.RequestException as e:
        try:
            error_detail = e.response.json().get("detail", str(e))
        except Exception:
            error_detail = str(e)

        if e.response and e.response.status_code == 404:
            return templates.TemplateResponse("game_not_found.html", {"request": request})

        raise HTTPException(status_code=500, detail=f"Errore durante il recupero: {error_detail}")
    
    return response_submit