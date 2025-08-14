from fastapi import Request, HTTPException
import requests
from typing import Dict
from urllib.parse import urljoin

from models.authentication import UserRegister, RegisterResponse
from config.constants import API_BASE_URL

def user_register(user: UserRegister, request: Request) -> RegisterResponse:
    """
    Invia i dati di registrazione dell’utente all’endpoint interno `/register-api`
    e restituisce l’identificativo del nuovo utente registrato.

    Args:
        user (UserRegister): Oggetto contenente nome utente, email e password in chiaro.
        request (Request): Oggetto FastAPI della richiesta corrente.

    Returns:
        RegisterResponse: Oggetto contenente l'ID dell'utente appena registrato.

    Raises:
        HTTPException:
            - 400 se l’utente è già registrato.
            - 500 in caso di errori di rete o errori non gestiti.
    """
    try:
        response = requests.post(
            urljoin(API_BASE_URL, "/register-api"),
            json=user.model_dump()
        )
        response.raise_for_status()
    except requests.RequestException as e:
        status_code: int = 500
        detail: str = "Errore sconosciuto durante la registrazione"

        if e.response is not None:
            status_code = e.response.status_code
            try:
                error_data: Dict = e.response.json()
                detail = error_data.get("detail", detail)
            except ValueError:
                # Il corpo della risposta non è JSON valido
                detail = e.response.text

        raise HTTPException(status_code=status_code, detail=detail)
    
    response_data = RegisterResponse.model_validate(response.json())
    return response_data