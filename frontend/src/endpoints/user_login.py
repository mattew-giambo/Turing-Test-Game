from fastapi import Request, HTTPException
import requests
from models.authentication import UserLogin, LoginResponse
from typing import Dict
from datetime import datetime

def user_login(email: str, password: str, request: Request, sessioni_attive: Dict[int, Dict[str, str]]) -> LoginResponse:
    user_cred = UserLogin(email= email, password= password)
    try:
        response = requests.post("/login-api", json= user_cred.model_dump())
        response.raise_for_status()
    except requests.RequestException as e:
        error_data: Dict =  e.response.json()
        raise HTTPException(
            status_code= error_data.get("status_code", 500),
            detail= error_data.get("detail", "Errore del server")
        )
    
    response_data = LoginResponse.model_validate(response.json())
    sessioni_attive[response_data.user_id] = {
            "user_name": response_data.user_name,
            "email": email,
            "timestamp": datetime.now()
        }
    
    return response_data