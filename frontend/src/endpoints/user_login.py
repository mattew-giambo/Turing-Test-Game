from fastapi import Request, HTTPException
import requests
from models.authentication import UserLogin, LoginResponse
from typing import Dict
from datetime import datetime
from utility.generate_random_string import generate_random_string

def user_login(user: UserLogin, request: Request, sessioni_attive: Dict[int, Dict[str, str]]) -> LoginResponse:
    try:
        response = requests.post("/login-api", json= user.model_dump())
        response.raise_for_status()
    except requests.RequestException as e:
        error_data: Dict =  e.response.json()
        raise HTTPException(
            status_code= error_data.get("status_code", 500),
            detail= error_data.get("detail", "Errore del server")
        )
    token = generate_random_string(10)
    response_data = LoginResponse.model_validate(response.json())
    sessioni_attive[response_data.user_id] = {
            "user_name": response_data.user_name,
            "email": response_data.email,
            "timestamp": datetime.now(),
            "token": token
        }
    
    return LoginResponse(
        user_id= response_data.user_id,
        user_name= response_data.user_name,
        email= response_data.email,
        token= token
    )