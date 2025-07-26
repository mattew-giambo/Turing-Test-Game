from fastapi import Request, HTTPException
import requests
from models.authentication import UserRegister, RegisterResponse
from typing import Dict

def user_register(user_name: str, email: str, password: str, request: Request) -> RegisterResponse:
    user_cred = UserRegister(user_name= user_name, email= email, password= password)
    try:
        response = requests.post("/register-api", json= user_cred.model_dump())
        response.raise_for_status()
    except requests.RequestException as e:
        error_data: Dict =  e.response.json()
        raise HTTPException(
            status_code= error_data.get("status_code", 500),
            detail= error_data.get("detail", "Errore del server")
        )
    
    response_data = RegisterResponse.model_validate(response.json())
    return response_data