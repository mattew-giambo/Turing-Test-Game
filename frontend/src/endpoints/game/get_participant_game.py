from fastapi import Request, HTTPException
from fastapi.templating import Jinja2Templates
import requests
from typing import Dict
from urllib.parse import urljoin

from models.game_info import GameInfoInput, GameInfoOutput
from models.participant_game import ParticipantGameOutput
from config.constants import API_BASE_URL
from utility.auth.verify_user_token import verify_user_token

def get_participant_game(game_id: int, player_id: int, player_token: str, request: Request, templates: Jinja2Templates, sessioni_attive: Dict[int, Dict[str, str]]):
    """
    Recupera i dati di gioco per un partecipante e visualizza la schermata della partita.

    L'endpoint verifica il token del giocatore, ottiene le informazioni generali della partita 
    dal backend centrale, e se la partita è ancora in corso e il giocatore è un partecipante,
    carica le domande disponibili.

    Args:
        game_id (int): ID univoco della partita.
        player_id (int): ID univoco del giocatore.
        player_token (str): Token di autenticazione del giocatore.
        request (Request): Oggetto FastAPI contenente le informazioni della richiesta.
        templates (Jinja2Templates): Motore di template per renderizzare le pagine HTML.
        sessioni_attive (Dict[int, Dict[str, str]]): Mappa contenente le sessioni utente attive.

    Returns:
        TemplateResponse: Pagina HTML con i dati della partita, oppure pagina di errore/login.
    
    Raises:
        HTTPException: 
            - 404 se la partita non esiste o non è associata al giocatore.
            - 500 in caso di errori di rete o errori non gestiti.
    """
    if not verify_user_token(player_id, player_token, sessioni_attive):
        return templates.TemplateResponse("login.html", {"request": request})
    
    try:
        payload = GameInfoInput(player_id=player_id, game_id=game_id)
        response = requests.post(
            urljoin(API_BASE_URL, "/game-info-api"),
            json=payload.model_dump()
        )
        response.raise_for_status()
        game_info = GameInfoOutput.model_validate(response.json())
        
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
                return templates.TemplateResponse("404.html", {"request": request})

        raise HTTPException(status_code=status_code, detail=detail)

    if game_info.is_terminated or game_info.player_role == "judge":
        return templates.TemplateResponse("partita_terminata.html", {"request": request})

    try:
        response = requests.post(
            urljoin(API_BASE_URL, f"/participant-game-api/{game_id}")
        )
        response.raise_for_status()
        game_data = ParticipantGameOutput.model_validate(response.json())

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

        raise HTTPException(status_code=status_code, detail=detail )
    
    return templates.TemplateResponse(
        "participant_game.html",
        {
            "request": request,
            "game_id": game_info.game_id,
            "player_id": game_info.player_id,
            "data": game_info.data,
            "questions": game_data.questions
        }
    )