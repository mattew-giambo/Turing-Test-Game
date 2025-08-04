from fastapi import Request, HTTPException
import requests
from models.authentication import UserLogin, LoginResponse
from typing import Dict
from datetime import datetime
from utility.generate_random_string import generate_random_string
from config.constants import API_BASE_URL
from urllib.parse import urljoin

def user_login(user: UserLogin, request: Request, sessioni_attive: Dict[int, Dict[str, str]]) -> LoginResponse:
    try:
        response = requests.post(urljoin(API_BASE_URL, "/login-api"), json= user.model_dump())
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
        print(status_code, detail)
        raise HTTPException(
            status_code=status_code,
            detail=detail
        )
    
    token = generate_random_string(10)

    response_data: Dict = response.json()
    sessioni_attive[response_data.get("user_id")] = {
            "user_name": response_data.get("user_name"),
            "email": response_data.get("email"),
            "timestamp": datetime.now(),
            "token": token
        }
    
    return LoginResponse(
        user_id= response_data.get("user_id"),
        user_name= response_data.get("user_name"),
        email= response_data.get("email"),
        token= token
    )