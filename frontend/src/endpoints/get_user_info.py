from fastapi import Request, HTTPException
from fastapi.templating import Jinja2Templates
import requests
from models.user_info import UserInfo
from config.constants import API_BASE_URL
from typing import Dict
from urllib.parse import urljoin

def get_user_info(user_id: int, request: Request):
    try:
        response = requests.get(urljoin(API_BASE_URL, f"/user-info-api/{user_id}"))
        response.raise_for_status()
    except requests.RequestException as e:
        error_data: Dict = e.response.json()
        raise HTTPException(
            status_code= error_data.get("status_code", 500),
            detail= error_data.get("detail", "Errore sconosciuto")
        )
    
    return UserInfo.model_validate(response.json())