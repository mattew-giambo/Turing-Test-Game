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
        error_data: Dict =  e.response.json()
        raise HTTPException(
            status_code= error_data.get("status_code", 500),
            detail= error_data.get("detail", "Errore del server")
        )
    
    response_data = RegisterResponse.model_validate(response.json())
    return response_data