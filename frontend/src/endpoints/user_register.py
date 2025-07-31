from fastapi import Request, HTTPException
import requests
from models.authentication import UserRegister, RegisterResponse
from typing import Dict
from config.constants import API_BASE_URL
from urllib.parse import urljoin

def user_register(user: UserRegister, request: Request) -> RegisterResponse:
    try:
        response = requests.post(urljoin(API_BASE_URL, "/register-api"), json= user.model_dump())
        response.raise_for_status()
    except requests.RequestException as e:
        status_code = 500
        detail = "Errore sconosciuto"

        if e.response is not None:
            status_code = e.response.status_code
            try:
                error_data: Dict = e.response.json()
                detail = error_data.get("detail", detail)
            except ValueError:
                # Il body non è in formato JSON
                detail = e.response.text

        raise HTTPException(
            status_code=status_code,
            detail=detail
        )
    
    response_data = RegisterResponse.model_validate(response.json())
    return response_data