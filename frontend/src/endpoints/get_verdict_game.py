from fastapi import Request, HTTPException
from fastapi.templating import Jinja2Templates
import requests
from urllib.parse import urljoin
from models.game_info import GameInfoInput, GameInfoOutput
from models.pending_game import GameReviewOutput
from config.constants import API_BASE_URL
from typing import Dict
from utility.verify_user_token import verify_user_token

def get_verdict_game(game_id: int, player_id: int, player_token: str, request: Request, templates: Jinja2Templates, sessioni_attive: Dict[int, Dict[str, str]]):
    """
    Recupera e visualizza la schermata del verdetto di una partita in corso o terminata.
    Verifica innanzitutto l'autenticità del token del giocatore; se non valido, reindirizza alla pagina di login.
    In caso di partita terminata o giocatore con ruolo 'participant', mostra la pagina di partita terminata.
    Altrimenti, carica i dati completi della sessione pending per consentire al giudice di esprimere il verdetto.

    Args:
        game_id (int): Identificativo univoco della partita.
        player_id (int): Identificativo univoco del giocatore.
        player_token (str): Token di autenticazione del giocatore.
        request (Request): Oggetto Request di FastAPI per la gestione delle richieste HTTP.
        templates (Jinja2Templates): Istanza di Jinja2Templates per il rendering dei template HTML.
        sessioni_attive (Dict[int, Dict[str, str]]): Dizionario contenente le sessioni utente attive.

    Returns:
        TemplateResponse: Pagina HTML generata in base allo stato della partita e al ruolo del giocatore.

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


    if game_info.is_terminated or game_info.player_role == "participant":
        return templates.TemplateResponse("partita_terminata.html", {"request": request})

    try:
        response = requests.get(
            urljoin(API_BASE_URL, f"/pending-game-session/{game_id}")
        )
        response.raise_for_status()
        game_data = GameReviewOutput.model_validate(response.json())

    except requests.RequestException as e:
        status_code: int = 500
        detail: str = "Errore durante il recupero"

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
    
    return templates.TemplateResponse(
        "verdict_game.html",
        {
            "request": request,
            "game_id": game_info.game_id,
            "player_id": game_info.player_id,
            "data": game_info.data,
            "session": game_data.session
        }
    )