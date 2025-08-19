from fastapi import Request, HTTPException
from fastapi.templating import Jinja2Templates
from urllib.parse import urljoin
from typing import Dict
import requests

from models.game_info import GameInfoInput, GameInfoOutput
from config.constants import API_BASE_URL
from utility.auth.verify_user_token import verify_user_token

def get_judge_game(game_id: int, player_id: int, player_token: str, request: Request, templates: Jinja2Templates, sessioni_attive: Dict[int, Dict[str, str]]):
    """
    Visualizza la schermata di gioco del giudice per una partita attiva.

    Verifica il token utente e, se valido, effettua una richiesta all’API interna
    per recuperare i dati della partita. In base allo stato della partita,
    restituisce il template HTML appropriato (gioco attivo, partita terminata o 404).

    Args:
        game_id (int): Identificativo della partita da visualizzare.
        player_id (int): ID del giocatore che accede come giudice.
        player_token (str): Token di autenticazione del giocatore.
        request (Request): Oggetto FastAPI della richiesta HTTP corrente.
        templates (Jinja2Templates): Motore di rendering dei template Jinja2.
        sessioni_attive (Dict[int, Dict[str, str]]): Mappa globale delle sessioni attive.

    Returns:
        TemplateResponse: Pagina HTML renderizzata per il giudice.

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

    except requests.RequestException as e:
        status_code: int = 500
        detail: str = "Errore sconosciuto durante il recupero della partita"

        if e.response is not None:
            status_code = e.response.status_code
            try:
                error_data = e.response.json()
                detail = error_data.get("detail", detail)
            except Exception:
                detail = e.response.text or detail

            if status_code == 404:
                return templates.TemplateResponse("404.html", {"request": request})

        raise HTTPException(status_code=status_code, detail=detail)

    response_data: GameInfoOutput = GameInfoOutput.model_validate(response.json())

    if response_data.is_terminated:
        return templates.TemplateResponse("partita_terminata.html", {"request": request})

    return templates.TemplateResponse(
        "judge_game.html", {
            "request": request,
            "game_id": response_data.game_id,
            "data": response_data.data,
            "player_id": response_data.player_id
        }
    )