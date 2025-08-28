from fastapi import Request, HTTPException
from fastapi.templating import Jinja2Templates
from typing import Dict
import requests

from models.user_stats import UserStats
from models.user_games import UserGames
from models.user_info import UserInfo
from utility.user.get_user_stats import get_user_stats
from utility.user.get_user_info import get_user_info
from utility.user.get_user_games import get_user_games
from utility.auth.verify_user_token import verify_user_token

def get_profilo(user_id: int, token: str, request: Request, templates: Jinja2Templates, sessioni_attive: Dict[int, Dict[str, str]]):
    """
    Recupera e rende la pagina profilo dell'utente autenticato.

    La funzione verifica la validità del token utente e, in caso positivo,
    effettua chiamate ai servizi interni per ottenere informazioni anagrafiche,
    statistiche di gioco e storico delle partite dell'utente.

    Vengono calcolate le percentuali di vittorie nelle modalità giudice e partecipante,
    e tutti i dati vengono passati al template HTML per il rendering della pagina profilo.

    Args:
        user_id (int): Identificativo univoco dell'utente.
        token (str): Token di sessione dell'utente da verificare.
        request (Request): Oggetto request per il rendering del template.
        templates (Jinja2Templates): Gestore dei template per FastAPI.
        sessioni_attive (Dict[int, Dict[str, str]]): Dizionario delle sessioni attive per la verifica token.

    Returns:
        TemplateResponse: Pagina HTML del profilo utente con dati popolati.
        HTTPException: In caso di errore nella verifica token o nei servizi di backend.

    Raises:
        HTTPException: 
            - 404 se l'utente non viene trovato.
            - 500 in caso di errori generici di comunicazione con i servizi.
    """
    if not verify_user_token(user_id, token, sessioni_attive):
        return templates.TemplateResponse("login.html", {"request": request})
    
    try:
        user_info: UserInfo = get_user_info(user_id)
        user_stats: UserStats = get_user_stats(user_id)
        user_games: UserGames = get_user_games(user_id)
    
    except requests.RequestException as e:
        status_code: int = 500
        detail: str = "Errore sconosciuto durante il recupero dati utente."

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

    perc_won_judge = round(user_stats.won_judge / user_stats.n_games_judge, 2) * 100 if user_stats.n_games_judge > 0 else 0
    perc_won_part = round(user_stats.won_part / user_stats.n_games_part, 2) * 100 if user_stats.n_games_part > 0 else 0

    return templates.TemplateResponse(
        "profilo.html",
        {
            "user_id": user_id,
            "username": user_info.user_name,
            "email": user_info.email,
            "n_games": user_stats.n_games,
            "n_games_judge": user_stats.n_games_judge,
            "n_games_part": user_stats.n_games_part,
            "score_part": user_stats.score_part,
            "score_judge": user_stats.score_judge,
            "won_part": user_stats.won_part,
            "won_judge": user_stats.won_judge,
            "lost_part": user_stats.lost_part,
            "lost_judge": user_stats.lost_judge,
            "user_games": user_games.user_games,
            "perc_won_judge": perc_won_judge,
            "perc_won_part": perc_won_part,
            "request": request
        }
    )