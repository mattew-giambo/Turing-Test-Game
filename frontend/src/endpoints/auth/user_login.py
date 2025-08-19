from fastapi import Request, HTTPException
import requests
from typing import Dict
from datetime import datetime
from urllib.parse import urljoin

from models.authentication import UserLogin, LoginResponse
from utility.auth.generate_random_string import generate_random_string
from config.constants import API_BASE_URL

def user_login(user: UserLogin, request: Request, sessioni_attive: Dict[int, Dict[str, str]]) -> LoginResponse:
    """
    Autentica un utente esternamente tramite API e aggiorna la mappa delle sessioni attive.

    Invia i dati di login (username e password) all’endpoint interno '/login-api'.
    In caso di autenticazione avvenuta con successo, genera un token casuale e
    registra una nuova sessione utente nella struttura in memoria `sessioni_attive`.

    Args:
        user (UserLogin): Oggetto contenente username e password inseriti dall’utente.
        request (Request): Oggetto FastAPI che rappresenta la richiesta HTTP corrente.
        sessioni_attive (Dict[int, Dict[str, str]]): Mappa globale delle sessioni utente attive,
            indicizzata per ID utente.

    Returns:
        LoginResponse: Oggetto contenente l’ID utente, nome utente, email e token di sessione.

    Raises:
        HTTPException:
            - 404 se lo username non esiste nel sistema.
            - 401 se la password è errata o non verificabile.
            - 500 in caso di errori di rete o errori non gestiti.
    """
    try:
        response = requests.post(
            urljoin(API_BASE_URL, "/login-api"),
            json=user.model_dump()
        )
        response.raise_for_status()
    except requests.RequestException as e:
        status_code: int = 500
        detail: str = "Errore sconosciuto durante il login"

        if e.response is not None:
            status_code = e.response.status_code
            try:
                error_data: Dict = e.response.json()
                detail = error_data.get("detail", detail)
            except ValueError:
                # Il corpo della risposta non è un JSON valido
                detail = e.response.text

        raise HTTPException(status_code=status_code, detail=detail)
    
    response_data: Dict = response.json()
    user_id: int = response_data.get("user_id")
    user_name: str = response_data.get("user_name")
    email: str = response_data.get("email")

    token: str = generate_random_string(10)

    sessioni_attive[user_id] = {
        "user_name": user_name,
        "email": email,
        "timestamp": datetime.now(),
        "token": token
    }

    return LoginResponse(
        user_id=user_id,
        user_name=user_name,
        email=email,
        token=token
    )